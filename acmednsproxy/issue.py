#!/usr/bin/env python3

from __future__ import print_function

from concurrent import futures
import argparse
import os
import re
import shlex
import subprocess
import sys

from . import paths


def get_alias(name, nameserver=None):
    # Attempt to resolve the challenge URL so we
    # don't have to have a pattern established in advance.
    # Strip off the asterix because they do.
    alias = '_acme-challenge.' + (name[2:] if name.startswith('*.') else name)

    cmd = ['dig']
    if nameserver:
        cmd.append('@' + nameserver)
    cmd.extend(('+short', alias))
    res = subprocess.check_output(cmd).decode()
    for line in res.splitlines():
        line = line.strip()
        if line.endswith('.'):
            alias = line.strip('.')
            break
    return name, alias    


def get_nameserver(name, nameserver=None):

    # Lookup the authority so we know what server/key to use.
    # We do this from 1.1.1.1 because on a few of our servers the
    # local dnsmasq is getting in the way.
    cmd = ['dig']
    if nameserver:
        cmd.append('@' + nameserver)
    cmd.extend((
        '+noall',
        '+authority',
        '+answer',
        name,
        'soa',
    ))
    soa = subprocess.check_output(cmd).decode()
    m = re.search(r'''
        ^
        (\S+)\s+ # The name.
        \d+\s+ # TTL.
        IN\s+
        SOA\s+
        (\S+) # The SOA.
    ''', soa, flags=re.M | re.X)
    if not m:
        print("Could not parse SOA for {}: {!r}".format(name, soa), file=sys.stderr)
        exit(1)
    if m.group(1) == '.':
        print("Could not find SOA for {}: {!r}".format(name, soa), file=sys.stderr)
        exit(2)

    return m.group(2).strip('.')


parser = argparse.ArgumentParser(description='''

First stage in the two-stage acme.sh Lets Encrypt process;
this proves to Lets Encrypt that you own the domains in question.

This script works best if you setup `_acme-proxy.YOURNAME` as a CNAME
to something that is on a DNS server that accepts updates, e.g.
Mike's acme-proxy.thequagmire.xyz.

Given a domain name (or names), this script resolves `_acme-proxy.YOURNAME`
to determine what it is actually updating, and determines
the authoritative nameserver for that as well.

''')

parser.add_argument('-v', '--verbose', action='store_true',
    help="acme.sh prints more.")
parser.add_argument('-n', '--dry-run', action='store_true',
    help="Do all resolution, but don't do anything.")
parser.add_argument('-d', '--debug', action='store_true',
    help="acme.sh debug mode prints out lots more.")
parser.add_argument('-f', '--force', action='store_true',
    help='acme.sh --force')

parser.add_argument('-s', '--staging', action='store_true',
    help="use letsencrypt's staging server; the certs don't validate, but the rate limiting is more forgiving (for testing)")
parser.add_argument('-x', '--extra',
    help="Extra arguments for acme.sh.")

parser.add_argument('-S', '--soa-nameserver', default='1.1.1.1',
    help="Nameserver to query for SOA records (to resolve other nameservers).")
parser.add_argument('-A', '--alias-nameserver',
    help="Nameserver for alias resolution (to figure out what to update); defaults to the OS.")
parser.add_argument('-C', '--challenge-nameserver',
    help="Nameserver for posting challenges; defaults to nameserver of first domain (via --soa-nameserver).")

parser.add_argument('domains', nargs='+')


def main():


    if not os.getuid():
        print("Must not run as root.")
        exit(1)

    args = parser.parse_args()

    cmd = [
        paths.acme_exec,
        '--issue',
        '--dns', 'dns_nsupdate',
        '--dnssleep', '5' if any('*' in x for x in args.domains) else '0',
    ]

    if not args.alias_nameserver:
        args.alias_nameserver = get_nameserver(args.domains[0], args.soa_nameserver)

    # Control flow is a little convoluted for speed.
    print('# Resolving aliases via', args.alias_nameserver)
    executor = futures.ThreadPoolExecutor(len(args.domains))
    for i, (name, alias) in enumerate(executor.map(lambda x: get_alias(x, args.alias_nameserver), args.domains)):
        print('#    {} -> {}'.format(name, alias))
        if not i:
            challenge_nameserver = args.challenge_nameserver or get_nameserver(alias)
        cmd.extend((
            '-d', name,
            '--domain-alias', alias,
        ))


    env = os.environ.copy()
    env['LE_WORKING_DIR'] = paths.acme_data
    env['NSUPDATE_SERVER'] = challenge_nameserver
    env['NSUPDATE_KEY'] = keypath = os.path.join(paths.nsupdate_keys, challenge_nameserver + '.key')
    if not os.path.exists(keypath):
        print("Please create nsupdate key file at:", keypath)
        exit(1)

    print("$ NSUPDATE_SERVER={}".format(challenge_nameserver))
    print("$ NSUPDATE_KEY={}".format(keypath))


    if args.verbose:
        cmd.append('--log')
    if args.debug:
        cmd.append('--debug')
    if args.force:
        cmd.append('--force')
    if args.staging:
        cmd.extend(('--server', 'https://acme-staging-v02.api.letsencrypt.org/directory'))

    if args.extra:
        cmd.extend(shlex.split(args.extra))

    print('$', ' '.join(('\\\n    ' if x.startswith('-') else '') + x for x in cmd))

    if not args.dry_run:
        code = subprocess.call(cmd, env=env)
        exit(code)

