#!/usr/bin/python3

import json, requests, sys
from collections import OrderedDict

API         = "https://api.github.com"
REPOS       = "/users/{}/repos"
GISTS       = "/users/{}/gists"

gist_fields = "html_url description".split()
repo_fields = "name description html_url".split()
rename      = dict(zip("description html_url".split(),
                       "desc        link    ".split()))

def get_paginated(url, verbose = False):
  data = []
  while url:
    if verbose: print("==>", url, file = sys.stderr)
    resp  = requests.get(url)
    url   = resp.links.get("next", {}).get("url")
    data.extend(resp.json())
  return data

def select(data, keys, rename = {}):
  data_ = ( OrderedDict( (rename.get(k, k), x[k]) for k in keys )
            for x in data )
  return sorted(data_, key = lambda x: tuple(x.values()))

def get_repos(user, verbose = False):
  return get_paginated(API + REPOS.format(user), verbose)

def get_gists(user, verbose = False):
  return get_paginated(API + GISTS.format(user), verbose)

def repos(users, verbose = False):
  return select(
    ( x for user in users for x in get_repos(user, verbose) ),
    repo_fields, rename)

def gists(users, verbose = False):
  return select(
    ( x for user in users for x in get_gists(user, verbose) ),
    gist_fields, rename)

COMMANDS = "gists repos".split()

if __name__ == "__main__":
  if len(sys.argv) < 3 or sys.argv[1] not in COMMANDS:
    print("Usage: gh.py {{ {} }} USERNAME..."
          .format(" | ".join(COMMANDS)), file = sys.stderr)
    sys.exit(1)
  d = globals()[sys.argv[1]](sys.argv[2:], verbose = True)
  print(json.dumps(d, indent = 2))  # sorted -> no sort_keys = True
