"""Build Tools.<version>.tox. Runs inside a live TouchDesigner, in bundle.toe only.

    exec(open(project.folder + '/scripts/build.py').read())

Run scripts/sync.py first: it puts the tox of every tool into build/ and
writes the versions into tools.json. This script rebuilds /tools from them:

1. every tool already in /tools is switched off (Active) and deleted, so a
   hook it put into /ui goes with it;
2. each tox from build/ is loaded, renamed after the manifest and checked
   against the manifest version;
3. the tools are laid out in one row on the grid, in manifest order;
4. the readme annotation, the changelog DAT and the About page are written;
5. /tools is saved as Tools.<version>.tox and the previous bundle is deleted.

Do not run it in a working project: Promote and the other tools hook into the
interface of the project they are loaded in.
"""
import glob
import json
import math
import os

ROOT = project.folder
GRID = 200         # one cell of the network editor grid
GAP = 50           # free space between two tool tiles, at least
BUNDLE = '/tools'


def _manifest():
    return json.load(open(os.path.join(ROOT, 'tools.json')))


def _clear(bundle):
    """Delete the tools in the bundle. Active goes off first (ui-hook.md)."""
    for child in list(bundle.children):
        if child.name in ('readme', 'changelog'):
            continue
        if child.isCOMP and hasattr(child.par, 'Active'):
            child.par.Active = False
        child.destroy()


def _load(bundle, tool):
    path = os.path.join(ROOT, 'build', '%s.%s.tox' % (tool['tox'], tool['version']))
    if not os.path.isfile(path):
        raise RuntimeError('%s is missing: run scripts/sync.py' % path)
    comp = bundle.loadTox(path)
    comp.name = tool['name']
    got = comp.par.Version.eval() if hasattr(comp.par, 'Version') else None
    if got != tool['version']:
        raise RuntimeError('%s: About says %r, tools.json says %r'
                           % (tool['title'], got, tool['version']))
    return comp


def layout(comps):
    """One row, manifest order, a common step that is a multiple of GRID."""
    widest = max(c.nodeWidth for c in comps)
    step = int(math.ceil((widest + GAP) / float(GRID)) * GRID)
    for i, c in enumerate(comps):
        c.nodeX = i * step
        c.nodeY = 0
    return step


def _readme_text(manifest):
    lines = [
        'All the tools in one component. Each tool works on its own; turn off '
        'its Active to switch it off.',
        '',
    ]
    for t in manifest['tools']:
        lines.append('%s %s  (%s)' % (t['title'], t['version'], t['name']))
        lines.append(t['description'])
        lines.append('')
    lines.append('To update: turn off Active on every tool, delete /tools, '
                 'drop the new Tools tox into the root.')
    return '\n'.join(lines)


def _readme(bundle, manifest, comps):
    note = bundle.op('readme')
    if note is None:
        note = bundle.create(annotateCOMP, 'readme')
        note.name = 'readme'   # its extension renames it on creation
    note.par.Titletext = 'README'
    note.par.Bodytext = _readme_text(manifest)
    # component.md: left edge of the tools, 200 above the top one
    note.nodeX = min(c.nodeX for c in comps)
    note.nodeY = max(max(c.nodeY for c in comps) + 200,
                     max(c.nodeY + c.nodeHeight for c in comps) + GAP)
    # Fit the box to the text, measured with the annotation's own font.
    # Word wrap is on, so a box narrower than a line would break it.
    body = note.op('annotation/body/bodyText')
    w, h = body.evalTextSize(note.par.Bodytext.eval())
    pad = 10
    note.nodeWidth = int(math.ceil(w)) + 2 * pad
    note.nodeHeight = note.par.Titleheight.eval() + int(math.ceil(h)) + 2 * pad
    return note


def _changelog(bundle, note):
    dat = bundle.op('changelog')
    if dat is None:
        dat = bundle.create(textDAT, 'changelog')
    dat.text = open(os.path.join(ROOT, 'CHANGELOG.md')).read()
    dat.color = (0.5, 0.05, 0.05)
    dat.nodeX = note.nodeX - 200
    dat.nodeY = note.nodeY
    return dat


def _about(bundle, version):
    page = next((p for p in bundle.customPages if p.name == 'About'), None)
    if page is None:
        page = bundle.appendCustomPage('About')
    if not hasattr(bundle.par, 'Version'):
        page.appendStr('Version', label='Version')
    if not hasattr(bundle.par, 'Toxsavebuild'):
        page.appendStr('Toxsavebuild', label='.tox Save Build')
    bundle.par.Version = version
    bundle.par.Version.default = version
    bundle.par.Toxsavebuild = app.build
    bundle.par.Toxsavebuild.default = app.build
    for name in ('Version', 'Toxsavebuild'):
        getattr(bundle.par, name).readOnly = True


def build():
    manifest = _manifest()
    version = manifest['version']
    bundle = op(BUNDLE)
    if bundle is None:
        bundle = op('/').create(baseCOMP, 'tools')
    _clear(bundle)
    comps = [_load(bundle, t) for t in manifest['tools']]
    step = layout(comps)
    note = _readme(bundle, manifest, comps)
    _changelog(bundle, note)
    _about(bundle, version)
    bundle.comment = ''
    out = os.path.join(ROOT, 'Tools.%s.tox' % version)
    for old in glob.glob(os.path.join(ROOT, 'Tools.*.tox')):
        if old != out:
            os.remove(old)
    bundle.save(out)
    print('saved %s: %s, step %d'
          % (os.path.basename(out),
             ', '.join('%s %s' % (t['name'], t['version'])
                       for t in manifest['tools']), step))
    return out


RESULT = build()
