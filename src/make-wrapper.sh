#!/bin/bash -e

program=$1
shift
#files=$@

wrapper=`dirname $0`/gzip-wrapper.sh
tmp="/tmp/`basename $0`-$$"
tgz="$tmp.tgz"
out="$tmp.out"
csf="$tmp.csf"

tar czvf "$tgz" "$program" "$@" >&2
{ cat "$tgz" "$wrapper"; date; hostname; } > "$csf"
sha=`sha1sum "$csf" | awk '{print $1}'`

cat `dirname $0`/gzip-wrapper.sh | \
    sed -e "s/__PROGNAME__/$program/1" \
	-e "s/__SHA1__/$sha/1" \
    > "$out"
cat "$tgz" >> "$out"
cat "$out"
rm -f "$tgz" "$out" "$csf"
