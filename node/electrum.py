#!/usr/bin/env python3
import asyncio
from environs import Env
import hashlib
import json
import logging
import sys

env = Env()
env.read_env()


class ElectrumClient:
    services = []
    msg_id = 0
    cached = {}

    def __init__(self, host=None, port=None):
        self.parse_services()
        tcps = list(filter(None, map(
            lambda s: s if s['protocol'] == 'tcp' else None, self.services)))
        tcp = tcps[0] # just get the first one
        self.host = host or tcp['host']
        self.port = port or tcp['port']
        self.reader = None
        self.writer = None
        self.name = None
        self.loop = self.get_or_create_eventloop()
        response = self.request('server.version', 'sats-tracker', '1.4')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.close()
        except:
            pass

    def close(self):
        self.writer.close()

    def get_or_create_eventloop(self):
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        return asyncio.get_event_loop()

    def request(self, method, *args, **kwargs):
        response = self.loop.run_until_complete(
                self._request(method, *args, **kwargs))
        return response

    def build_request(self, method, *args, **kwargs):
        jsonrpc = {
            'jsonrpc': '2.0',
            'method': method,
        }
        with_id = kwargs.pop('with_id', True)
        if args:
            jsonrpc['params'] = list(args)
        if kwargs:
            params = jsonrpc.get('params', [])
            jsonrpc['params'] = params + [{k: v} for k, v in kwargs.items()]
        if with_id:
            return self.with_id(jsonrpc, from_dict=True)
        return json.dumps(jsonrpc)

    def with_id(self, jsonrpc, from_dict=False):
        if not from_dict:
            jsonrpc = json.loads(jsonrpc)
        jsonrpc['id'] = self.msg_id
        self.msg_id += 1
        return json.dumps(jsonrpc) + '\n'

    async def _request(self, method, *args, **kwargs):
        if not self.reader:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        kwargs['with_id'] = False
        request = self.build_request(method, *args, **kwargs)
        cached_data = self.cached.get(request)
        if cached_data:
            return json.loads(cached_data)
        self.writer.write(self.with_id(request).encode())
        data = ''
        while '\n' not in data:
            # TODO: how to keep this from hanging if the server doesn't respond
            line = await self.reader.readline()
            data += line.decode()
        self.cached[request] = data
        return json.loads(data)

    def get_details(self, pk):
        '''
        This will produce the same output that btc-rpc-explorer produces
        '''
        details = {}
        pk_hash = self.pubkey_hash(pk)
        #print(f'hash of pubkey is {pk_hash}')
        response = self.request('blockchain.scripthash.get_history', pk_hash)
        result = response.get('result')
        if result:
            result.reverse()
            details['txCount'] = len(result)
            details['txids'] = [t['tx_hash'] for t in result]
            details['blockHeightsByTxid'] = {
                t['tx_hash']: t['height'] for t in result
            }
            details['balanceSat'] = 0
        response = self.request('blockchain.scripthash.get_balance', pk_hash)
        result = response.get('result')
        if result:
            details['balanceSat'] = result['confirmed']
        return details

    def reverse_hex(self, hexstr):
        it = iter(hexstr)
        items = [a + b for a, b in zip(it, it)]
        items.reverse()
        return ''.join(items)

    def pubkey_hash(self, pk):
        # should assert if invalid hex or length
        hexstr = hashlib.sha256(bytes.fromhex(pk)).hexdigest()
        return self.reverse_hex(hexstr)

    def parse_services(self):
        if self.services:
            return self.services
        # ELECTRUM_SERVICES=rpc://localhost:8000,tcp://umbrel.local:50001
        svc = env.str('ELECTRUM_SERVICES', 'tcp://localhost:50001').split(',')
        for service in svc:
            try:
                protocol, host, port = service.split(':')
                self.services.append({
                    'protocol': protocol,
                    'host': host.split('//')[1],
                    'port': int(port),
                })
            except Exception as e:
                print(f'error parsing {service}')


def main(args=None):
    with ElectrumClient() as electrum:
        response = electrum.request('server.banner')
        print(response.get('result') or response.get('error'))
    return 0


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
