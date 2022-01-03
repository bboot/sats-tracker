from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import (
        DetailView,
        ListView,
        CreateView,
        UpdateView,
        DeleteView,
    )
import json
from pprint import PrettyPrinter
import traceback

from .models import TxOut, Actor
from node.explorer import Explorer

# Create your views here.
class TxOutDetailView(DetailView):
    model = TxOut
    template_name = "txout_detail.html"


class TxOutListView(ListView):
    model = TxOut
    template_name = "txout_list.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        '''
        Normally I would like to do this:
            qs = qs.order_by("height")
        But alas, the data is encrypted so these kinds of operations
        have to be done using custom code.
        '''
        qs = super().get_queryset(*args, **kwargs)
        return sorted(qs, key=lambda x: x.height)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actors'] = ActorListView().get_queryset()
        return context

    def one_time_migration_001(self):
        for item in TxOut.objects.values():
            item['encrypted_address'] = item['address']
            item['encrypted_transaction'] = item['transaction']
            item['encrypted_notes'] = item['notes']
            item['encrypted_amount'] = item['amount']
            item['encrypted_height'] = item['height']
            item['encrypted_spent_tx'] = item['spent_tx']
            item['encrypted_data'] = item['data']
            item['unique_key'] = item['address'] + ' ' + item['transaction']
            txout = TxOut(**item)
            txout.save()


class AddrLookup:
    cache = {} # XXX Not thread safe
    def __new__(cls, addr, amount):
        obj = cls.cache.get(addr)
        if obj:
            # do some verification, otherwise, re-get it
            txs = obj.transactions
            for tx in txs:
                if tx["amount"] is not None:
                    return obj
        obj = Addr(addr, amount)
        cls.cache[addr] = obj
        return obj


class TxLookup:
    cache = {} # XXX Not thread safe
    def __new__(cls, tx, addr):
        obj = cls.cache.get((tx, addr))
        if obj:
            return obj
        obj = Tx(tx, addr)
        cls.cache[(tx, addr)] = obj
        return obj


SAT = 100000000
class Tx:
    '''
    Looking up transactions identified by :tx: that have already been
    associated with :addr:

    Don't pass in random txid's otherwise we might think an addr is
    spent when it isn't

    This is not organized right
    '''
    def __init__(self, tx, addr):
        self.tx = tx
        self.addr = addr
        data = Explorer().lookup(tx)
        self.data = data
        self.addr_looks_spent = False
        self.dump()
        self.amount = 0
        vouts = self.data.get('vout')
        #PrettyPrinter().pprint(vouts)
        for vout in vouts:
            spk = vout['scriptPubKey']
            if spk and spk.get('address', '') == addr:
                self.amount = int(vout['value'] * SAT)
            else:
                pass
        if not self.amount:
            # did not find a vout, this addr has been spent
            self.addr_looks_spent = True

    def dump(self):
        if 'hex'in self.data:
            # Just not using it now and it looks messy
            del self.data['hex']
        #PrettyPrinter().pprint(self.data)


class Addr:
    def __init__(self, addr, amount):
        self.addr = addr
        self.amount = amount
        data = Explorer().lookup(addr) or []
        self.data = {
            'txs': None,
            'addr': None
        }
        self.spent_tx = None
        for item in data:
            if 'txCount' in item:
                self.data["txs"] = item
            elif "isvalid" in item:
                self.data["addr"] = item
        self.lookup_transactions()

    def lookup_transactions(self):
        self.transactions = []
        txs = self.data["txs"]
        if not txs:
            return
        for tx, height in txs["blockHeightsByTxid"].items():
            transaction = TxLookup(tx, self.addr)
            if transaction.addr_looks_spent:
                assert txs["balanceSat"] == "0",\
                        f"Address {self.addr} looked spent"
                self.spent_tx = tx
            # These are returned in the tx_lookup api
            self.transactions.append({
                "txid": tx,
                "height": height,
                "spent": transaction.addr_looks_spent,
                "amount": transaction.amount,
                # this field is removed before sending
                # in the tx_lookup api response
                "transaction": transaction
            })

# api
def tx_lookup(request):
    post = request.POST.dict()
    addr = AddrLookup(post["address"], post["amount"])
    for tx in addr.transactions:
        if tx["txid"] == post["txid"] and post["amount"] and(
                str(tx["amount"]) == post["amount"]):
            tx["match"] = True
    # TODO: Indicate something wrong with the addr
    # Present the tx's, which one is it?
    # Remove the <Tx> objects from the data to be sent back
    payload_txs = [tx.copy() for tx in addr.transactions]
    for tx in payload_txs:
        del tx["transaction"]
    payload = {
        'data': {
            'spent_tx': addr.spent_tx,
            'transactions': payload_txs,
        }
    }
    return HttpResponse(json.dumps(payload))


class ValidateAddrMixin:
    def post(self, request, *args, **kwargs):
        self.object = None
        if kwargs.get('pk'):
            # If 'pk' is present, this is an edit. otherwise it's
            # a new.
            self.object = self.get_object()
        form = self.get_form()
        valid_tx = self.custom_is_valid(form)
        if not valid_tx:
            return self.form_invalid(form)
        if self.object:
            self.object.set_data(valid_tx["transaction"].data)
            self.update_actors()
        ret = self.form_valid(form)
        return ret

    def update_actors(self):
        for actor in self.object.get_actors():
            actor.add_txout(self.object)

    def custom_is_valid(self, form):
        '''
        Returns transaction data dict if valid. Also updates the
        form with data found from the blockchain.

        We are going to validate whether the address is found on
        the blockchain, then record what transaction it was in if
        only one. If more than one, we will record the transaction
        that matches the amount. If none or more than one match
        the amount, then we have to present with some transactions
        to choose from.

        When presenting the tx, show the amount as well so the right
        one is easier to pick out.

        TODO: Also, look at the other tx's in the database, whether
        any of them are txin's and if so record that, and associate
        the corresponding actors. Actually it would be too costly to
        scan every address whether it is a txin, just look at each
        address's tx to decide <- what?
        '''
        try:
            form = form.save(commit=False)
        except Exception as e:
            print(traceback.format_exc())
            print(form.errors)
            return None
        post = self.request.POST
        addr = AddrLookup(post["address"], post["amount"])
        txs = addr.transactions
        for tx in txs:
            found = False
            if tx["txid"] == form.transaction:
                if addr.spent_tx:
                    found = True
                elif form.amount and str(tx["amount"]) == str(form.amount):
                    found = True
            elif not form.transaction:
                if form.amount and str(tx["amount"]) == str(form.amount):
                    found = True
            if found:
                tx["match"] = True
                form.height = str(tx["height"])
                form.save()
                return tx
        return None


class TxOutCreateView(ValidateAddrMixin, CreateView):
    model = TxOut
    template_name = "txout_new.html"
    fields = (
        "address",
        "notes",
        "actors",
        "amount",
        "spent_tx",
        "owned",
        "transaction",
    )


class TxOutUpdateView(ValidateAddrMixin, UpdateView):
    model = TxOut
    template_name = "txout_edit.html"
    fields = (
        "address",
        "notes",
        "actors",
        "amount",
        "spent_tx",
        "owned",
        "transaction",
    )


class TxOutDeleteView(DeleteView):
    model = TxOut
    template_name = "txout_delete.html"
    success_url = reverse_lazy('txout_list')


class ActorCreateView(CreateView):
    model = Actor
    template_name = "actor_new.html"
    fields = (
        "name",
        "notes",
        "txouts",
        "counterparty",
    )

    def get_success_url(self):
        return reverse("actor_list")


class ActorUpdateView(UpdateView):
    model = Actor
    template_name = "actor_edit.html"
    fields = (
        "name",
        "notes",
        "counterparty",
    )

    def get_success_url(self):
        actor = self.get_object()
        return reverse("actor_detail", kwargs={"pk": actor.pk})


class ActorDetailView(DetailView):
    model = Actor
    template_name = "actor_detail.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # by defining an object list, we can re-use the
        # txout_list.html template, which is moved to main.html
        context['object_list'] = self.object.get_txouts()
        return context


class ActorListView(ListView):
    model = Actor
    template_name = "actor_list.html"


class ActorDeleteView(DeleteView):
    model = Actor
    template_name = "actor_delete.html"
    success_url = reverse_lazy('actor_list')
