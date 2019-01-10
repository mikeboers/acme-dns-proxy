#!/usr/bin/env python3

from __future__ import print_function

import argparse
import subprocess
import os
import shlex
import sys

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-n', '--dry-run', action='store_true')
parser.add_argument('-d', '--debug', action='store_true')

parser.add_argument('-C', '--root', default=os.path.expanduser('~letsencrypt/tls'))
parser.add_argument('-N', '--name', help="Basename of installed files.")

parser.add_argument('-r', '--systemctl-reload', action='append', default=[])
parser.add_argument('-R', '--reload', action='append', default=[], help="Manual reload commands; don't forget to sudo.")

parser.add_argument('-x', '--extra', help="Extra arguments for acme.sh --installcert.")

parser.add_argument('primary')
parser.add_argument('secondaries', nargs='*', help="Not used here.")

args = parser.parse_args()


args.name = args.name or args.primary


reloadcmds = list(args.reload)
for name in args.systemctl_reload:
    reloadcmds.append('sudo systemctl reload "{}"'.format(name))
if not reloadcmds:
    print("No reloads given.", file=sys.stderr)
    exit(1)

cmd = [
    os.path.expanduser('~letsencrypt/.acme.sh/acme.sh'),
    '--installcert',
    '-d', args.primary,
    '--key-file', os.path.join(args.root, args.name + '.key'),
    '--fullchain-file', os.path.join(args.root, args.name + '.pem'),
    '--reloadcmd', '; '.join(reloadcmds),
]

#for name in args.secondaries:
#	cmd.extend(('-d', name))

if args.verbose:
    cmd.append('--log')
if args.debug:
    cmd.append('--debug')
if args.extra:
    cmd.extend(shlex.split(args.extra))

print('$', ' '.join(cmd))

if not args.dry_run:
    code = subprocess.call(cmd)
    exit(code)

