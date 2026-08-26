import json
import os
import urllib.request
from datetime import datetime, timezone


USERNAME = os.getenv("GITHUB_USERNAME", "davi-ricardo")
TOKEN = os.getenv("GITHUB_TOKEN")

OUTPUT = "assets/github-stats.svg"

API_URL = "https://api.github.com/graphql"


def github_graphql(query, variables=None):
    payload = {
        "query": query,
        "variables": variables or {}
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "github-stats-generator"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "errors" in result:
        raise RuntimeError(json.dumps(result["errors"], indent=2))

    return result["data"]


def escape_xml(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def format_number(value):
    return f"{value:,}".replace(",", ".")


def generate_svg(stats):
    width = 820
    height = 300

    commits = stats["commits"]
    issues = stats["issues"]
    prs = stats["prs"]
    repos = stats["repos"]
    stars = stats["stars"]
    followers = stats["followers"]

    svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}"
role="img"
aria-label="GitHub statistics for {escape_xml(USERNAME)}">

<defs>
    <linearGradient id="border" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#30363d"/>
        <stop offset="100%" stop-color="#58a6ff"/>
    </linearGradient>
</defs>

<rect
    x="1"
    y="1"
    width="{width - 2}"
    height="{height - 2}"
    rx="14"
    fill="#0d1117"
    stroke="url(#border)"
    stroke-width="2"
/>

<text
    x="35"
    y="48"
    fill="#f0f6fc"
    font-family="Arial, Helvetica, sans-serif"
    font-size="24"
    font-weight="700">
    GitHub Overview
</text>

<text
    x="35"
    y="73"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="14">
    @{escape_xml(USERNAME)}
</text>

<line
    x1="35"
    y1="92"
    x2="785"
    y2="92"
    stroke="#30363d"
    stroke-width="1"
/>

<text
    x="55"
    y="135"
    fill="#58a6ff"
    font-family="Arial, Helvetica, sans-serif"
    font-size="28"
    font-weight="700">
    {format_number(commits)}
</text>

<text
    x="55"
    y="157"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13">
    Commits
</text>

<text
    x="205"
    y="135"
    fill="#f0f6fc"
    font-family="Arial, Helvetica, sans-serif"
    font-size="28"
    font-weight="700">
    {format_number(repos)}
</text>

<text
    x="205"
    y="157"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13">
    Repositories
</text>

<text
    x="370"
    y="135"
    fill="#f2cc60"
    font-family="Arial, Helvetica, sans-serif"
    font-size="28"
    font-weight="700">
    {format_number(stars)}
</text>

<text
    x="370"
    y="157"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13">
    Stars
</text>

<text
    x="510"
    y="135"
    fill="#a5d6ff"
    font-family="Arial, Helvetica, sans-serif"
    font-size="28"
    font-weight="700">
    {format_number(followers)}
</text>

<text
    x="510"
    y="157"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13">
    Followers
</text>

<text
    x="55"
    y="215"
    fill="#f0f6fc"
    font-family="Arial, Helvetica, sans-serif"
    font-size="24"
    font-weight="700">
    {format_number(issues)}
</text>

<text
    x="55"
    y="236"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13">
    Issues
</text>

<text
    x="205"
    y="215"
    fill="#f0f6fc"
    font-family="Arial, Helvetica, sans-serif"
    font-size="24"
    font-weight="700">
    {format_number(prs)}
</text>

<text
    x="205"
    y="236"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13">
    Pull Requests
</text>

<circle
    cx="690"
    cy="205"
    r="34"
    fill="#161b22"
    stroke="#238636"
    stroke-width="5"
/>

<text
    x="690"
    y="211"
    text-anchor="middle"
    fill="#3fb950"
    font-family="Arial, Helvetica, sans-serif"
    font-size="16"
    font-weight="700">
    ACTIVE
</text>

<text
    x="690"
    y="255"
    text-anchor="middle"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="12">
    GitHub Profile
</text>

</svg>
"""

    return svg


def main():
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN is not available.")

    current_year = datetime.now(timezone.utc).year

    query = """
    query(
        $login: String!,
        $from: DateTime!,
        $to: DateTime!
    ) {
        user(login: $login) {

            followers {
                totalCount
            }

            repositories(
                first: 100
                ownerAffiliations: OWNER
                privacy: PUBLIC
            ) {
                totalCount

                nodes {
                    stargazerCount
                }
            }

            contributionsCollection(
                from: $from
                to: $to
            ) {
                totalCommitContributions
                totalIssueContributions
                totalPullRequestContributions
            }
        }
    }
    """

    variables = {
        "login": USERNAME,
        "from": f"{current_year}-01-01T00:00:00Z",
        "to": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    }

    data = github_graphql(query, variables)

    user = data["user"]

    repositories = user["repositories"]["nodes"]

    total_stars = sum(
        repository["stargazerCount"]
        for repository in repositories
    )

    contributions = user["contributionsCollection"]

    stats = {
        "commits": contributions["totalCommitContributions"],
        "issues": contributions["totalIssueContributions"],
        "prs": contributions["totalPullRequestContributions"],
        "repos": user["repositories"]["totalCount"],
        "stars": total_stars,
        "followers": user["followers"]["totalCount"]
    }

    os.makedirs(
        os.path.dirname(OUTPUT),
        exist_ok=True
    )

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(generate_svg(stats))

    print("GitHub statistics generated successfully.")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
