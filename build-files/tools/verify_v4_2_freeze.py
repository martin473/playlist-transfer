#!/usr/bin/env python3
"""V4.2 is an implementation freeze.

This package was produced by applying the four corrections recorded in README.md to v4.1.
Future amendments must be attached to a concretely blocked dispatch rather than generating v4.3.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
required=[root/'README.md',root/'manifests/execution-order.json',root/'reference/pi-playlist-bridge-plan-v2.6.md']
missing=[str(p) for p in required if not p.is_file()]
if missing: raise SystemExit('missing v4.2 artifacts: '+', '.join(missing))
print('V4.2 implementation-freeze package present:',root)
