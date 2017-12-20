#!/usr/bin/python3

import json, requests, sys
from collections import OrderedDict

API         = "https://api.github.com"
REPOS       = "/users/{}/repos"
GISTS       = "/users/{}/gists"

user        = "obfusk"

gist_fields = "description html_url".split()
repo_fields = ["name"] + gist_fields
rename      = dict(zip("description html_url".split(),
                       "desc        link    ".split()))

def get_paginated(url):
  data = []
  while url:
    print("==>", url, file = sys.stderr)
    resp  = requests.get(url)
    url   = resp.links.get("next", {}).get("url")
    data.extend(resp.json())
  return data

def select(data, keys, rename = {}):
  data_ = ( OrderedDict( (rename.get(k, k), x[k]) for k in keys )
            for x in data )
  return sorted(data_, key = lambda x: tuple(x.values()))

def repos(user):
  return select(get_paginated(API + REPOS.format(user)),
                repo_fields, rename)

def gists(user):
  return select(get_paginated(API + GISTS.format(user)),
                gist_fields, rename)

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    if sys.argv[1] not in "gists repos".split(): sys.exit(1)
    u = sys.argv[2] if len(sys.argv) >= 3 else user
    d = globals()[sys.argv[1]](u)
    print(json.dumps(d, indent = 2)) # sort_keys = True
