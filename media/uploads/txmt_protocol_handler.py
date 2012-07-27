#! /usr/bin/env python
import sys
import re
import os
import urllib

filename = urllib.unquote(re.compile('file://(.+)').search(sys.argv[1]).group(1))
line = re.compile('line=(\d+)').search(sys.argv[1]).group(1)
os.system('xterm -e vim +%s "%s"' % (line, filename))
