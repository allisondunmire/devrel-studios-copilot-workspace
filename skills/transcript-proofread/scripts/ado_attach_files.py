"""
Attach local caption files to an Azure DevOps work item.

Authentication uses the caller's Azure CLI session and requests an access
token scoped to Azure DevOps. Tokens are never written to disk or logged.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


ADO_RESOURCE = "499b84ac-1321-427f-aa17-267ca6975798"
API_VERSION = "7.1"


def build_upload_url(organization, project, file_name):
    organization = urllib.parse.quote(organization, safe="")
    project = urllib.parse.quote(project, safe="")
    query = urllib.parse.urlencode(
        {"fileName": file_name, "api-version": API_VERSION}
    )
    return (
        f"https://dev.azure.com/{organization}/{project}/"
        f"_apis/wit/attachments?{query}"
    )


def build_patch_url(organization, project, work_item_id):
    organization = urllib.parse.quote(organization, safe="")
    project = urllib.parse.quote(project, safe="")
    return (
        f"https://dev.azure.com/{organization}/{project}/_apis/wit/"
        f"workitems/{work_item_id}?api-version={API_VERSION}"
    )


def build_work_item_url(organization, project, work_item_id):
    organization = urllib.parse.quote(organization, safe="")
    project = urllib.parse.quote(project, safe="")
    query = urllib.parse.urlencode(
        {"$expand": "relations", "api-version": API_VERSION}
    )
    return (
        f"https://dev.azure.com/{organization}/{project}/_apis/wit/"
        f"workitems/{work_item_id}?{query}"
    )


def build_patch_payload(attachment_url, comment):
    return [
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "AttachedFile",
                "url": attachment_url,
                "attributes": {"comment": comment},
            },
        }
    ]


def inspect_work_item(work_item, expected_type):
    actual_type = work_item.get("fields", {}).get("System.WorkItemType")
    if expected_type and actual_type != expected_type:
        raise RuntimeError(
            f"Work item {work_item.get('id', 'unknown')} is "
            f"{actual_type or 'an unknown type'}, not {expected_type}."
        )

    names = set()
    for relation in work_item.get("relations", []):
        if relation.get("rel") != "AttachedFile":
            continue
        attributes = relation.get("attributes", {})
        name = attributes.get("name")
        if not name:
            query = urllib.parse.parse_qs(
                urllib.parse.urlsplit(relation.get("url", "")).query
            )
            name = next(iter(query.get("fileName", [])), None)
        if name:
            names.add(name.casefold())
    return names


def get_access_token():
    az_command = shutil.which("az") or shutil.which("az.cmd")
    if not az_command:
        raise RuntimeError(
            "Azure CLI was not found. Install it and run 'az login'."
        )
    try:
        result = subprocess.run(
            [
                az_command,
                "account",
                "get-access-token",
                "--resource",
                ADO_RESOURCE,
                "--query",
                "accessToken",
                "-o",
                "tsv",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip()
        raise RuntimeError(
            f"Could not get an Azure DevOps access token: {detail}"
        ) from error

    token = result.stdout.strip()
    if not token:
        raise RuntimeError(
            "Azure CLI returned an empty token. Run 'az login' and retry."
        )
    return token


def request_json(url, method, token, body, content_type):
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Azure DevOps request failed ({error.code}): {detail}"
        ) from error
    if not payload:
        return {}
    try:
        return json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Azure DevOps returned a response that was not valid JSON."
        ) from error


def attach_file(
    organization,
    project,
    work_item_id,
    file_path,
    token,
    comment,
):
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as handle:
        attachment = request_json(
            build_upload_url(organization, project, file_name),
            "POST",
            token,
            handle.read(),
            "application/octet-stream",
        )

    attachment_url = attachment.get("url")
    if not attachment_url:
        raise RuntimeError(
            f"Azure DevOps did not return an attachment URL for {file_name}."
        )

    request_json(
        build_patch_url(organization, project, work_item_id),
        "PATCH",
        token,
        json.dumps(
            build_patch_payload(attachment_url, comment)
        ).encode("utf-8"),
        "application/json-patch+json",
    )
    return attachment_url


def get_work_item(
    organization,
    project,
    work_item_id,
    token,
):
    return request_json(
        build_work_item_url(organization, project, work_item_id),
        "GET",
        token,
        None,
        "application/json",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Attach caption files to an Azure DevOps work item."
    )
    parser.add_argument("--organization", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--work-item-id", required=True, type=int)
    parser.add_argument(
        "--expected-work-item-type",
        default="Episode",
        help="Required work item type (default: Episode)",
    )
    parser.add_argument(
        "--comment",
        default="Corrected caption file added via Copilot CLI.",
    )
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    missing = [path for path in args.files if not os.path.isfile(path)]
    if missing:
        for path in missing:
            print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        token = get_access_token()
        work_item = get_work_item(
            args.organization,
            args.project,
            args.work_item_id,
            token,
        )
        existing_names = inspect_work_item(
            work_item,
            args.expected_work_item_type,
        )
        for file_path in args.files:
            file_name = os.path.basename(file_path)
            if file_name.casefold() in existing_names:
                print(f"Already attached: {file_path}")
                continue
            attach_file(
                args.organization,
                args.project,
                args.work_item_id,
                file_path,
                token,
                args.comment,
            )
            print(f"Attached: {file_path}")
            existing_names.add(file_name.casefold())
    except (OSError, RuntimeError) as error:
        print(f"Attachment failed: {error}", file=sys.stderr)
        sys.exit(1)

    project = urllib.parse.quote(args.project, safe="")
    print(
        f"https://dev.azure.com/{args.organization}/{project}/"
        f"_workitems/edit/{args.work_item_id}"
    )


if __name__ == "__main__":
    main()
