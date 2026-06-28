#!/usr/bin/env python3
"""
Fetches GitHub repo content for hackathon analysis.
Outputs repos_data.json with raw file contents and commit timestamps.
"""

import os
import sys
import json
import time
import base64
import re
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HACKATHON_START = "2026-06-27"
HACKATHON_END = "2026-06-28"

PRIORITY_FILES = [
    "README.md", "readme.md", "README.txt", "README",
    "requirements.txt", "package.json", "Gemfile", "go.mod",
    "pyproject.toml", "Cargo.toml",
    "docker-compose.yml", "docker-compose.yaml", "Dockerfile",
    ".env.example", ".env.sample", "app.py", "main.py",
    "index.js", "index.ts", "server.js", "server.ts",
    "app.js", "app.ts",
]

SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".rb", ".go", ".rs", ".java", ".cs"}

MAX_SOURCE_FILES = 15
MAX_FILE_CHARS = 8000


def headers():
    h = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"token {GITHUB_TOKEN}"
    return h


def parse_repos(filepath):
    """Parse repos from a markdown file (URLs) or JSON file (structured submissions)."""
    path = Path(filepath)
    if path.suffix == ".json":
        submissions = json.loads(path.read_text())
        seen, result = set(), []
        for s in submissions:
            url = s.get("github", "")
            m = re.search(r'github\.com/([a-zA-Z0-9_.\-]+/[a-zA-Z0-9_.\-]+)', url)
            if m:
                owner_repo = m.group(1).rstrip("/").rstrip(".git")
                if owner_repo not in seen:
                    seen.add(owner_repo)
                    result.append({
                        "owner_repo": owner_repo,
                        "submission_name": s.get("name", ""),
                        "submission_description": s.get("description", ""),
                        "submission_num": s.get("num"),
                        "demo_url": s.get("demo"),
                        "members": s.get("members", 1),
                        "partner_technologies": s.get("partner_technologies", ""),
                    })
        return result
    else:
        content = path.read_text()
        matches = re.findall(r'https://github\.com/([a-zA-Z0-9_.\-]+/[a-zA-Z0-9_.\-]+)', content)
        seen, result = set(), []
        for m in matches:
            m = m.rstrip("/")
            if m not in seen:
                seen.add(m)
                result.append({"owner_repo": m, "submission_name": "", "submission_description": "", "submission_num": None, "demo_url": None, "members": 1, "partner_technologies": ""})
        return result


def get(url, pause=0.2):
    time.sleep(pause)
    return requests.get(url, headers=headers())


def fetch_repo_meta(owner_repo):
    r = get(f"https://api.github.com/repos/{owner_repo}", pause=0.1)
    if r.status_code == 200:
        d = r.json()
        return {
            "name": d.get("name", owner_repo.split("/")[-1]),
            "description": d.get("description") or "",
            "default_branch": d.get("default_branch", "main"),
            "stars": d.get("stargazers_count", 0),
            "language": d.get("language") or "",
        }
    return {"name": owner_repo.split("/")[-1], "description": "", "default_branch": "main", "stars": 0, "language": ""}


def fetch_tree(owner_repo, branch):
    r = get(f"https://api.github.com/repos/{owner_repo}/git/trees/{branch}?recursive=1")
    if r.status_code == 404:
        alt = "master" if branch == "main" else "main"
        r = get(f"https://api.github.com/repos/{owner_repo}/git/trees/{alt}?recursive=1")
    if r.status_code == 200:
        return r.json().get("tree", [])
    return []


def fetch_file(owner_repo, path):
    r = get(f"https://api.github.com/repos/{owner_repo}/contents/{path}", pause=0.1)
    if r.status_code == 200:
        d = r.json()
        if isinstance(d, dict) and d.get("encoding") == "base64" and d.get("content"):
            try:
                return base64.b64decode(d["content"]).decode("utf-8", errors="replace")[:MAX_FILE_CHARS]
            except Exception:
                pass
    return ""


def fetch_commits(owner_repo):
    r = get(f"https://api.github.com/repos/{owner_repo}/commits?per_page=1")
    last_date = None
    if r.status_code == 200 and r.json():
        last_date = r.json()[0]["commit"]["committer"]["date"]

    first_date = None
    link = r.headers.get("Link", "")
    match = re.search(r'<[^>]+[?&]page=(\d+)[^>]*>;\s*rel="last"', link)
    if match:
        last_page = match.group(1)
        r2 = get(f"https://api.github.com/repos/{owner_repo}/commits?per_page=1&page={last_page}")
        if r2.status_code == 200 and r2.json():
            first_date = r2.json()[0]["commit"]["committer"]["date"]
    else:
        if r.status_code == 200 and r.json():
            first_date = r.json()[0]["commit"]["committer"]["date"]

    return first_date, last_date


def fetch_repo(repo_entry):
    owner_repo = repo_entry["owner_repo"] if isinstance(repo_entry, dict) else repo_entry
    print(f"  Fetching metadata...")
    meta = fetch_repo_meta(owner_repo)

    print(f"  Fetching file tree...")
    tree = fetch_tree(owner_repo, meta["default_branch"])
    tree_paths = {item["path"] for item in tree if item["type"] == "blob"}

    files = {}

    for fname in PRIORITY_FILES:
        if fname in tree_paths:
            content = fetch_file(owner_repo, fname)
            if content:
                files[fname] = content

    source_files = [
        item["path"] for item in tree
        if item["type"] == "blob"
        and Path(item["path"]).suffix in SOURCE_EXTENSIONS
        and item["path"] not in files
        and item.get("size", 0) < 100000
    ][:MAX_SOURCE_FILES]

    print(f"  Fetching {len(source_files)} source files...")
    for path in source_files:
        content = fetch_file(owner_repo, path)
        if content:
            files[path] = content

    print(f"  Fetching commit history...")
    first_commit, last_commit = fetch_commits(owner_repo)

    return {
        "owner_repo": owner_repo,
        "url": f"https://github.com/{owner_repo}",
        "submission_name": repo_entry.get("submission_name", "") if isinstance(repo_entry, dict) else "",
        "submission_description": repo_entry.get("submission_description", "") if isinstance(repo_entry, dict) else "",
        "submission_num": repo_entry.get("submission_num") if isinstance(repo_entry, dict) else None,
        "demo_url": repo_entry.get("demo_url") if isinstance(repo_entry, dict) else None,
        "members": repo_entry.get("members", 1) if isinstance(repo_entry, dict) else 1,
        "partner_technologies": repo_entry.get("partner_technologies", "") if isinstance(repo_entry, dict) else "",
        "meta": meta,
        "files": files,
        "first_commit": first_commit,
        "last_commit": last_commit,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetcher.py <repos.md>")
        sys.exit(1)

    repos_file = sys.argv[1]
    if not Path(repos_file).exists():
        print(f"Error: {repos_file} not found")
        sys.exit(1)

    if not GITHUB_TOKEN:
        print("Warning: GITHUB_TOKEN not found in .env or environment. Rate limited to 60 req/hr.")
    else:
        print("GitHub token loaded.")

    repos = parse_repos(repos_file)
    if not repos:
        print(f"No GitHub URLs found in {repos_file}")
        sys.exit(1)

    print(f"\nFound {len(repos)} repos. Fetching content...\n")

    results = []
    for i, repo_entry in enumerate(repos, 1):
        owner_repo = repo_entry["owner_repo"] if isinstance(repo_entry, dict) else repo_entry
        print(f"[{i}/{len(repos)}] {owner_repo}")
        try:
            data = fetch_repo(repo_entry)
            results.append(data)
            print(f"  OK - {len(data['files'])} files fetched")
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "owner_repo": owner_repo,
                "url": f"https://github.com/{owner_repo}",
                "submission_name": repo_entry.get("submission_name", "") if isinstance(repo_entry, dict) else "",
                "submission_description": repo_entry.get("submission_description", "") if isinstance(repo_entry, dict) else "",
                "submission_num": repo_entry.get("submission_num") if isinstance(repo_entry, dict) else None,
                "demo_url": repo_entry.get("demo_url") if isinstance(repo_entry, dict) else None,
                "members": repo_entry.get("members", 1) if isinstance(repo_entry, dict) else 1,
                "partner_technologies": repo_entry.get("partner_technologies", "") if isinstance(repo_entry, dict) else "",
                "meta": {"name": owner_repo.split("/")[-1], "description": "", "language": ""},
                "files": {},
                "first_commit": None,
                "last_commit": None,
                "fetch_error": str(e),
            })
        time.sleep(0.3)

    output = Path("repos_data.json")
    output.write_text(json.dumps(results, indent=2))
    print(f"\nDone. Data saved to repos_data.json ({len(results)} repos)")
    print("Now run: /analyze-hackathon (without args) to generate report.html")


if __name__ == "__main__":
    main()
