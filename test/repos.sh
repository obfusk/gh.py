#!/bin/bash
"$PY" gh.py repos obfusk \
  | jq '[.[]|select(.name|startswith("obfusk"))]'
