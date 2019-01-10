#!/usr/bin/env python3

from __future__ import print_function

from concurrent import futures
import argparse
import os
import re
import shlex
import subprocess
import sys


def get_alias(name):
    # Attempt to resolve the challenge URL so we
    # don't have to have a pattern established in advance.
    # Strip off the asterix because they do.
    alias = '_acme-challenge.' + (name[2:] if name.startswith('*.') else name)
    res = subprocess.check_output([
        'dig',
        '+short',
        alias,
    ]).decode()
    for line in res.splitlines():
        line = line.strip()
        if line.endswith('.'):
            alias = line.strip('.')
            break
    return name, alias    

def get_primary(name):

    # Lookup the authority so we know what server/key to use.
    soa = subprocess.check_output([
        'dig',
        '+noall',
        '+authority',
        '+answer',
        name,
        'soa',
    ]).decode()
    m = re.match(r'^(\S+)\s+\d+\s+IN\s+SOA\s+(\S+)\s', soa)
    if not m:
        print("Could not parse SOA: {}".format(soa), file=sys.stderr)
        exit(1)
    if m.group(1) == '.':
        print("Could not find SOA: {}".format(args.domains[0]), file=sys.stderr)
        exit(2)

    return m.group(2).strip('.')


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-n', '--dry-run', action='store_true')
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-x', '--extra')
parser.add_argument('-s', '--staging', action='store_true')
parser.add_argument('domains', nargs='+')
args = parser.parse_args()


cmd = [
    os.path.expanduser('~letsencrypt/.acme.sh/acme.sh'),
    '--issue',
    '--dns', 'dns_nsupdate',
    '--dnssleep', '5' if any('*' in x for x in args.domains) else '0',
]


# Control flow is a little convoluted for speed.
print('# Resolving aliases...')
executor = futures.ThreadPoolExecutor(len(args.domains))
for i, (name, alias) in enumerate(executor.map(get_alias, args.domains)):
    print('#    {} -> {}'.format(name, alias))
    if not i:
        primary = get_primary(alias)
    cmd.extend((
        '-d', name,
        '--domain-alias', alias,
    ))


env = os.environ.copy()
env['NSUPDATE_SERVER'] = primary
env['NSUPDATE_KEY'] = keypath = os.path.join(os.path.expanduser('~/nsupdate'), primary + '.key')
print("$ NSUPDATE_SERVER={}".format(primary))
print("$ NSUPDATE_KEY={}".format(keypath))


if args.verbose:
    cmd.append('--log')
if args.debug:
    cmd.append('--debug')
if args.staging:
    cmd.extend(('--server', 'https://acme-staging-v02.api.letsencrypt.org/directory'))

if args.extra:
    cmd.extend(shlex.split(args.extra))

print('$', ' '.join(('\\\n    ' if x.startswith('-') else '') + x for x in cmd))

if not args.dry_run:
    code = subprocess.call(cmd, env=env)
    exit(code)
