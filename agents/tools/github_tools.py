"""
GitHub Tools for AXIOM Defect Intelligence.
Fetches, caches, and searches live issues from GitHub repository:
https://github.com/JyothiLakshmikanth/EKey2W/issues
"""

import os
import re
import json
import logging
import base64
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("axiom.tools.github")

DEFAULT_REPO = "JyothiLakshmikanth/EKey2W"
_CACHED_ISSUES: List[Dict[str, Any]] = []


def _get_github_token() -> Optional[str]:
    """Retrieve GitHub token from env or .env file."""
    token = os.getenv("GITHUB_TOKEN")
    if not token and os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GITHUB_TOKEN="):
                        token = line.strip().split("=", 1)[1].strip()
                        break
        except Exception:
            pass
    return token


def github_list_all_issues(repo: str = DEFAULT_REPO, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Fetches all open and closed issues from the target GitHub repository.
    Uses in-memory caching to minimize GitHub API rate limiting.
    """
    global _CACHED_ISSUES
    if _CACHED_ISSUES and not force_refresh:
        return _CACHED_ISSUES

    token = _get_github_token()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "axiom-defect-agent/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_issues = []
    page = 1
    per_page = 100

    try:
        while True:
            url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page={per_page}&page={page}"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                logger.warning(f"GitHub API error fetching {repo} page {page}: {resp.status_code} - {resp.text[:100]}")
                break
            items = resp.json()
            if not items or not isinstance(items, list):
                break
            all_issues.extend(items)
            if len(items) < per_page:
                break
            page += 1
            if page > 5:  # Safety cap at 500 issues
                break

        if all_issues:
            _CACHED_ISSUES = all_issues
            logger.info(f"GitHub: Cached {len(all_issues)} issues from {repo}")
    except Exception as e:
        logger.error(f"Failed to fetch GitHub issues from {repo}: {e}")

    return _CACHED_ISSUES


def github_get_issue_by_number(issue_number: int, repo: str = DEFAULT_REPO) -> Optional[Dict[str, Any]]:
    """Retrieve a single GitHub issue by its issue number."""
    issues = github_list_all_issues(repo)
    for issue in issues:
        if issue.get("number") == issue_number:
            return issue
    return None


def github_find_matching_issue(query: str, repo: str = DEFAULT_REPO) -> Optional[Dict[str, Any]]:
    """
    Finds the most relevant GitHub issue matching a user query:
    1. By explicit issue number (e.g. #2, issue 2, GH-2, GH-ISSUE-2)
    2. By exact title match
    3. By token/keyword overlap in title and body
    """
    issues = github_list_all_issues(repo)
    if not issues:
        return None

    # 0. Filter issues: prioritize actual issues over pull requests
    actual_issues = [i for i in issues if "pull_request" not in i]
    search_pool = actual_issues if actual_issues else issues

    # 1. Check for explicit issue number
    num_match = re.search(r'(?:#|issue\s*|gh-issue-|gh-)(\d+)\b', query, re.IGNORECASE)
    if num_match:
        target_num = int(num_match.group(1))
        for issue in search_pool:
            if issue.get("number") == target_num:
                logger.info(f"GitHub: Matched issue #{target_num} by explicit number")
                return issue

    # 2. Check for exact title match or substring in query
    clean_query = query.lower()
    for issue in search_pool:
        title = issue.get("title", "").lower()
        if title and (title in clean_query or clean_query in title):
            logger.info(f"GitHub: Exact/substring title match on #{issue.get('number')}: {issue.get('title')}")
            return issue

    # 3. Score by meaningful keyword overlap
    stop_words = {"the", "for", "bug", "defect", "triage", "and", "show", "visually", "analysis", "preform", "perform", "with", "what", "how", "why", "from", "this", "then", "post", "ticket"}
    query_tokens = set(re.findall(r'[a-zA-Z0-9]{3,}', clean_query)) - stop_words

    best_issue = None
    best_score = 0

    for issue in search_pool:
        title_tokens = set(re.findall(r'[a-zA-Z0-9]{3,}', issue.get("title", "").lower()))
        body_tokens = set(re.findall(r'[a-zA-Z0-9]{3,}', (issue.get("body") or "").lower()))

        # Heavily weight title matches over body matches
        title_overlap = query_tokens.intersection(title_tokens)
        body_overlap = query_tokens.intersection(body_tokens)
        score = (len(title_overlap) * 3) + len(body_overlap)

        if score > best_score:
            best_score = score
            best_issue = issue

    if best_issue and best_score >= 2:
        logger.info(f"GitHub: Keyword match on #{best_issue.get('number')}: {best_issue.get('title')} (score={best_score})")
        return best_issue

    return None


def format_github_issue_evidence(issue: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a GitHub issue into an authoritative EvidenceEnvelope.
    Extracts linked requirements and test cases mentioned in the issue body.
    """
    num = issue.get("number")
    title = issue.get("title", "")
    body = issue.get("body", "") or ""

    # Extract linked requirements (REQ-L...) and test cases (TC-...)
    linked_reqs = list(set(re.findall(r'REQ-[A-Z0-9-]+', body)))
    linked_tcs = list(set(re.findall(r'TC-[A-Z0-9-]+', body)))

    payload = {
        "Type": "GitHub Issue",
        "Id": f"GH-ISSUE-{num}",
        "Issue_Number": num,
        "Summary": title,
        "Title": title,
        "Status": issue.get("state", "open").capitalize(),
        "State": issue.get("state"),
        "Labels": [l.get("name") if isinstance(l, dict) else l for l in issue.get("labels", [])],
        "Author": issue.get("user", {}).get("login"),
        "URL": issue.get("html_url"),
        "Body": body,
        "Linked_Requirements": linked_reqs,
        "Linked_Test_Cases": linked_tcs,
        "Created_At": issue.get("created_at"),
        "Updated_At": issue.get("updated_at")
    }

    return {
        "artifact_id": f"GH-ISSUE-{num}",
        "artifact_type": "github_issue_record",
        "source_system": "github_repository",
        "source_uri": issue.get("html_url", f"https://github.com/{DEFAULT_REPO}/issues/{num}"),
        "version": "1.0",
        "updated_at": issue.get("updated_at", "2026-10-18T00:00:00Z"),
        "authoritative": True,
        "synthetic": False,
        "quality_status": "verified",
        "payload": payload
    }


def github_get_file_content(file_path: str, repo: str = DEFAULT_REPO, ref: str = "main") -> Optional[Dict[str, Any]]:
    """
    Fetches file content and metadata directly from GitHub repository.
    Returns decoded UTF-8 content and blob SHA.
    """
    token = _get_github_token()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "axiom-codefix-agent/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={ref}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            raw_content = base64.b64decode(data.get("content", "")).decode("utf-8")
            return {
                "file_path": file_path,
                "content": raw_content,
                "sha": data.get("sha"),
                "size": data.get("size"),
                "ref": ref
            }
        logger.warning(f"GitHub get file failed for {file_path} (ref={ref}): {resp.status_code}")
    except Exception as e:
        logger.error(f"Error fetching {file_path} from GitHub: {e}")
    return None


def github_create_branch(branch_name: str, repo: str = DEFAULT_REPO, base_branch: str = "main") -> Dict[str, Any]:
    """
    Creates a new branch on GitHub pointing to the latest commit of base_branch.
    If the branch already exists, retrieves its reference without overwriting.
    """
    token = _get_github_token()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "axiom-codefix-agent/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # 1. Check if branch already exists
    check_url = f"https://api.github.com/repos/{repo}/git/ref/heads/{branch_name}"
    try:
        r_check = requests.get(check_url, headers=headers, timeout=10)
        if r_check.status_code == 200:
            obj = r_check.json().get("object", {})
            logger.info(f"GitHub branch '{branch_name}' already exists with SHA {obj.get('sha')}")
            return {
                "status": "existing",
                "branch_name": branch_name,
                "sha": obj.get("sha"),
                "repo": repo
            }

        # 2. Get base branch commit SHA
        base_url = f"https://api.github.com/repos/{repo}/git/ref/heads/{base_branch}"
        r_base = requests.get(base_url, headers=headers, timeout=10)
        if r_base.status_code != 200:
            raise RuntimeError(f"Could not retrieve base branch '{base_branch}' SHA: {r_base.status_code} - {r_base.text}")

        base_sha = r_base.json()["object"]["sha"]

        # 3. Create the ref
        create_url = f"https://api.github.com/repos/{repo}/git/refs"
        payload = {"ref": f"refs/heads/{branch_name}", "sha": base_sha}
        r_create = requests.post(create_url, headers=headers, json=payload, timeout=10)

        if r_create.status_code == 201:
            logger.info(f"GitHub: Created branch '{branch_name}' from {base_branch} ({base_sha[:7]})")
            return {
                "status": "created",
                "branch_name": branch_name,
                "sha": base_sha,
                "repo": repo
            }
        elif r_create.status_code == 422:
            return {"status": "existing", "branch_name": branch_name, "sha": base_sha, "repo": repo}
        else:
            raise RuntimeError(f"Failed to create branch: {r_create.status_code} - {r_create.text}")

    except Exception as e:
        logger.error(f"Error creating branch '{branch_name}' on {repo}: {e}")
        return {"status": "failed", "branch_name": branch_name, "error": str(e), "repo": repo}


def github_commit_file(
    file_path: str,
    new_content: str,
    commit_message: str,
    branch_name: str,
    repo: str = DEFAULT_REPO
) -> Dict[str, Any]:
    """
    Commits updated file content directly to the specified branch on GitHub.
    Retrieves the current file blob SHA on that branch to ensure atomic commit.
    """
    token = _get_github_token()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "axiom-codefix-agent/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        # Retrieve latest blob sha on the branch
        file_meta = github_get_file_content(file_path, repo=repo, ref=branch_name)
        file_sha = file_meta.get("sha") if file_meta else None

        commit_payload = {
            "message": commit_message,
            "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
            "branch": branch_name
        }
        if file_sha:
            commit_payload["sha"] = file_sha

        put_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        resp = requests.put(put_url, headers=headers, json=commit_payload, timeout=15)

        if resp.status_code in (200, 201):
            res_data = resp.json()
            commit_info = res_data.get("commit", {})
            sha = commit_info.get("sha", "")
            logger.info(f"GitHub: Committed '{file_path}' to branch '{branch_name}' (SHA: {sha[:7]})")
            return {
                "status": "committed",
                "commit_sha": sha,
                "commit_url": commit_info.get("html_url"),
                "file_path": file_path,
                "branch": branch_name,
                "repo": repo
            }
        else:
            logger.error(f"GitHub commit failed ({resp.status_code}): {resp.text}")
            return {"status": "failed", "error": resp.text, "branch": branch_name, "repo": repo}

    except Exception as e:
        logger.error(f"Error committing {file_path} to {branch_name}: {e}")
        return {"status": "failed", "error": str(e), "branch": branch_name, "repo": repo}


def github_create_pull_request(
    title: str,
    body: str,
    head_branch: str,
    base_branch: str = "main",
    repo: str = DEFAULT_REPO
) -> Dict[str, Any]:
    """
    Creates an authoritative GitHub Pull Request targeting base_branch.
    If a PR for this head branch already exists, retrieves and returns it.
    """
    token = _get_github_token()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "axiom-codefix-agent/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        # Check existing PRs
        list_url = f"https://api.github.com/repos/{repo}/pulls?state=all"
        r_list = requests.get(list_url, headers=headers, timeout=10)
        if r_list.status_code == 200:
            for p in r_list.json():
                if p.get("head", {}).get("ref") == head_branch:
                    logger.info(f"GitHub PR for '{head_branch}' already exists: #{p['number']}")
                    return {
                        "status": "existing",
                        "pr_number": p.get("number"),
                        "pr_url": p.get("html_url"),
                        "title": p.get("title"),
                        "state": p.get("state"),
                        "head_branch": head_branch,
                        "base_branch": base_branch,
                        "repo": repo
                    }

        # Create new PR
        pr_payload = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch
        }
        create_url = f"https://api.github.com/repos/{repo}/pulls"
        resp = requests.post(create_url, headers=headers, json=pr_payload, timeout=15)

        if resp.status_code == 201:
            pr_data = resp.json()
            logger.info(f"GitHub: Created PR #{pr_data.get('number')}: {pr_data.get('html_url')}")
            return {
                "status": "created",
                "pr_number": pr_data.get("number"),
                "pr_url": pr_data.get("html_url"),
                "title": pr_data.get("title"),
                "state": pr_data.get("state"),
                "head_branch": head_branch,
                "base_branch": base_branch,
                "repo": repo
            }
        else:
            logger.error(f"GitHub PR creation failed ({resp.status_code}): {resp.text}")
            return {"status": "failed", "error": resp.text, "head_branch": head_branch, "repo": repo}

    except Exception as e:
        logger.error(f"Error creating PR for {head_branch}: {e}")
        return {"status": "failed", "error": str(e), "head_branch": head_branch, "repo": repo}


def format_github_pull_request_evidence(
    pr_result: Dict[str, Any],
    file_path: str,
    patch_diff: str,
    commit_sha: str = ""
) -> Dict[str, Any]:
    """
    Normalizes GitHub Pull Request details into an authoritative EvidenceEnvelope.
    """
    pr_num = pr_result.get("pr_number", "N/A")
    pr_url = pr_result.get("pr_url", "")
    head_branch = pr_result.get("head_branch", "")
    repo = pr_result.get("repo", DEFAULT_REPO)

    payload = {
        "Type": "GitHub Pull Request",
        "PR_Number": pr_num,
        "PR_URL": pr_url,
        "Repository": repo,
        "Branch": head_branch,
        "Base_Branch": pr_result.get("base_branch", "main"),
        "Target_File": file_path,
        "Commit_SHA": commit_sha,
        "Patch_Diff": patch_diff,
        "State": pr_result.get("state", "open"),
        "Status": pr_result.get("status", "created"),
        "Safety_Compliance": "Rule #3 Compliant: Pull Request opened for Engineering review; no direct push to main."
    }

    return {
        "artifact_id": f"GH-PR-{pr_num}",
        "artifact_type": "proposed_surgical_patch",
        "source_system": "github_pull_request",
        "source_uri": pr_url or f"https://github.com/{repo}/pulls",
        "version": "1.0",
        "updated_at": "2026-10-18T20:30:00Z",
        "authoritative": True,
        "synthetic": False,
        "quality_status": "verified",
        "payload": payload
    }


def github_add_issue_comment(
    issue_number: int,
    comment_body: str,
    repo: str = DEFAULT_REPO,
    deduplicate: bool = True
) -> Dict[str, Any]:
    """
    Posts an authoritative analysis and fix comment directly to the GitHub issue.
    Informs the user and engineering team about root cause, surgical fix, and PR link.
    Automatically prevents duplicate comments by checking existing comments on the issue.
    """
    token = _get_github_token()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "axiom-agent/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"

    # Deduplication check: check if a comment with the same header or body already exists
    if deduplicate and token:
        try:
            get_resp = requests.get(url, headers=headers, timeout=10)
            if get_resp.status_code == 200:
                existing_comments = get_resp.json()
                first_line = comment_body.strip().splitlines()[0] if comment_body.strip() else ""
                for ec in existing_comments:
                    ec_body = ec.get("body", "")
                    # If exact same body or exact same AXIOM header, avoid duplicate
                    if first_line and first_line in ec_body:
                        logger.info(f"GitHub: Authoritative comment matching '{first_line[:50]}' already exists on #{issue_number} (ID {ec.get('id')}). Skipping duplicate.")
                        return {
                            "status": "already_posted",
                            "comment_id": ec.get("id"),
                            "comment_url": ec.get("html_url"),
                            "issue_number": issue_number,
                            "repo": repo
                        }
        except Exception as e:
            logger.warning(f"GitHub deduplication check warning: {e}")

    try:
        resp = requests.post(url, headers=headers, json={"body": comment_body}, timeout=15)
        if resp.status_code == 201:
            data = resp.json()
            logger.info(f"GitHub: Posted comment to issue #{issue_number}: {data.get('html_url')}")
            return {
                "status": "posted",
                "comment_id": data.get("id"),
                "comment_url": data.get("html_url"),
                "issue_number": issue_number,
                "repo": repo
            }
        else:
            logger.error(f"GitHub comment failed ({resp.status_code}): {resp.text}")
            return {"status": "failed", "error": resp.text, "issue_number": issue_number}
    except Exception as e:
        logger.error(f"Error commenting on issue #{issue_number}: {e}")
        return {"status": "failed", "error": str(e), "issue_number": issue_number}


