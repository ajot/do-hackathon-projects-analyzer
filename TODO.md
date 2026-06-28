# TODO

## Bugs / tech debt

- [ ] **`fetcher.py` fix is not version-controlled.** `fetcher.py` is gitignored, so the repo-name truncation fix (replacing `rstrip(".git")` with an explicit `endswith(".git")` slice) only exists on the local machine. If this project is rebuilt from the repo alone, the bug returns: `rstrip(".git")` strips any trailing `{. g i t}` characters, mangling names like `bonsai`→`bonsa`, `gambit`→`gamb`, `omnicon-rsi`→`omnicon-rs`. Decide whether to un-ignore `fetcher.py` or document the fix in the README.

## Follow-ups

- [ ] Re-fetch and re-analyze if any of the 2 still-empty repos go public (#1 test entry, #69 voice-bridge — both 404 at last check).
- [ ] `fetcher.py` caps at 15 source files / 8000 chars per file — a DO call buried deeper could be missed on borderline repos.
