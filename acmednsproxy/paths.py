import os

here = os.path.abspath(os.path.join(__file__, '..', '..'))
home = os.environ.get("ACME_DNS_PROXY_HOME") or os.path.expanduser('~')

acme_exec = os.path.join(here, 'vendor', 'acme.sh', 'acme.sh')
acme_data = os.path.join(home, 'acme.sh')

nsupdate_keys = os.path.join(home, 'nsupdate')

tls_data = os.path.join(home, 'tls')
