
# acme-dns-proxy

## Install

```

useradd --system -m -d /var/lib/letsencrypt -s /bin/bash letsencrypt
su letsencrypt
cd

# Install acme.sh
curl https://get.acme.sh | sh -s email=my@example.com

# Install acme-dns-proxy
mkdir dev
git clone git@github.com:mikeboers/acme-dns-proxy dev/acme-dns-proxy
cd dev/acme-dns-proxy
git submodule update --init
cd ../..

python3 -m venv venv
. venv/bin/activate
pip install -e dev/acme-dns-proxy

echo 'source ~/venv/bin/activate' >> ~/.bashrc

```

## Use

Use `acme-dns-issue` and `acme-dns-install` commands to simplify the DNS-based letsencrypt process.

We assume that:

- You're running your own bind on your primary nameserver.
- Domains are optionally CNAME-d into a more convenient location. E.g. Mike runs a dynamic `acme-proxy.thequagmire.xyz`.
- You have setup update keys for your bind (which are either able to update the `_acme-challenge` subdomain, or whatever the CNAME is).
- Your update keys are stored them in `nsupdate/$nameserver.key`.
- The SOA for each of your domains points at your bind.

Basic use:

```
acme-dns-issue example.com foo.example.com *.bar.example.com
acme-dns-install -r nginx example.com
```

