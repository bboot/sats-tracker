from django.shortcuts import render
from environs import Env
from lightning import LightningRpc

from .rpc import BitcoinRpc


class BitcoinViewData:
    def __init__(self, running):
        self.running = running
        self.online = False
        self.peer_count = 0
        self.block_height = 0
        self.version = ""
        self.message = ""

class LightningViewData:
    def __init__(self, running):
        self.running = running
        self.peer_count = 0
        self.channel_count = 0
        self.block_height = 0
        self.version = ""
        self.message = ""


def index(request):
    # LIGHTNING NETWORK
    # Lightning Network Socket file (you might need to change this)
    ln = LightningRpc("/home/pi/.lightning/lightning-rpc")
    try:
        l_info = ln.getinfo()
        l = LightningViewData(True)
        l.block_height = l_info["blockheight"]
        l.version = l_info["version"]
        l.version = l.version.replace("v", "")

        l_peers = ln.listpeers()
        l.peer_count = len(l_peers["peers"])

        l_funds = ln.listfunds()
        l.channel_count = len(l_funds["channels"])
    except:
        l = LightningViewData(False)

    # BITCOIN
    b = BitcoinViewData(True)
    try:
        rpc = BitcoinRpc()
        header = rpc.call('getblockheader', rpc.call('getbestblockhash'))
        b.block_height = header['height']
        info = rpc.call('getnetworkinfo')
        b.version = info["subversion"].replace("/", "").replace("Satoshi:", "")
        b.peer_count = int(info["connections"])
        if b.peer_count > 0:
            b.online = True
    except Exception as e:
        b.message = str(e)
        b.running = False

    # RETURN VIEW DATA
    return render(request, 'node.html', {'lightning': l, 'bitcoin': b})
