import requests
import base64


def get_repository_info(repo_url: str):

    parts = repo_url.rstrip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL")

    owner = parts[-2]
    repo = parts[-1]

    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(url)

    if response.status_code == 404:
        raise ValueError("Repository not found")

    if response.status_code != 200:
        raise ValueError("Failed to fetch repository information")

    data = response.json()

    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "owner": data["owner"]["login"],
        "description": data["description"],
        "language": data["language"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "url": data["html_url"]
    }


def get_repository_files(owner: str, repo: str):

    repo_url = f"https://api.github.com/repos/{owner}/{repo}"

    repo_response = requests.get(repo_url)

    if repo_response.status_code != 200:
        raise ValueError("Repository not found")

    repo_data = repo_response.json()

    default_branch = repo_data["default_branch"]

    tree_url = (
        f"https://api.github.com/repos/{owner}/{repo}"
        f"/git/trees/{default_branch}?recursive=1"
    )

    tree_response = requests.get(tree_url)

    if tree_response.status_code != 200:
        raise ValueError("Unable to fetch repository files")

    tree_data = tree_response.json()

    files = []

    for item in tree_data.get("tree", []):

        if item["type"] == "blob":
            files.append({
                "path": item["path"],
                "type": "file"
            })

        elif item["type"] == "tree":
            files.append({
                "path": item["path"],
                "type": "folder"
            })

    return files
def get_file_content(owner: str, repo: str, path: str):

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    response = requests.get(url)

    if response.status_code == 404:
        raise ValueError("File not found")

    if response.status_code != 200:
        raise ValueError("Unable to fetch file")

    data = response.json()

    if data.get("type") != "file":
        raise ValueError("Selected path is not a file")

    content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    return {
        "path": data["path"],
        "name": data["name"],
        "content": content
    }