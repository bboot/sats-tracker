import datetime as dt
from django.db import models
from django.urls import reverse
from encrypted_fields import fields
from environs import Env
import json
from pathlib import Path

from txouts.icons import Animal

env = Env()
env.read_env()


# Create your models here.
class TxOut(models.Model):
    '''
    Entries are a unique combo of tx and address
    TODO: "*" will replace "encrypted_*" once it all works.
    '''
    # XXX: for encrypted fields blank is ok for now
    _unique_key_data = fields.EncryptedCharField(blank=True, max_length=100)
    unique_key = fields.SearchField(hash_key=env.str("TXOUT_UNIQUE_KEY"),
            encrypted_field_name='_unique_key_data', unique=True)
    # need address since it's entered in the form
    # TODO: should consolidate this and transaction to unique_key
    address = fields.EncryptedCharField(max_length=100)
    notes = fields.EncryptedTextField()
    actors = models.ManyToManyField("txouts.Actor")
    amount = fields.EncryptedBigIntegerField()
    height = fields.EncryptedIntegerField(default=1)
    owned = models.BooleanField(default=True)
    # We need to record the transaction because the address
    # is often used in more than one.
    # Are transactions always 65 chars?
    # This can be left blank as it will be looked up anyways.
    transaction = fields.EncryptedCharField(max_length=100, blank=True)
    spent_tx = fields.EncryptedCharField(max_length=100, blank=True)
    # Don't get too dependent on JSONField or anything, since
    # we are going to store this encrypted later.
    # May want to use BinaryField
    # I think data will be:
    # { 'transaction': tx_dict, 'addr-details': details_dict }
    data = fields.EncryptedTextField(default="{}")

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def get_block_time(self):
        data = json.loads(self.data)
        return data.get("transaction", {}).get("blocktime")

    @property
    def blocktime(self):
        '''
        XXX: These "properties" should go in the View class,
        under get_context_data
        '''
        blocktime = self.get_block_time()
        if not blocktime:
            return ""
        return f"{dt.datetime.fromtimestamp(int(blocktime))}"

    @property
    def blockdate(self):
        blocktime = self.get_block_time()
        if not blocktime:
            return ""
        return f"{dt.datetime.fromtimestamp(int(blocktime)).strftime('%D')}"

    @property
    def blockhour(self):
        blocktime = self.get_block_time()
        if not blocktime:
            return ""
        hour = dt.datetime.fromtimestamp(int(blocktime),
                                         tz=dt.timezone(dt.timedelta(hours=-8)))
        return f"{hour.strftime('%I:%M:%S %p')}"

    def set_data(self, data):
        if not data:
            return
        if "blocktime" in data:
            key = "transaction"
        elif "txCount" in data:
            key = "addr-details"
        else:
            key = "not-sure"
        data_json = json.loads(self.data)
        existing = data_json.get(key)
        if existing:
            existing.update(data)
        else:
            data_json[key] = data
        self.data = json.dumps(data_json)

    def get_actors(self):
        for actor in self.actors.all():
            yield actor

    def validated(self):
        if self.height < 2:
            return False
        if len(self.transaction) < 64:
            return False
        return True

    def addr_repr(self):
        return self.address[-6:]

    def __str__(self):
        '''
        TODO(maybe) "spent" could be a link to the tx in which
        it was spent
        '''
        spent = ''
        if self.spent_tx:
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

    def get_txouts(self):
        for transaction in self.txouts.all():
            yield transaction

    def add_txout(self, txout):
        self.txouts.add(txout)

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
