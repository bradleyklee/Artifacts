#!/usr/bin/env python3
"""Tiny JSON assertion helper used by the Makefile."""
import argparse, json, sys
from pathlib import Path


def get(obj, path):
    cur = obj
    for part in path.split('.'):
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def coerce(s):
    try:
        return json.loads(s)
    except Exception:
        return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('json_file')
    ap.add_argument('--eq', action='append', nargs=2, metavar=('PATH','VALUE'), default=[])
    ap.add_argument('--ge', action='append', nargs=2, metavar=('PATH','VALUE'), default=[])
    ap.add_argument('--quiet', action='store_true', help='print only failures')
    ns = ap.parse_args()
    obj = json.loads(Path(ns.json_file).read_text())
    failures = []
    for path, expected_s in ns.eq:
        actual = get(obj, path)
        expected = coerce(expected_s)
        if actual != expected:
            failures.append(f'{path}: expected {expected!r}, got {actual!r}')
    for path, expected_s in ns.ge:
        actual = get(obj, path)
        expected = coerce(expected_s)
        if actual < expected:
            failures.append(f'{path}: expected >= {expected!r}, got {actual!r}')
    if failures:
        print(json.dumps({'ok': False, 'failures': failures}, indent=2))
        raise SystemExit(1)
    if not ns.quiet:
        print(json.dumps({'ok': True, 'checked': ns.json_file}, indent=2))


if __name__ == '__main__':
    main()
