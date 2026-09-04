# Agent Portability

`harmony-next/SKILL.md` is the source of truth. Host-specific instructions should point agents at that skill directory instead of copying the full rule text.

## Supported Paths

| Host | Current path | Notes |
| --- | --- | --- |
| skills.sh / generic skills CLI | `npx skills add linhay/harmony-next.skills` | Recommended default. Installs the repository's single `harmony-next` skill. |
| Gemini CLI | `gemini skills install https://github.com/linhay/harmony-next.skills --path harmony-next --scope user` | Loads the skill directory directly. |
| Claude Code | `npx skills add linhay/harmony-next.skills --skill harmony-next -a claude-code -g -y --copy` | Use `--copy` for non-interactive global installs. |
| Claude.ai | release artifact `harmony-next.skill.zip` | Upload the packaged skill artifact when a file upload flow is needed. |
| Codex | `npx skills add linhay/harmony-next.skills --skill harmony-next -a codex -g -y --copy` | Current distribution is a skill install, not a Codex plugin. |
| Codex manual install | `$REPO_ROOT/.agents/skills/harmony-next`, `$HOME/.agents/skills/harmony-next`, or `/etc/codex/skills/harmony-next` | Copy or symlink the `harmony-next/` directory. |
| Generic project instructions | repository `AGENTS.md` plus `harmony-next/SKILL.md` | `AGENTS.md` stays small; the skill contains the HarmonyOS routing rules. |

## Adapter Rule

Keep adapters thin:

- Put behavior and routing in `harmony-next/SKILL.md`.
- Put user-facing installation instructions in `README.md` and `README_en.md`.
- Put host support notes here.
- Use `harmony-next/scripts/check_packaging_docs.py` to catch version, command, and path drift.

## Out Of Scope

This repository is a reference and automation skill pack, not an always-on behavior mode. Do not add lifecycle hooks, status lines, mode trackers, or per-host copied rule files unless a concrete host integration requires them.
