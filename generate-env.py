#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import secrets
import socket
import stat
import sys


def get_content(args, data):
    content = f"""export DEBUG=True
export SECRET_KEY={data['secret_key']}
export TXOUT_UNIQUE_KEY={data['txout_unique_key']}
export FIELD_ENCRYPTION_KEYS={data['field_encryption_keys']}
export DB_PASSWORD={data['user_password']}
export DATABASE_URL=postgres://sats_trackeruser:$DB_PASSWORD@{args.hostname}:5432/sats_tracker
# Bitcoind
export RPC_PORT=8332
export RPC_USER='<RPC user from your bitcoin core installation>'
export RPC_PASSWORD='<RPC password from your bitcoin core installation>'
export BITCOIND_HOST='<IP address of host that is running bitcoin core>'
export BITCOIN_NETWORK=mainnet
# Electrum
export ELECTRUM_SERVICES=rpc://{args.electrum_host}:8000,tcp://{args.electrum_host}:50001
# To use Bitcoin Explorer instead of Electrum, for example from umbrel:
export EXPLORER=http://umbrel.local:3002
export ALLOWED_HOSTS=localhost,127.0.0.1,{socket.gethostname()}
"""
    return content

def get_pg_setup_txt(args, data):
    postgres_setup_txt=f'''#!/bin/sh
sudo -u postgres psql -c "CREATE DATABASE sats_tracker;"
sudo -u postgres psql -c "
CREATE USER sats_trackeruser WITH PASSWORD \'{data['user_password']}\';
ALTER ROLE sats_trackeruser SET client_encoding TO 'utf8';
ALTER ROLE sats_trackeruser SET default_transaction_isolation TO 'read committed';
ALTER ROLE sats_trackeruser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sats_tracker TO sats_trackeruser;
"
'''
    return postgres_setup_txt

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
        print(f'Not overwriting existing .env file at {fenv}')
        return 1
    with open(fenv, 'w') as f:
        f.write(txt)
    pgsetup = Path(cwd.joinpath('pgsetup.sh'))
    if pgsetup.is_file():
        print(f'Not overwriting existing pgsetup.sh file at {pgsetup}')
        return 1
    with open(pgsetup, 'w') as f:
        f.write(get_pg_setup_txt(args, data))
    st = os.stat(pgsetup)
    os.chmod(pgsetup, st.st_mode | stat.S_IEXEC)
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
