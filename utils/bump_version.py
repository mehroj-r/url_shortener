# Increment the patch version in the VERSION file (auto-increment script)

version_file = 'VERSION'

with open(version_file, 'r') as f:
    version = f.read().strip()

major, minor, patch = map(int, version.split('.'))
patch += 1

with open(version_file, 'w') as f:
    f.write(f'{major}.{minor}.{patch}')