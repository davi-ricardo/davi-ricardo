import json
import os
import urllib.request
from datetime import datetime, timezone


USERNAME = os.getenv("GITHUB_USERNAME", "davi-ricardo")
TOKEN = os.getenv("GITHUB_TOKEN")

OUTPUT = "assets/github-stats.svg"
API_URL = "https://api.github.com/graphql"

YEAR = datetime.now(timezone.utc).year


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
            "User-Agent": "davi-ricardo-github-profile"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    if "errors" in result:
        raise RuntimeError(
            json.dumps(result["errors"], indent=2)
        )

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


def language_color(language):
    colors = {
        "JavaScript": "#f1e05a",
        "TypeScript": "#3178c6",
        "Python": "#3572A5",
        "PHP": "#4F5D95",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Shell": "#89e051",
        "Java": "#b07219",
        "C": "#555555",
        "C++": "#f34b7d",
        "C#": "#178600",
        "Go": "#00ADD8",
        "Rust": "#dea584",
        "Dart": "#00B4AB",
        "Vue": "#41b883",
        "SCSS": "#c6538c"
    }

    return colors.get(language, "#8b949e")


def contribution_color(count):
    if count == 0:
        return "#161b22"

    if count <= 2:
        return "#0e4429"

    if count <= 5:
        return "#006d32"

    if count <= 9:
        return "#26a641"

    return "#39d353"


def generate_metric(x, y, value, label, value_color="#f0f6fc"):
    return f"""
    <text
        x="{x}"
        y="{y}"
        fill="{value_color}"
        font-family="Arial, Helvetica, sans-serif"
        font-size="25"
        font-weight="700">
        {escape_xml(format_number(value))}
    </text>

    <text
        x="{x}"
        y="{y + 22}"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="12">
        {escape_xml(label.upper())}
    </text>
    """


def generate_svg(stats):
    width = 820
    height = 430

    svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}"
role="img"
aria-label="GitHub activity dashboard for {escape_xml(USERNAME)}">

<defs>

    <linearGradient
        id="border"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%">

        <stop
            offset="0%"
            stop-color="#30363d"/>

        <stop
            offset="100%"
            stop-color="#58a6ff"/>

    </linearGradient>

</defs>

<!-- Background -->

<rect
    x="1"
    y="1"
    width="{width - 2}"
    height="{height - 2}"
    rx="14"
    fill="#0d1117"
    stroke="url(#border)"
    stroke-width="2"/>


<!-- Header -->

<text
    x="32"
    y="38"
    fill="#f0f6fc"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13"
    font-weight="700">
    GITHUB ACTIVITY
</text>

<text
    x="788"
    y="38"
    text-anchor="end"
    fill="#58a6ff"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13"
    font-weight="700">
    {YEAR}
</text>

<text
    x="32"
    y="60"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="12">
    @{escape_xml(USERNAME)}
</text>

<line
    x1="32"
    y1="78"
    x2="788"
    y2="78"
    stroke="#30363d"
    stroke-width="1"/>


<!-- Metrics -->

{generate_metric(32, 112, stats["commits"], "Commits", "#58a6ff")}

{generate_metric(155, 112, stats["repos"], "Repositories")}

{generate_metric(305, 112, stats["stars"], "Stars", "#f2cc60")}

{generate_metric(435, 112, stats["followers"], "Followers", "#a5d6ff")}

{generate_metric(575, 112, stats["issues"], "Issues")}

{generate_metric(690, 112, stats["prs"], "Pull Requests")}


<!-- Contribution Activity -->

<line
    x1="32"
    y1="150"
    x2="788"
    y2="150"
    stroke="#30363d"
    stroke-width="1"/>

<text
    x="32"
    y="177"
    fill="#f0f6fc"
    font-family="Arial, Helvetica, sans-serif"
    font-size="13"
    font-weight="700">
    CONTRIBUTION ACTIVITY
</text>

<text
    x="788"
    y="177"
    text-anchor="end"
    fill="#8b949e"
    font-family="Arial, Helvetica, sans-serif"
    font-size="11">
    {format_number(stats["total_contributions"])} contributions
</text>
"""

    # Contribution heatmap
    heatmap_x = 32
    heatmap_y = 194

    weeks = stats["weeks"]

    for week_index, week in enumerate(weeks):

        for day_index, day in enumerate(
            week["contributionDays"]
        ):

            count = day["contributionCount"]

            x = heatmap_x + (week_index * 12)
            y = heatmap_y + (day_index * 10)

            svg += f"""
            <rect
                x="{x}"
                y="{y}"
                width="8"
                height="8"
                rx="2"
                fill="{contribution_color(count)}">

                <title>
                    {escape_xml(day["date"])}:
                    {count} contributions
                </title>

            </rect>
            """

    # Heatmap legend
    legend_x = 32
    legend_y = 278

    svg += f"""
    <text
        x="{legend_x}"
        y="{legend_y + 1}"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="10">
        Less
    </text>
    """

    legend_colors = [
        "#161b22",
        "#0e4429",
        "#006d32",
        "#26a641",
        "#39d353"
    ]

    for index, color in enumerate(legend_colors):

        x = legend_x + 30 + (index * 14)

        svg += f"""
        <rect
            x="{x}"
            y="{legend_y - 9}"
            width="9"
            height="9"
            rx="2"
            fill="{color}"/>
        """

    svg += f"""
    <text
        x="{legend_x + 105}"
        y="{legend_y + 1}"
        fill="#8b949e"
        font-family="Arial, Helvetica, sans-serif"
        font-size="10">
        More
    </text>
    """


    # Languages
    language_x = 455
    language_y = 315

    svg += f"""
    <line
        x1="32"
        y1="292"
        x2="788"
        y2="292"
        stroke="#30363d"
        stroke-width="1"/>

    <text
        x="32"
        y="320"
        fill="#f0f6fc"
        font-family="Arial, Helvetica, sans-serif"
        font-size="13"
        font-weight="700">
        TOP LANGUAGES
    </text>
    """

    languages = stats["languages"]

    bar_x = 32
    bar_y = 337
    bar_width = 440
    bar_height = 8

    current_x = bar_x

    for language in languages:

        percentage = language["percentage"]

        segment_width = (
            bar_width * percentage / 100
        )

        svg += f"""
        <rect
            x="{current_x}"
            y="{bar_y}"
            width="{segment_width}"
            height="{bar_height}"
            fill="{language_color(language["name"])}"/>
        """

        current_x += segment_width


    # Language labels
    label_y = 370

    for index, language in enumerate(languages):

        if index >= 5:
            break

        column = index % 3
        row = index // 3

        x = 32 + (column * 150)
        y = label_y + (row * 25)

        color = language_color(
            language["name"]
        )

        svg += f"""
        <circle
            cx="{x}"
            cy="{y - 4}"
            r="4"
            fill="{color}"/>

        <text
            x="{x + 10}"
            y="{y}"
            fill="#c9d1d9"
            font-family="Arial, Helvetica, sans-serif"
            font-size="11">

            {escape_xml(language["name"])}
            {language["percentage"]:.1f}%

        </text>
        """


    # Footer
    svg += f"""
    <text
        x="788"
        y="400"
        text-anchor="end"
        fill="#6e7681"
        font-family="Arial, Helvetica, sans-serif"
        font-size="10">
        Generated automatically via GitHub Actions
    </text>

</svg>
"""

    return svg


def main():

    if not TOKEN:
        raise RuntimeError(
            "GITHUB_TOKEN is not available."
        )

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

                    languages(
                        first: 10
                        orderBy: {
                            field: SIZE,
                            direction: DESC
                        }
                    ) {

                        edges {

                            size

                            node {
                                name
                            }

                        }

                    }

                }

            }

            contributionsCollection(
                from: $from
                to: $to
            ) {

                totalCommitContributions

                totalIssueContributions

                totalPullRequestContributions

                contributionCalendar {

                    totalContributions

                    weeks {

                        contributionDays {

                            contributionCount

                            date

                        }

                    }

                }

            }

        }

    }
    """

    variables = {

        "login": USERNAME,

        "from":
            f"{YEAR}-01-01T00:00:00Z",

        "to":
            datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

    }

    data = github_graphql(
        query,
        variables
    )

    user = data["user"]

    repositories = (
        user["repositories"]["nodes"]
    )

    contributions = (
        user["contributionsCollection"]
    )

    # Stars
    total_stars = sum(
        repository["stargazerCount"]
        for repository in repositories
    )

    # Languages
    language_sizes = {}

    for repository in repositories:

        for edge in repository["languages"]["edges"]:

            language_name = edge["node"]["name"]
            language_size = edge["size"]

            language_sizes[language_name] = (
                language_sizes.get(language_name, 0)
                + language_size
            )

    total_language_size = sum(
        language_sizes.values()
    )

    languages = []

    if total_language_size > 0:

        sorted_languages = sorted(
            language_sizes.items(),
            key=lambda item: item[1],
            reverse=True
        )

        for name, size in sorted_languages[:5]:

            percentage = (
                size / total_language_size
            ) * 100

            languages.append({
                "name": name,
                "percentage": percentage
            })

    stats = {

        "commits":
            contributions[
                "totalCommitContributions"
            ],

        "issues":
            contributions[
                "totalIssueContributions"
            ],

        "prs":
            contributions[
                "totalPullRequestContributions"
            ],

        "repos":
            user[
                "repositories"
            ]["totalCount"],

        "stars":
            total_stars,

        "followers":
            user[
                "followers"
            ]["totalCount"],

        "total_contributions":
            contributions[
                "contributionCalendar"
            ]["totalContributions"],

        "weeks":
            contributions[
                "contributionCalendar"
            ]["weeks"],

        "languages":
            languages
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

        file.write(
            generate_svg(stats)
        )

    print(
        "GitHub dashboard generated successfully."
    )

    print(
        json.dumps(
            {
                key: value
                for key, value in stats.items()
                if key not in ["weeks"]
            },
            indent=2
        )
    )


if __name__ == "__main__":
    main()
