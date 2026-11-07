# Using interface-craft with Codex

The repository is also a [Codex plugin](https://developers.openai.com/codex/plugins/build). Codex reads the same `skills/interface-craft` folder that Claude Code uses; nothing is copied.

## Install

```bash
codex plugin marketplace add harun-yardimci/interface-craft
```

Requires Codex CLI v0.122 or later (older releases used `codex marketplace add`). A local clone works too: `codex plugin marketplace add /path/to/interface-craft`. Restart Codex if it is already running.

Manual alternative, without the plugin system:

```bash
git clone https://github.com/harun-yardimci/interface-craft.git
cp -R interface-craft/skills/interface-craft ~/.agents/skills/
```

## Setup for the render audit

The theme, token and hit-area audits need only Python 3. The render audit needs its dependency once:

```bash
cd ~/.codex/plugins/cache/interface-craft/interface-craft/*/skills/interface-craft/scripts && npm install
```

Codex caches plugins under `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`; adjust the path for a manual install. It drives the Chrome or Edge already on the machine; nothing is downloaded.

## Usage

Invoke it with `$interface-craft` or `@interface-craft`, or describe the task ("review this checkout flow", "the cards have different heights") and let Codex pick the skill. `agents/openai.yaml` provides the display name and default prompt in the Codex UI.

## How it works

- `.codex-plugin/plugin.json` at the repository root: the Codex plugin manifest; `skills` points at `./skills/`, the same folder Claude Code reads.
- `.agents/plugins/marketplace.json`: the marketplace entry. Its `source.path` is `./`, so the repository root is the plugin root, and `installation` is `INSTALLED_BY_DEFAULT`, so `codex plugin marketplace add` installs the plugin in one step. If it is listed but not active, run `codex plugin add interface-craft@interface-craft` or use `/plugins` in Codex.

No symlinks are involved, so the layout works the same on Windows.
