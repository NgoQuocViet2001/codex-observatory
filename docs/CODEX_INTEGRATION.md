# Codex Integration

## What Happens on npm Install

When you run:

```bash
npm install -g codex-observatory
```

Codex Observatory tries to do the equivalent of:

```bash
codex-observatory install-codex --patch-codex
```

That setup step:

- installs helper tools under `~/.codex/tools`
- installs the Codex Observatory skill under `~/.codex/skills`
- patches the local `codex` launcher so `codex stats` and `codex stat` work directly
- stores launcher backups under `~/.codex/integrations/codex-observatory/backups`

## Manual Repair

If the automatic setup was skipped or failed, run this once:

```bash
codex-observatory install-codex --patch-codex
```

## Clean Removal

To undo the launcher patch and remove the Codex-side integration files:

```bash
codex-observatory uninstall-codex
```

Then remove the npm package:

```bash
npm uninstall -g codex-observatory
```

## Notes

- `codex stats` is the recommended user-facing command.
- `codex-observatory` and `codex-stats` remain available as direct aliases.
- Only `stats` and `stat` are intercepted.
- Other Codex commands continue to run normally.
