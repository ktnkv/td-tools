"""Bundle test runner. Runs inside a live TouchDesigner, in bundle.toe.

    exec(open(project.folder + '/tests/run_tests.py').read())

Each tests/test_*.py defines test_* functions that take one argument, `t`:
the bundle COMP, the manifest and a few asserts. The tests only read the
bundle; nothing is created or removed.
Set ONLY to a substring to run matching tests: ONLY = 'layout'.
"""
import glob
import json
import os
import traceback

BUNDLE = '/tools'


class Harness:
    def __init__(self, bundle):
        self.bundle = bundle
        self.manifest = json.load(open(project.folder + '/tools.json'))
        self.tools = self.manifest['tools']

    def comps(self):
        """The tool COMPs in manifest order, None for a missing one."""
        return [self.bundle.op(t['name']) for t in self.tools]

    def eq(self, got, want, what=''):
        assert got == want, '%s: got %r, want %r' % (what or 'value', got, want)

    def true(self, cond, what):
        assert cond, what


def _load(path):
    ns = dict(globals())
    exec(compile(open(path).read(), path, 'exec'), ns)
    return [(os.path.basename(path)[:-3] + '.' + k, v)
            for k, v in ns.items() if k.startswith('test_') and callable(v)]


def run():
    bundle = op(BUNDLE)
    if bundle is None:
        raise RuntimeError('%s not found: run scripts/build.py' % BUNDLE)
    t = Harness(bundle)
    only = globals().get('ONLY')
    tests = []
    for path in sorted(glob.glob(project.folder + '/tests/test_*.py')):
        tests += _load(path)
    if only:
        tests = [x for x in tests if only in x[0]]
    passed, failed = 0, []
    for name, fn in tests:
        try:
            fn(t)
            passed += 1
        except Exception:
            failed.append((name, traceback.format_exc(limit=4)))
    for name, tb in failed:
        print('FAIL', name)
        print(tb)
    print('%d passed, %d failed (%d tests)' % (passed, len(failed), len(tests)))
    return not failed


RESULT = run()
