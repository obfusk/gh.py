#!/bin/bash
"$PY" gh.py contribs obfusk \
  | jq '[.[]|select(.name|contains("bun"))]'
