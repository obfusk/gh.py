SHELL   := bash
PY      ?= python3

export PY

.PHONY: test

test:
	diff -Naur <( test/repos.sh     ) test/repos.out
	diff -Naur <( test/gists.sh     ) test/gists.out
	diff -Naur <( test/contribs.sh  ) test/contribs.out
	diff -Naur <( test/repo_info.sh ) test/repo_info.out
