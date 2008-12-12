#!/bin/bash
die() { echo "$0: $@" >&2; exit 1; }
program=__PROGNAME__
dir=/tmp/.wrap.__SHA1__.`whoami`.`hostname`
if ! test -d $dir; then
    rm -rf $dir || die "Can't remove $dir"
    mkdir $dir || die "Can't create $dir/"
    cat $0 | { while :; do read -r l || die "Read failed"; [ "$l" = "EOF" ] && break; done; cat; } | tar zxf - -C $dir || die "Unpacking failed"
fi
exec $dir/$program "$@"
EOF
