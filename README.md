# td-tools

TouchDesigner tools in one component.

Each tool has its own repository with its source, tests and releases. This repository collects their releases into `Tools.*.tox`, one component that holds them all.

## Tools

<!-- tools:start -->
| Tool | Version | What it does | Path |
| --- | --- | --- | --- |
| [Menu&nbsp;Step](https://github.com/ktnkv/td-par-menu-step) | [0.1.0](https://github.com/ktnkv/td-par-menu-step/releases/tag/v0.1.0) | Steps through a menu parameter with the arrow keys. | `/tools/menustep` |
| [Promote](https://github.com/ktnkv/td-par-promoter) | [0.6.4](https://github.com/ktnkv/td-par-promoter/releases/tag/v0.6.4) | Lifts a parameter up through its ancestor COMPs in one drag. | `/tools/promote` |
| [Size&nbsp;Guard](https://github.com/ktnkv/td-op-size-guard) | [0.1.2](https://github.com/ktnkv/td-op-size-guard/releases/tag/v0.1.2) | Keeps every operator tile in the network editor at one size. | `/tools/sizeguard` |
<!-- tools:end -->

## Install

1. Download `Tools.*.tox` from the [latest release](https://github.com/ktnkv/td-tools/releases/latest).
2. Drop it into the root of your project. It becomes `/tools`, with every tool inside at the path in the table.

Each tool works on its own. To switch one off, turn off its **Active**. To use only some of the tools, take their tox files from the same release or from the tool's own repository and drop them into `/tools`.

### Update

1. Turn off **Active** on every tool in `/tools`. Promote removes its hook from the TouchDesigner interface only when it is turned off.
2. Delete `/tools`.
3. Drop the new `Tools.*.tox` into the root.

The tools come back with their default settings, so note the ones you changed, for example **Size** in Size Guard. The changes the tools made to the project stay: they are ordinary parameters, binds and tile sizes.

## License

[MIT](LICENSE)
