# Using interface-craft with Gemini CLI

The repository is also a [Gemini CLI extension](https://geminicli.com/docs/extensions/). Gemini auto-discovers the `skills/` folder bundled with the extension; the skill file is the same one Claude Code and Codex read.

## Install

```bash
gemini extensions install https://github.com/harun-yardimci/interface-craft
```

A local clone works too: `gemini extensions install /path/to/interface-craft`. Restart Gemini CLI if it is already running.

## Setup for the render audit

```bash
cd ~/.gemini/extensions/interface-craft/skills/interface-craft/scripts && npm install
```

The theme, token and hit-area audits need no setup.

## Usage

Describe the task ("review this screen", "check dark mode", "make this onboarding better") and the skill activates when the request matches its description.

## Workspace mode

Running Gemini CLI from inside a clone of this repository loads the skill as a workspace skill through the `.gemini/skills` symlink, without a global install.

## How it works

- `gemini-extension.json`: the extension manifest at the repository root.
- `.gemini/skills`: a git-tracked symlink to `../skills` for workspace mode. On Windows, replace it with a copy after cloning (`rm .gemini/skills && cp -R skills .gemini/skills`) and keep that change local.
