import os

from setuptools import setup, find_packages


setup(

    name='acme-dns-proxy',
    version='1.0.0.dev0',

    description="Making it easy to use acme.sh with DNS CNAMEs.",
    url='http://github.com/mikeboers/acme-dns-proxy',

    license='BSD-3',

    packages=find_packages(exclude=['build*', 'tests*']),

    install_requires='''
        dnspython
    ''',

    entry_points={
        'console_scripts': '''
            acme-dns-issue = acmednsproxy.issue:main
            acme-dns-install = acmednsproxy.install:main
        '''
    }

)
