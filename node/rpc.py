import bitcoin
import bitcoin.rpc
from environs import Env


class BitcoinRpc(bitcoin.rpc.Proxy):
    initialized = False

    def __init__(self):
        if not self.initialized:
            BitcoinRpc.initialize()
            super().__init__(service_url=self.url)

    @classmethod
    def initialize(cls):
        '''
        Experiment with a long-standing rpc connection
        '''
        env = Env()
        env.read_env()
        rpc_user = env.str("RPC_USER", default="default_user")
        rpc_port = env.int('RPC_PORT', default=8332)
        rpc_password = env.str('RPC_PASSWORD')
        network = env.str("BITCOIN_NETWORK", default="mainnet")
        host = env.str("BITCOIND_HOST", default="localhost")
        bitcoin.SelectParams(network)
        cls.url = f"http://{rpc_user}:{rpc_password}@{host}:{rpc_port}"
