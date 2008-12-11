#!/bin/bash

git describe 2>/dev/null | grep -qE . || exit 1
ver=`git describe`

git update-index -q --refresh
test -z "$(git diff-index --name-only HEAD --)" || ver="$ver-dirty"
ver=$(echo "$ver" | sed -e 's/-/./g' | sed -e 's/^v//');
echo $ver
