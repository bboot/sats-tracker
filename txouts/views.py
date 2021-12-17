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


class AddrLookup:
    cache = {} # XXX Not thread safe
    def __new__(cls, addr, amount):
        obj = cls.cache.get(addr)
        if obj:
            # do some verification, otherwise, re-get it
            txs = obj.transactions
            for tx in txs.values():
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
        self.transactions = {}
        self.lookup_transactions()

    def lookup_transactions(self):
        txs = self.data["txs"]
        for tx, height in txs["blockHeightsByTxid"].items():
            amount = TxLookup(tx, self.addr).amount
            if amount is not None:
                amount = int(amount)
            self.transactions[tx] = {
                "height": height,
                "amount": amount,
            }


def tx_lookup(request):
    post = request.POST.dict()
    del post["csrfmiddlewaretoken"]
    data = {
        'data': post
    }
    print(post)
    txs = AddrLookup(post["address"], post["amount"]).transactions
    print(f'txs out the door: {txs}')
    tx = txs.get(post["transaction"])
    if tx:
        print(f'Got the tx!!!! {tx}')
        post["amount"] = str(tx["amount"])
        return HttpResponse(json.dumps(data))
    if post["amount"]:
        for tx, tx_data in list(txs.items()):
            if tx_data["amount"] is None:
                print(f'{tx_data["amount"]} != {post["amount"]}')
                txs.pop(tx)
            elif tx_data["amount"] != int(post["amount"]):
                print(f'{tx_data["amount"]} != {post["amount"]}')
                txs.pop(tx)
    if not len(txs):
        # TODO: Indicate something wrong with the addr
        print(f'No txs!!! (left)')
        return HttpResponse(json.dumps({'candidates': txs}))
    if len(txs) == 1:
        print('Got heem!!')
        tx, tx_data = next(iter(txs.items()))
        post["transaction"] = tx
        post["amount"] = str(int(tx_data["amount"]))
        return HttpResponse(json.dumps(data))
    # Present the tx's, which one is it?
    print(f'Wich txxx!?')
    return HttpResponse(json.dumps({'candidates': txs}))


class ValidateAddrMixin:
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        print(form) # debug: print it rendered out
        print(form.__class__) # debug: what's a widgets.TxOutForm ??
        self.object = None # we're not using it but what is it
        if not self.custom_is_valid(form):
            return self.form_invalid(form)
        return self.form_valid(form)

    def custom_is_valid(self, form):
        '''
        Not sure if this is the best way to do this, but we are going
        to validate whether the address is found on the blockchain,
        then record what transaction it was in if only one. If more
        than one, we will record the transaction that matches the
        amount. If none or more than one match the amount, then we
        have to present with some transactions to choose from.

        When presenting the tx, show the amount as well so the right
        one is easier to pick out.

        Also, look at the other tx's in the database, whether any
        of them are txin's and if so record that, and associate the
        corresponding actors. Actually it would be too costly to
        scan every address whether it is a txin, just look at each
        address's tx to decide
        '''
        post = self.request.POST
        txs = AddrLookup(post["address"], post["amount"]).transactions
        print(f'txs out the door: {txs}')
        try:
            form = form.save(commit=False)
        except Exception as e:
            print(traceback.format_exc())
            return False
        tx = txs.get(form.transaction)
        if tx:
            print(f'Got the tx!!!! {tx}')
            form.amount = str(int(tx["amount"]))
            form.save()
            return True
        if form.amount:
            for tx, tx_data in list(txs.items()):
                if tx_data["amount"] != int(form.amount):
                    print(f'{tx_data["amount"]} != {form.amount}')
                    txs.pop(tx)
        if not len(txs):
            # TODO: Indicate something wrong with the addr
            print(f'No txs!!! (left)')
            if tx:
                # XXX: Allow it to save, even though we couldn't
                # find the transaction. Need to pop up a warning
                # or better yet, flag the entry.
                return True
            return False
        if len(txs) == 1:
            tx, tx_data = next(iter(txs.items()))
            form.transaction = tx
            form.amount = str(int(tx_data["amount"]))
            form.save()
            return True
        # TODO: Need to present the tx's, which one is it?
        print(f'Wich txxx!?')
        return False


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


class ActorDetailView(DetailView):
    model = Actor
    template_name = "actor_detail.html"


class ActorListView(ListView):
    model = Actor
    template_name = "actor_list.html"


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



class ActorDeleteView(DeleteView):
    model = Actor
    template_name = "actor_delete.html"
    success_url = reverse_lazy('actor_list')
