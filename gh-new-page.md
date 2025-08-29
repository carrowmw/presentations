# Build and publish (minimal)

Assuming setup is done and gh-pages worktree exists:

```bash
# Build
python3 create_build.py --name <name>
# or explicit source/output:
# python3 create_build.py <path/to/index.html> builds/<name>_build

# Publish
./scripts/publish-build.sh <name> builds/<name>_build
```

URLs:
- https://carrowmw.github.io/presentations/<name>/