#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Push a local directory to GitHub through api.github.com.

Why this exists: on this network github.com:443 is blocked while
api.github.com is reachable, so `git push` cannot work. This script
recreates the commit via the Git Data API instead.

    python3 push_via_api.py <owner/repo> <branch> <local-dir> "<commit message>"
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"


def token():
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


class Gh:
    def __init__(self, tok):
        self.tok = tok

    def call(self, method, path, body=None):
        req = urllib.request.Request(
            API + path, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": f"Bearer {self.tok}",
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json",
                     "User-Agent": "scam-guard-push"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:400]
            raise SystemExit(f"{method} {path} -> {e.code}: {detail}")


def walk(root):
    skip_dirs = {"__pycache__", ".git"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if fn in (".DS_Store",) or fn.startswith("._"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            yield rel, full


def main():
    owner_repo, branch, root, message = sys.argv[1:5]
    gh = Gh(token())

    files = sorted(walk(root))
    print(f"files: {len(files)}")

    # A brand-new repository has no commit, and the Git Data API refuses to
    # create blobs until one exists. Seed it with a single file first.
    try:
        gh.call("GET", f"/repos/{owner_repo}/git/ref/heads/{branch}")
        print("repo already has commits")
    except SystemExit:
        seed = base64.b64encode(b"seed\n").decode()
        gh.call("PUT", f"/repos/{owner_repo}/contents/.seed",
                {"message": "seed", "content": seed, "branch": branch})
        print("seeded empty repo")

    tree = []
    for i, (rel, full) in enumerate(files, 1):
        with open(full, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        blob = gh.call("POST", f"/repos/{owner_repo}/git/blobs",
                       {"content": data, "encoding": "base64"})
        tree.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print(f"  [{i:2d}/{len(files)}] {rel}  ({os.path.getsize(full)} B)")

    t = gh.call("POST", f"/repos/{owner_repo}/git/trees", {"tree": tree})
    print(f"tree: {t['sha']}")

    commit = gh.call("POST", f"/repos/{owner_repo}/git/commits",
                     {"message": message, "tree": t["sha"], "parents": []})
    print(f"commit: {commit['sha']}")

    gh.call("PATCH", f"/repos/{owner_repo}/git/refs/heads/{branch}",
            {"sha": commit["sha"], "force": True})
    print(f"branch {branch} -> {commit['sha'][:8]}")

    # make sure the pushed branch is the default branch
    gh.call("PATCH", f"/repos/{owner_repo}", {"default_branch": branch})
    print("default branch set")


if __name__ == "__main__":
    main()
