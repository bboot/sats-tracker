from datetime import datetime
from django.shortcuts import render
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
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.order_by("height")
        return qs


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
        obj = cls.cache.get(tx)
        if obj:
            return obj
        obj = Tx(tx, addr)
        cls.cache[tx] = obj
        return obj


SAT = 100000000
class Tx:
    def __init__(self, tx, addr):
        self.tx = tx
        self.addr = addr
        data = Explorer().lookup(tx)
        self.data = data
        self.dump()
        self.amount = None
        vouts = self.data.get('vout')
        print('@@@@@@@@@@@@@@@@vouts:')
        PrettyPrinter().pprint(vouts)
        for vout in vouts:
            spk = vout['scriptPubKey']
            if spk['address'] == addr:
                print('Founndddd itttt!')
                self.amount = vout['value'] * SAT
            else:
                # debug
                print(f"{spk['address']} != {addr}")

    def dump(self):
        if 'hex'in self.data:
            # Just not using it now and it looks messy
            del self.data['hex']
        PrettyPrinter().pprint(self.data)


class Addr:
    def __init__(self, addr, amount):
        self.addr = addr
        self.amount = amount
        data = Explorer().lookup(addr)
        self.data = {
            'txs': None,
            'addr': None
        }
        for item in data:
            if 'txCount' in item:
                self.data["txs"] = item
            elif "isvalid" in item:
                self.data["addr"] = item
        self.transactions = []
        self.lookup_transactions()

    def lookup_transactions(self):
        txs = self.data["txs"]
        for tx, height in txs["blockHeightsByTxid"].items():
            transaction = TxLookup(tx, self.addr)
            amount = transaction.amount
            if amount is not None:
                amount = int(amount)
            self.transactions.append({
                "txid": tx,
                "height": height,
                "amount": amount,
                "transaction": transaction
            })

# api
def tx_lookup(request):
    post = request.POST.dict()
    del post["csrfmiddlewaretoken"]
    data = {
        'data': post
    }
    txs = AddrLookup(post["address"], post["amount"]).transactions
    print(f'txs found are: {txs}')
    for tx in txs:
        if tx["txid"] == post["transaction"] and post["amount"] and(
                str(tx["amount"]) == post["amount"]):
            print(f'Got the tx!!!! {tx}')
            post["transaction"] = tx["txid"]
            post["height"] = str(tx["height"])
            return HttpResponse(json.dumps(data))
    # TODO: Indicate something wrong with the addr
    # Present the tx's, which one is it?
    # Remove the <Tx> objects from the data to be sent back
    for tx in txs:
        if "transaction" in tx:
            del tx["transaction"]
    return HttpResponse(json.dumps({'candidates': txs}))


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
        return self.form_valid(form)

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
        txs = AddrLookup(post["address"], post["amount"]).transactions
        print(f'txs out the door: {txs}')
        for tx in txs:
            if tx["txid"] == form.transaction and form.amount and(
                    str(tx["amount"]) == form.amount):
                print(f'Got the tx!!!! {tx}')
                form.height = str(tx["height"])
                form.save()
                return tx
        # TODO: Need to present the tx's, which one is it?
        print(f'Wich txxx!?')
        return None


class TxOutCreateView(ValidateAddrMixin, CreateView):
    model = TxOut
    template_name = "txout_new.html"
    fields = (
        "address",
        "notes",
        "actors",
        "amount",
        "spent",
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
        "spent",
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
        actor = self.get_object()
        return reverse("actor_detail", kwargs={"pk": actor.pk})


class ActorUpdateView(UpdateView):
    model = Actor
    template_name = "actor_edit.html"
    fields = (
        "name",
        "notes",
        "txouts",
        "counterparty",
    )

    def get_success_url(self):
        actor = self.get_object()
        return reverse("actor_detail", kwargs={"pk": actor.pk})


class ActorDetailView(DetailView):
    model = Actor
    template_name = "actor_detail.html"


class ActorListView(ListView):
    model = Actor
    template_name = "actor_list.html"


class ActorDeleteView(DeleteView):
    model = Actor
    template_name = "actor_delete.html"
    success_url = reverse_lazy('actor_list')
