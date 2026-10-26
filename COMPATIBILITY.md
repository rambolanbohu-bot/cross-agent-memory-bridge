# Compatibility / 兼容矩阵
| Platform | Skill discovery | Real execution | Snapshot reading | Snapshot update | Conclusion |
|---|---|---|---|---|---|
| Codex Windows | Historical native host PASS | Current real chat explicit load, 26 CLI calls | Local verify PASS | Local approved workflow PASS | Separate evidence; not one automatic fresh-model workflow |
| ChatGPT | NOT_TESTED | NOT_TESTED | Manual snapshot if supported; NOT_TESTED | NOT_TESTED | No native claim |
| Claude | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | Not verified |
| Gemini | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | Not verified |
| Muse | Permission-blocked | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| Linux/macOS | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED |

Windows evidence: Python 3.12.10. Python 3.11 syntax checked, not locally executed. Original suite: 33 tests, 32 passed, one real junction skipped; remote Windows/Ubuntu CI NOT_RUN. Independent native-host model call failed 401; not retried here. Script roles A/B are simulations only.

Documented project locations: Codex .agents/skills/<name>; Claude Code .claude/skills/<name>; Gemini CLI .gemini/skills/<name> or .agents/skills/<name>. These are documentation references, not execution tests. Verify current host support/permissions. Ordinary chat may support only manual Markdown snapshots. Refresh by new reviewed export; no private GitHub connector is assumed. Export target labels are not proprietary adapters.
Sources: https://learn.chatgpt.com/docs/build-skills ; https://code.claude.com/docs/en/skills ; https://geminicli.com/docs/cli/skills/ .
