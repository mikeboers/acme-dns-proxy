#!/usr/bin/env python3

from __future__ import print_function

import argparse
import os
import shlex
import subprocess
import sys

from . import paths

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-n', '--dry-run', action='store_true')
parser.add_argument('-d', '--debug', action='store_true')

parser.add_argument('-C', '--root', default=paths.tls_data,
    help="Where to store the certs? Defaults to ~/tls")
parser.add_argument('-N', '--name',
    help="Basename of installed files; defaults to the domain name.")

parser.add_argument('-r', '--systemctl-reload', metavar='SERVICE', action='append', default=[],
    help="Issue a `systemctl reload SERVICE`; can be used multiple times.")
parser.add_argument('-R', '--reload', action='append', default=[],
    help="Manual reload commands; don't forget to sudo here.")

parser.add_argument('-x', '--extra', help="Extra arguments for acme.sh --installcert.")

parser.add_argument('primary')
parser.add_argument('secondaries', nargs='*', help="Not used here.")


def main():

    if not os.getuid():
        print("Must not run as root.")
        exit(1)

    args = parser.parse_args()


    args.name = args.name or args.primary


    reloadcmds = list(args.reload)
    for name in args.systemctl_reload:
        reloadcmds.append('sudo systemctl reload "{}"'.format(name))
    if not reloadcmds:
        print("No reloads given.", file=sys.stderr)
        exit(1)

    cmd = [
        paths.acme_exec,
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
    
    env = os.environ.copy()
    env['LE_WORKING_DIR'] = paths.acme_data

    if not args.dry_run:
        code = subprocess.call(cmd, env=env)
        exit(code)

