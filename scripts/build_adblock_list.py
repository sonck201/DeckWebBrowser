#!/usr/bin/env python3
"""Merge ad-block host lists into defaults/adblock-hosts.txt (one domain per line).

Accepts plain domain lists and hosts-file format ("0.0.0.0 domain").
Usage: python3 scripts/build_adblock_list.py
"""
import os
import re
import urllib.request

SOURCES = [
    'https://pgl.yoyo.org/adservers/serverlist.php?hostformat=nohtml&showintro=0&mimetype=plaintext',
    'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
    'https://raw.githubusercontent.com/StevenBlack/hosts/refs/heads/master/alternates/fakenews-gambling/hosts',
    'https://raw.githubusercontent.com/StevenBlack/hosts/refs/heads/master/alternates/gambling/hosts',
]
OUT = os.path.join(os.path.dirname(__file__), '..', 'defaults', 'adblock-hosts.txt')

DOMAIN = re.compile(r'^(?=.{1,253}$)([a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?\.)+[a-z][a-z0-9-]{0,62}$')
IP = re.compile(r'^[0-9.]+$|:')
SKIP = {'localhost', 'localhost.localdomain', 'local', 'broadcasthost', '0.0.0.0'}


def parse(text):
    for line in text.splitlines():
        tokens = line.split('#', 1)[0].lower().split()
        if tokens and IP.search(tokens[0]):
            tokens = tokens[1:]
        for token in tokens:
            if token not in SKIP and DOMAIN.match(token):
                yield token


def main():
    domains = set()
    for url in SOURCES:
        with urllib.request.urlopen(url, timeout=60) as res:
            found = set(parse(res.read().decode('utf-8', 'replace')))
        print(f'{len(found):>7} {url}')
        domains |= found
    with open(OUT, 'w', encoding='utf-8') as file:
        file.write('\n'.join(sorted(domains)) + '\n')
    print(f'{len(domains):>7} unique -> {os.path.normpath(OUT)}')


if __name__ == '__main__':
    assert list(parse('0.0.0.0 ads.x.com # c\n127.0.0.1 localhost\n::1 ip6-localhost\nplain.org\n# a.com\n')) == ['ads.x.com', 'plain.org']
    main()
