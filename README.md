
Use `issue` and `install` commands to simplify the DNS-based letsencrypt process.

We assume that:

- You're running your own bind on your primary nameserver.
- Domains are optionally CNAME-d into a more convenient location. E.g. Mike runs a dynamic `acme-proxy.thequagmire.xyz`.
- You have setup update keys for your bind (which are either able to update the `_acme-challenge` subdomain, or whatever the CNAME is).
- Your update keys are stored them in `nsupdate/$nameserver.key`.
- The SOA for each of your domains points at your bind.

Basic use:

```
./issue example.com foo.example.com *.bar.example.com
./install -r nginx example.com
```

