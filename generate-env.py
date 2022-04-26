#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import secrets
import sys


def get_content(args, data):
    content = f"""export DEBUG=True
export SECRET_KEY={data['secret_key']}
export TXOUT_UNIQUE_KEY={data['txout_unique_key']}
export FIELD_ENCRYPTION_KEYS={data['field_encryption_keys']}
export DATABASE_URL=postgres://sats_trackeruser:{data['user_password']}@{args.hostname}:5432/sats_tracker
# Bitcoind
export RPC_PORT=8332
export RPC_USER=<RPC user from your bitcoin core installation>
export RPC_PASSWORD=<RPC password from your bitcoin core installation>
export BITCOIND_HOST=<IP address of host that is running bitcoin core>
export BITCOIN_NETWORK=mainnet
# Electrum
export ELECTRUM_SERVICES=rpc://{args.electrum_host}:8000,tcp://{args.electrum_host}:50001
# To use Bitcoin Explorer instead of Electrum, for example from umbrel:
export EXPLORER=http://umbrel.local:3002
"""
    return content

def gen_encryption_material(args):
    data = {}
    data['secret_key'] = secrets.token_urlsafe(50)
    data['field_encryption_keys'] = secrets.token_hex(32)
    data['txout_unique_key'] = secrets.token_hex(32)
    data['user_password'] = secrets.token_urlsafe(16)
    return data


def main(args):
    data = gen_encryption_material(args)
    txt = get_content(args, data)
    cwd = Path(__file__).parent.resolve()
    fenv = Path(cwd.joinpath('.env'))
    if fenv.is_file():
        print(f'Not overwriting existing file at {fenv}')
        return 1
    with open(fenv, 'w') as f:
        f.write(txt)
    return 0


if __name__=="__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-H', '--hostname', action='store',
                        default='localhost',
                        help='Hostname where database is installed')
    parser.add_argument('-e', '--electrum_host', action='store',
                        default='localhost',
                        help='Hostname where electrum is installed')
    args = parser.parse_args()
    sys.exit(main(args))
