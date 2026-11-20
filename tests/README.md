# Tests

The tests run inside a live TouchDesigner, in `bundle.toe`, after `scripts/build.py`. Run the whole folder from the Textport:

```python
exec(open(project.folder + '/tests/run_tests.py').read())
```

Set `ONLY = 'layout'` before the line to run only the tests whose name contains it. The tests only read `/tools`; they create and delete nothing.

`test_bundle.py`:

- `/tools` holds exactly the tools of `tools.json`, under their names and at their versions, plus `readme` and `changelog`;
- every tool is shipped with **Active** on;
- About is the last page, its `Version` is the bundle version, and `Tools.<version>.tox` exists;
- the `changelog` DAT matches `CHANGELOG.md`, the `readme` annotation lists every tool with its version;
- the tools stand in one row in manifest order, at `nodeY` 0, with one step that is a multiple of the 200-unit grid, and no two tiles overlap.

The tests of each tool live in that tool's repository.
