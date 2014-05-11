#!/usr/bin/env python

"""
Minimalistic tool to check multiple parcels in PP Emonitoring at a time.
"""

import monitoring
import sys

for n in sys.argv[1:]:
    try:
        p = monitoring.Parcel(n)
        print '[%20s] %s @ %s / %s' % (n, p.events[-1]['description'], p.events[-1]['time'], p.events[-1]['location'])
    except Exception as exc:
        print >>sys.stderr, '[%s] Failed: %s' % (n, sys.exc_info()[1])
