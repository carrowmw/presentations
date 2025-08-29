# Deploying a build/ subfolder to GitHub Pages

This guide explains how to:

- create a presentation build with `create_build.py` into `builds/<name>_build`, and
- publish that subfolder to GitHub Pages using `git subtree`.

## Prerequisites

- Python 3 available as `python3`
- Git installed
- (Recommended) Git LFS installed if your build includes large binaries: https://git-lfs.github.com

## 1) Create the build

Run the project’s build script. Replace `<name>` with your presentation key (e.g., `ap2`).

```bash
python3 create_build.py --name <name>
# Result: builds/<name>_build/ with index.html and assets
```

Verify the build exists:

```bash
ls -la builds/<name>_build
```

## 2) Commit your changes to main

```bash
git add .
git commit -m "Build <name> for deployment"
git push origin main
```

If you see “Large files detected” when pushing, move those assets to Git LFS and retry:

```bash
git lfs install
git lfs track "**/*.json"   # or track specific large paths
git add .gitattributes
git commit -m "Track large assets with LFS"
# If the large file was already committed, rewrite history:
git lfs migrate import --include="**/*.json" --include-ref=refs/heads/main
git push origin main --force-with-lease
```

If Git warns about “embedded git repository” inside builds/, remove the nested .git folder and re-add:

```bash
git rm --cached -r builds/<name>_build
rm -rf builds/<name>_build/.git
git add builds/<name>_build
git commit -m "Convert <name>_build from submodule to regular folder"
git push origin main
```

## 3) Create a Pages branch from the build folder

Use `git subtree split` from the repo root. This produces a branch whose root is your build folder.

```bash
# Optional: remove a conflicting local gh-pages
git branch -D gh-pages 2>/dev/null || true

# Create a split branch with only the build contents
git subtree split --prefix=builds/<name>_build -b <name>-gh-pages
```

## 4) Publish to GitHub Pages (same repository)

Push the split branch to the repo’s gh-pages branch:

```bash
git push origin <name>-gh-pages:gh-pages --force
```

Then in GitHub:

- Settings → Pages → Build and deployment: “Deploy from a branch”
- Branch: `gh-pages`, Folder: `/ (root)`
- Save. Pages will deploy in ~1–2 minutes.

Your site will be at:

```
https://<your-username>.github.io/<this-repo>/
```

## 5) Update the site after changes

After editing slides and re-running the build:

```bash
python3 create_build.py --name <name>
git add .
git commit -m "Update <name> build"
git push origin main

# Recreate and push the split
git branch -D <name>-gh-pages 2>/dev/null || true
git subtree split --prefix=builds/<name>_build -b <name>-gh-pages
git push origin <name>-gh-pages:gh-pages --force
```

## Host multiple builds under one GitHub Pages site

You can persist many presentations by publishing each build into a subfolder of the `gh-pages` branch using a worktree.

Note: `../presentations-pages` is just a local folder that holds a checkout of the `gh-pages` branch of this same repository. It is not a separate GitHub repository. Pushes from this worktree go to `origin gh-pages` on the current repo.

One-time setup:
```bash
git fetch origin
# Create/update a gh-pages worktree into ../presentations-pages
if git ls-remote --exit-code --heads origin gh-pages >/dev/null 2>&1; then
  git worktree add -B gh-pages ../presentations-pages origin/gh-pages
else
  git worktree add -B gh-pages ../presentations-pages
fi

cd ../presentations-pages
git rm -r . 2>/dev/null || true
git clean -fdx

# Use a single-quoted heredoc to avoid '!' expansion in zsh
cat > index.html <<'HTML'
<!doctype html><meta charset="utf-8"><title>Presentations</title>
<h1>Presentations</h1>
<ul></ul>
HTML

git add -A && git commit -m "Initialize gh-pages for multi-build hosting" || true
git push -u origin gh-pages
```

Publish builds:
```bash
# From repo root
rsync -av --delete --exclude '.git*' builds/<name>_build/ ../presentations-pages/<name>/
cd ../presentations-pages && git add -A && git commit -m "Publish <name>" && git push origin gh-pages
```

Helper script:
```bash
./scripts/publish-build.sh <name> [<build-path>]
# e.g.
./scripts/publish-build.sh ap2 builds/ap2_build
./scripts/publish-build.sh cupum builds/cupum_build
```

Your links will be:
```
https://<your-username>.github.io/<this-repo>/<name>/
```

Notes:
- If a build folder is a submodule, initialize it before publishing:
  `git submodule update --init --recursive builds/<name>_build`
- Keep using `create_build.py` to regenerate builds, then re-run the publish script.

## Notes

- Use a unique local branch name (e.g., `<name>-gh-pages`) to avoid conflicts with any existing `gh-pages`.
- If you prefer a separate repository for the site, add it as a remote (e.g., `git remote add <site> <url>`) and `git push <site> <name>-gh-pages:gh-pages --force`.
- Avoid nested Git repos in `builds/`. If you intended a submodule, manage it via `git submodule`; otherwise remove the nested `.git` folder before committing.
