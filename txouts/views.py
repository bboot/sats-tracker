from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
        DetailView,
        ListView,
        CreateView,
        UpdateView,
        DeleteView,
    )
from pprint import PrettyPrinter

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
        for vout in vouts:
            spk = vout['scriptPubKey']
            if spk['address'] == addr:
                self.amount = vout['value'] * SAT

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
            self.transactions[tx] = {
                "height": height,
                "amount": int(TxLookup(tx, self.addr).amount)
            }


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
        form = form.save(commit=False)
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
