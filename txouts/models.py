from datetime import datetime
from django.db import models
from django.urls import reverse
import json

from txouts.icons import Animal


# Create your models here.
class TxOut(models.Model):
    '''
    TODO: Entries must be a unique combo of tx and address
    '''
    address = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    actors = models.ManyToManyField("txouts.Actor")
    txins = models.ManyToManyField("txouts.TxOut", blank=True)
    amount = models.BigIntegerField()
    height = models.IntegerField(default=1)
    # Maybe store a spent_tx instead of just a boolean, also
    # this boolean is known when we look it up so it shouldn't
    # be part of the form but leave it for now.
    spent = models.BooleanField(default=False)
    owned = models.BooleanField(default=True)
    # We need to record the transaction because the address
    # is often used in more than one.
    # Are transactions always 65 chars?
    # This can be left blank as it will be looked up anyways.
    transaction = models.CharField(max_length=100, blank=True)
    # Don't get too dependent on JSONField or anything, since
    # we are going to store this encrypted later.
    # May want to use BinaryField
    # data = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('address', 'transaction')

    def __init__(self, *args, **kwargs):
        self.data_json = None # XXX not used yet
        return super().__init__(*args, **kwargs)

    @property
    def blocktime(self):
        if not self.data_json:
            self.data_json = json.loads(self.data)
        blocktime = self.data_json.get("blocktime")
        if not blocktime:
            return ""
        return f"{datetime.fromtimestamp(int(blocktime))}"

    def get_actors(self):
        for actor in self.actors.all():
            print(actor)
            yield actor

    def validated(self):
        if self.height < 2:
            return False
        if len(self.transaction) < 64:
            return False
        return True

    def __str__(self):
        '''
        TODO(maybe) "spent" could be a link to the tx in which
        it was spent
        '''
        spent = ''
        if self.spent:
            spent = ' (spent)'
        owned = '(*)'
        if not self.owned:
            owned = ''
        return '{}[{}..{}] {:,}${}'.format(
            owned,
            self.address[0:4],
            self.address[-6:],
            self.amount,
            spent,
        )

    def fmt_amount(self):
        return '{:,}'.format(int(self.amount))

    def get_absolute_url(self):
        return reverse("txout_detail", args=[str(self.id)])


class Actor(models.Model):
    name = models.CharField(max_length=80)
    notes = models.TextField(blank=True)
    txouts = models.ManyToManyField(TxOut, blank=True)
    counterparty = models.BooleanField(default=True)

    def __str__(self):
        owned = "(*)"
        if self.counterparty:
            owned = ""
        return f"{owned}{self.name}"

    def get_movements(self):
        for movement in self.txouts.all():
            print(movement)
            yield movement

    @property
    def icon(self):
        return Animal(self.id).classes()

    @property
    def color(self):
        return Animal(self.id).color()

    @property
    def style(self):
        return Animal(self.id).style()

    def get_absolute_url(self):
        return reverse("txout_list", args=[str(self.id)])
