# Resolving Merge Conflicts in Adaptive English Level Test

When GitHub reports merge conflicts for this project, use the command line to resolve them locally where you can run tests and verify the result.

## 1. Update the local repository

Fetch the latest changes from the base branch (usually `main`) and ensure your feature branch starts from the newest commit:

```bash
git fetch origin
git checkout <your-feature-branch>
git merge origin/main
```

If the base branch is named differently, adjust the commands accordingly.

## 2. Inspect conflicted files

Git marks conflicted files with `<<<<<<<`, `=======`, and `>>>>>>>` sections. List the files to review:

```bash
git status
```

Open each listed file (for example `app/cat_engine.py`, `app/item_bank.py`, `app/main.py`, `requirements.txt`, `tests/test_api_flow.py`) and decide which pieces to keep. Often you need to combine logic from both sides instead of choosing one block entirely.

### Example: `DOMAIN_TARGETS` conflict in `app/cat_engine.py`

If you encounter a block like the screenshot below while merging:

```
<<<<<<< HEAD
DOMAIN_TARGETS = {part: 10 for part in CAT_PARTS}
=======
DOMAIN_TARGETS = {...}  # numbers inlined per section
>>>>>>> main
```

Choose the version that keeps the dictionary comprehension (`Accept Current Change` in VS Code). The comprehension ensures every entry in `CAT_PARTS` automatically receives the same target count, so adding a new section in the future does not require touching two separate places. After picking that side, delete the conflict markers and save the file before continuing with the rest of the resolution steps.

## 3. Edit and test

After editing a file, remove the conflict markers and make sure the result compiles. When all conflicts are fixed:

```bash
git add <file>
```

Run the automated suite to confirm nothing broke:

```bash
pytest
```

## 4. Finalize the merge

If tests pass, complete the merge locally:

```bash
git commit
```

Finally push the resolved branch back to GitHub:

```bash
git push origin <your-feature-branch>
```

The pull request will update automatically, showing the conflicts are resolved. If new conflicts appear later, repeat these steps.
