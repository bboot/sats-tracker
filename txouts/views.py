from django.urls import reverse, reverse_lazy
from django.views.generic import (
        DetailView,
        ListView,
        CreateView,
        UpdateView,
        DeleteView,
    )

from .models import TxOut, Actor

# Create your views here.
class TxOutDetailView(DetailView):
    model = TxOut
    template_name = "txout_detail.html"


class TxOutListView(ListView):
    model = TxOut
    template_name = "txout_list.html"


class TxOutCreateView(CreateView):
    model = TxOut
    template_name = "txout_new.html"
    fields = (
        "address",
        "notes",
        "actors",
        "txins",
        "amount",
        "spent",
        "owned",
        "transaction",
    )


class TxOutUpdateView(UpdateView):
    model = TxOut
    template_name = "txout_edit.html"
    fields = (
        "address",
        "notes",
        "actors",
        "txins",
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
