#!/bin/sh -e

TARGET=$1
if [ ! "$TARGET" ]; then
    echo "Usage: $0 file_to_fix"
    exit 1
fi

CURRENT_VERSION=$(latex --version | grep "pdfTeX [0-9]" | cut -d' ' -f2)
MOST_RECENT_VERSION_WITHOUT_ISSUE="3.141592653-2.6-1.40.22"

if [ "$(printf '%s\n%s\n' $MOST_RECENT_VERSION_WITHOUT_ISSUE $CURRENT_VERSION | sort --version-sort | head -1)" != "$CURRENT_VERSION" ]; then
    echo "Version $CURRENT_VERSION requires fixing"
    sed -i "/begin.document./e cat newline-fix.tex" $TARGET
else
    echo "Version $CURRENT_VERSION does not need fixing"
fi