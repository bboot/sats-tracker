#!/usr/bin/env python3
import asyncio
import json
import logging
import sys


class ElectrumClient:
    msg_id = 0
    cached = {}

    def __init__(self, host='127.0.0.1', port=50001):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.name = None
        self.loop = asyncio.get_event_loop()
        self.request('server.version', 'sats-tracker', '1.4')

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.close()
        except:
            pass

    def close(self):
        self.writer.close()


def main(args=None):
    with ElectrumClient() as electrum:
        response = electrum.request('server.banner')
        print(response.get('result') or response.get('error'))
    return 0


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
