from django.db import models

# Create your models here.
class TxOut(models.Model):
    address = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    actors = models.ManyToManyField("txouts.Actor")
    txins = models.ManyToManyField("txouts.TxOut", blank=True)
    amount = models.BigIntegerField()
    # maybe store a spent_tx instead of just a boolean
    spent = models.BooleanField(default=False)

    def __str__(self):
        '''
        TODO(maybe) "spent" could be a link to the tx in which
        it was spent
        '''
        spent = ''
        if self.spent:
            spent = ' (spent)'
        return '[{}..{}] {:,}${}'.format(
            self.address[0:4],
            self.address[-6:],
            self.amount,
            spent,
        )


    def get_absolute_url(self):
        return reverse("txout_detail", args=[str(self.id)])


class Actor(models.Model):
    name = models.CharField(max_length=80)
    notes = models.TextField(blank=True)
    txouts = models.ManyToManyField(TxOut, blank=True)
    counterparty = models.BooleanField(default=True)

    def __str__(self):
        counterparty = ""
        if self.counterparty:
            counterparty = "(*)"
        return f"{counterparty}{self.name}"

    def get_absolute_url(self):
        return reverse("txout_list", args=[str(self.id)])
