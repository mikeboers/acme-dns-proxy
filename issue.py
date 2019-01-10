#!/usr/bin/env python3

from __future__ import print_function

import argparse
import subprocess
import os
import shlex

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-n', '--dry-run', action='store_true')
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-x', '--extra')
parser.add_argument('-s', '--staging', action='store_true')
parser.add_argument('domains', nargs='+')
args = parser.parse_args()


env = os.environ.copy()
env['NSUPDATE_SERVER'] = 'ns1.thequagmire.xyz'
env['NSUPDATE_KEY'] = os.path.expanduser('~letsencrypt/nsupdate/acme-proxy.thequagmire.xyz.key')

cmd = [
    os.path.expanduser('~letsencrypt/.acme.sh/acme.sh'),
    '--issue',
    '--dns', 'dns_nsupdate',
    '--dnssleep', '5' if any('*' in x for x in args.domains) else '0',
]

for name in args.domains:
    if name.startswith('*.'):
        alias = name[2:]
    else:
        alias = name
    cmd.extend((
        '-d', name,
        '--domain-alias', alias + '.acme-proxy.thequagmire.xyz',
    ))

if args.verbose:
    cmd.append('--log')
if args.debug:
    cmd.append('--debug')
if args.staging:
    cmd.extend(('--server', 'https://acme-staging-v02.api.letsencrypt.org/directory'))

if args.extra:
    cmd.extend(shlex.split(args.extra))

print('$', ' '.join(cmd))

if not args.dry_run:
    code = subprocess.call(cmd, env=env)
    exit(code)
