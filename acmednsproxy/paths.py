import os

here = os.path.abspath(os.path.join(__file__, '..', '..'))
home = os.environ.get("ACME_DNS_PROXY_HOME") or os.path.expanduser('~')

# Use the default locations.
acme_exec = os.path.join(home, '.acme.sh', 'acme.sh')
acme_data = os.path.join(home, '.acme.sh')

# Where we pull keys from.
nsupdate_keys = os.path.join(home, 'nsupdate')

# Where we install certs to.
tls_data = os.path.join(home, 'tls')

