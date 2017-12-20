#!/bin/bash
"$PY" gh.py gists obfusk \
  | jq '[.[]|select(.desc|contains("pry"))]'
