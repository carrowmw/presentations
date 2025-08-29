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

## Notes

- Use a unique local branch name (e.g., `<name>-gh-pages`) to avoid conflicts with any existing `gh-pages`.
- If you prefer a separate repository for the site, add it as a remote (e.g., `git remote add <site> <url>`) and `git push <site> <name>-gh-pages:gh-pages --force`.
- Avoid nested Git repos in `builds/`. If you intended a submodule, manage it via `git submodule`; otherwise remove the nested `.git` folder before committing.
