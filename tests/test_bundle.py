"""The bundle holds exactly the tools of the manifest, at their versions."""
import os

GRID = 200


def test_tools_match_manifest(t):
    for tool, comp in zip(t.tools, t.comps()):
        t.true(comp is not None, 'no /tools/%s' % tool['name'])
        t.eq(comp.par.Version.eval(), tool['version'], tool['name'] + ' Version')


def test_nothing_else_inside(t):
    want = {x['name'] for x in t.tools} | {'readme', 'changelog'}
    t.eq({c.name for c in t.bundle.children}, want, 'children of /tools')


def test_every_tool_is_active(t):
    for comp in t.comps():
        t.true(comp.par.Active.eval(), comp.name + ' Active is off')


def test_about(t):
    version = t.manifest['version']
    t.eq(t.bundle.customPages[-1].name, 'About', 'last page')
    t.eq(t.bundle.par.Version.eval(), version, 'Version')
    t.eq(t.bundle.par.Version.default, version, 'Version default')
    t.eq(t.bundle.par.Toxsavebuild.eval(), t.bundle.par.Toxsavebuild.default,
         'Toxsavebuild value and default')
    t.true(os.path.isfile(project.folder + '/Tools.%s.tox' % version),
           'Tools.%s.tox is missing' % version)


def test_changelog_matches_file(t):
    text = open(project.folder + '/CHANGELOG.md').read()
    t.eq(t.bundle.op('changelog').text, text, 'changelog DAT')


def test_readme_lists_every_tool(t):
    body = t.bundle.op('readme').par.Bodytext.eval()
    for tool in t.tools:
        t.true('%s %s' % (tool['title'], tool['version']) in body,
               'readme does not list %s %s' % (tool['title'], tool['version']))


def test_layout_one_row_on_the_grid(t):
    comps = t.comps()
    t.eq({c.nodeY for c in comps}, {0}, 'nodeY')
    xs = [c.nodeX for c in comps]
    t.eq(xs[0], 0, 'first nodeX')
    steps = {b - a for a, b in zip(xs, xs[1:])}
    t.eq(len(steps) <= 1, True, 'one step between tools: %s' % xs)
    for s in steps:
        t.true(s > 0 and s % GRID == 0, 'step %d is not a positive multiple of %d'
               % (s, GRID))


def test_layout_no_overlap(t):
    boxes = [(o.name, o.nodeX, o.nodeY, o.nodeX + o.nodeWidth,
              o.nodeY + o.nodeHeight)
             for o in t.bundle.children if o.name != 'readme']
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            apart = a[3] <= b[1] or b[3] <= a[1] or a[4] <= b[2] or b[4] <= a[2]
            t.true(apart, '%s overlaps %s' % (a[0], b[0]))
