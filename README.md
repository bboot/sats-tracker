Sats Tracker
==
This is a python-django app, intended to run in a local network, not in the cloud, as it stores private information. A good place to install it is on a local computer or an umbrel. All data is stored encrypted on-disk.

This version connects to electrum and bitcoin core to look up bitcoin addresses and transactions that are entered. Everything after that is manual right now. The data is collected in two categories: "txouts" and "actors". The point of this project is to link txouts to "actors" (for lack of a better name) so that the users track exactly how much information is theoretically available to surveillance analytics.

# Installation
Instructions are for Debian Linux, but with some modifications to the commands below it should install fine on other platforms.
- Install dependencies: Recommended to have python >= 3.9
`sudo apt install python3 python3-pip python3-venv python3-dev libpq-dev libxml2-dev libxslt-dev postgresql postgresql-contrib`
- Launch python virtual environment
`source .venv/bin/activate`
- Install python requirements
`pip install -r requirements.txt`
- Set up environment
`./generate-env.py`
`./pgsetup.sh`
- Initial django setup of database
`./manage.py makemigrations`
`./manage.py migrate`
- Create the django superuser.
`./manage.py createsuperuser`
- Run it
`./manage.py runserver 0.0.0.0:8020`
- Log into `http://localhost:8020` with the superuser's credentials and start adding transactions

If you want to use a separate user than the superuser, log into `http://localhost:8020/admin` and click on `AUTHENTICATION AND AUTHORIZATION` and create a regular user. The superuser can browse the database but cannot read users' data as that is encrypted

# TODO
- add a backup
- add search function
- use BDK for watch-only wallets to remove the manual entry
