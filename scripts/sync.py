#!/usr/bin/env python3
"""Bring the manifest and the README table up to the latest tool releases.

    python3 scripts/sync.py            download the latest release of every tool
                                       into build/, write its version to
                                       tools.json, regenerate the README table
    python3 scripts/sync.py --check    change nothing; list tools whose latest
                                       release is newer than tools.json, exit 1
                                       if there are any

The GitHub Release of each tool is the only source. Needs the gh CLI.
After a sync, build the bundle in bundle.toe (scripts/build.py).
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'tools.json')
README = os.path.join(ROOT, 'README.md')
BUILD = os.path.join(ROOT, 'build')
START, END = '<!-- tools:start -->', '<!-- tools:end -->'


def gh(*args):
    return subprocess.run(['gh', *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def latest(repo):
    tag = gh('release', 'view', '--repo', repo, '--json', 'tagName',
             '--jq', '.tagName')
    return tag[1:] if tag.startswith('v') else tag


def download(tool, version):
    os.makedirs(BUILD, exist_ok=True)
    for old in glob.glob(os.path.join(BUILD, tool['tox'] + '.*.tox')):
        os.remove(old)
    gh('release', 'download', 'v' + version, '--repo', tool['repo'],
       '--pattern', '%s.%s.tox' % (tool['tox'], version), '--dir', BUILD)


def table(manifest):
    rows = ['| Tool | Version | What it does | Path |',
            '| --- | --- | --- | --- |']
    for t in manifest['tools']:
        url = 'https://github.com/' + t['repo']
        rows.append('| [%s](%s) | [%s](%s/releases/tag/v%s) | %s | `/tools/%s` |' % (
            t['title'].replace(' ', '&nbsp;'), url, t['version'], url,
            t['version'], t['description'], t['name']))
    return '\n'.join(rows)


def write_table(manifest):
    text = open(README).read()
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    open(README, 'w').write(
        head + START + '\n' + table(manifest) + '\n' + END + tail)


def main():
    check = '--check' in sys.argv[1:]
    manifest = json.load(open(MANIFEST))
    stale = []
    for t in manifest['tools']:
        new = latest(t['repo'])
        if new != t['version']:
            stale.append((t['title'], t['version'], new))
        if not check:
            download(t, new)
            t['version'] = new
    for title, old, new in stale:
        print('%s: %s -> %s' % (title, old, new))
    if check:
        return 1 if stale else 0
    with open(MANIFEST, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')
    write_table(manifest)
    print('build/:', ', '.join(sorted(os.listdir(BUILD))))
    if stale:
        print('Bump the bundle version in tools.json, then run scripts/build.py '
              'in bundle.toe.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
