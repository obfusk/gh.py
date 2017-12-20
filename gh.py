#!/usr/bin/python3

import json, requests, sys
from collections import OrderedDict, defaultdict

GH                = "https://github.com"
API               = "https://api.github.com"

REPOS             = "/users/{}/repos"
GISTS             = "/users/{}/gists"
ISSUES            = "/search/issues?q=author:{}"
REPO              = "/repos/{}"

repo_fields       = "name description html_url".split()
gist_fields       = "html_url description".split()
contrib_fields    = "name count contrib".split()
repo_info_fields  = "full_name description html_url".split()
rename            = dict(zip("description html_url full_name".split(),
                             "desc        link     name     ".split()))

def get(url, verbose = False):
  if verbose: print("==>", url, file = sys.stderr)
  resp = requests.get(url); resp.raise_for_status()
  return resp

def get_paginated(url, verbose = False):
  while url:
    resp  = get(url, verbose); json = resp.json()
    url   = resp.links.get("next", {}).get("url")
    for x in json if isinstance(json, list) else json["items"]:
      yield x

def renamed(x, keys, rename):
  return OrderedDict( (rename.get(k, k), x[k]) for k in keys )

def select(data, keys, rename = {}):
  return sorted(( renamed(x, keys, rename) for x in data ),
                key = lambda x: tuple(x.values()))

def get_repos(user, verbose = False):
  return get_paginated(API + REPOS.format(user), verbose)

def get_gists(user, verbose = False):
  return get_paginated(API + GISTS.format(user), verbose)

def get_contribs(user, verbose = False):
  contribs = defaultdict(lambda: dict(count = 0, contrib = False))
  for issue in get_paginated(API + ISSUES.format(user), verbose):
    name = issue["repository_url"].replace(API + REPO.format(""), "")
    if name.startswith(user + "/"): continue
    contribs[name]["count"] += 1
    if issue["author_association"] in "CONTRIBUTOR OWNER".split():
      contribs[name]["contrib"] = True
  return [ dict(name = k, **v) for k,v in contribs.items() ]

def get_repo_info(repo, verbose = False):
  return get(API + REPO.format(repo), verbose).json()

def repos(users, verbose = False):
  return select(
    ( x for user in users for x in get_repos(user, verbose) ),
    repo_fields, rename)

def gists(users, verbose = False):
  return select(
    ( x for user in users for x in get_gists(user, verbose) ),
    gist_fields, rename)

def contribs(users, verbose = False):
  return select(
    ( x for user in users for x in get_contribs(user, verbose) ),
    contrib_fields, rename)

def repo_info(repos, verbose = False):
  return select(
    ( get_repo_info(repo, verbose) for repo in repos ),
    repo_info_fields, rename)

COMMANDS = "gists repos contribs repo_info".split()

if __name__ == "__main__":
  if len(sys.argv) < 3 or sys.argv[1] not in COMMANDS:
    print("Usage: gh.py {{ {} }} USERNAME..."
          .format(" | ".join(COMMANDS)), file = sys.stderr)
    sys.exit(1)
  try:
    d = globals()[sys.argv[1]](sys.argv[2:], verbose = True)
  except requests.exceptions.HTTPError as e:
    print(e, file = sys.stderr); sys.exit(1)
  print(json.dumps(d, indent = 2))  # sorted -> no sort_keys = True
