#!/usr/bin/env bash

# bump_version.sh (assessment|project|templates|tools) (show|major|minor|patch|prerelease|build)

set -o nounset
set -o errexit
set -o pipefail

HELP_INFORMATION="bump_version.sh (assessment|project|templates|tools) (show|major|minor|patch|prerelease|build|finalize)"

if [ $# -ne 2 ]
then
   echo "$HELP_INFORMATION"
else
    case $1 in
        project)
            VERSION_FILE=src/_version.py
            old_version=$(sed -n "s/^__version__ = \"\(.*\)\"$/\1/p" "$VERSION_FILE")
          ;;
        assessment|templates|tools)
            VERSION_FILE=src/$1/_version.py
            old_version=$(sed -n "s/^__version__ = \"\(.*\)\"$/\1/p" "$VERSION_FILE")
            ;;
        *)
            echo "$HELP_INFORMATION"
            exit
            ;;
    esac
    case $2 in
        major|minor|patch|prerelease|build)
            new_version=$(python -c "import semver; print(semver.bump_$2('$old_version'))")
            echo Changing version from "$old_version" to "$new_version"
            # A temp file is used to provide compatability with macOS development
            # as a result of macOS using the BSD version of sed
            tmp_file=/tmp/version.$$
            sed "s/$old_version/$new_version/" "$VERSION_FILE" > $tmp_file
            mv "$tmp_file" "$VERSION_FILE"
            git add "$VERSION_FILE"
            git commit -m"Bump version from $old_version to $new_version"
            git push
            ;;
        finalize)
            new_version=$(python -c "import semver; print(semver.finalize_version('$old_version'))")
            echo Changing version from "$old_version" to "$new_version"
            # A temp file is used to provide compatability with macOS development
            # as a result of macOS using the BSD version of sed
            tmp_file=/tmp/version.$$
            sed "s/$old_version/$new_version/" "$VERSION_FILE" > $tmp_file
            mv "$tmp_file" "$VERSION_FILE"
            git add "$VERSION_FILE"
            git commit -m"Bump version from $old_version to $new_version"
            git push
            ;;
        show)
            echo "$old_version"
            ;;
        *)
            echo "$HELP_INFORMATION"
            ;;
    esac
fi
