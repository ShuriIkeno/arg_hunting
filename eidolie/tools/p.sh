#!/bin/bash
# run play.py and show only the in-game page content (not desktop chrome / address bar)
python "$(dirname "$0")/play.py" "$@" | awk '/^RESULT/{print} /^--- frame: .*app\/[a-z_0-9]+(\.html)?/{if($0 !~ /console.html/){on=1}} on'
