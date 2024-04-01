import os
import subprocess
import re

# @TODO:
# - sort by recent commits
# - fetch the human readable game name out of the game.json
# - read a description out of the game.json
# - make sure that the other makefile cleanup stuff doesn't wipe this stuff
# - do some test deployments

SKIPDIRS = set([".git"])

URL_TEMPLATE = (
    "https://morgan3d.github.io/quadplay/console/quadplay.html"
    "?game=https://{gh_user}.github.io/{reponame}/{dirname}/{gamejson}"
)


CONTENT_TEMPLATE = """
|[![{dirname}]({dirname}/label128.png)]({game_url})|
|-----------------|
|project name: {dirname}|
|this is where a description would be nice to generate somehow|
|[play {dirname}]({game_url})|
"""

GAME_HEADER_TEMPLATE = """
### {gamename}
"""


def main():
    all_stuff = os.listdir(".")
    subdirs = [d for d in all_stuff if os.path.isdir(d) and d not in SKIPDIRS]
    print(subdirs)
    git_remote = subprocess.check_output(
        ["git", "remote", "-v"]
    ).decode("utf-8")
    m = re.match(r".*:(?P<username>.*)/(?P<reponame>.*)\.git", git_remote)
    username = m.group("username")
    reponame = m.group("reponame")

    DATA = {
        "username": username,
        "reponame": reponame,
        "games": {},
    }

    for d in subdirs:
        game_data = {}

        # should only be one game.json
        game_data["jsonpath"] = next(
            t for t in os.listdir(d) if t.endswith(".game.json")
        )
        game_data["url"] = URL_TEMPLATE.format(
            gh_user=username,
            reponame=reponame,
            dirname=d,
            gamejson=game_data["jsonpath"],
        )

        m = re.match(r"(?P<game_name>.*?)\.(?P<branch_name>.*)", d)
        game_data["name"] = m.group("game_name")
        game_data["branch"] = m.group("branch_name")
        game_data["dirname"] = d

        game_data["commit-date-unix"] = subprocess.check_output(
            [
                "git",
                "--work-tree", d,
                "log",
                "-n", "1",
                "--pretty=format:%ct"
            ]
        ).decode("utf-8")
        game_data["commit-date-readable"] = subprocess.check_output(
            [
                "git",
                "--work-tree", d,
                "log",
                "-n", "1",
                "--date=format-local:%m/%d/%Y",
                "--pretty=format:%cd",
            ]
        ).decode("utf-8")
        # @TODO: this needs to be left in the source repo, maybe a small json
        #        blob? or into a file
        try:
            with open(os.path.join(d, "description.md")) as fi:
                game_data["description"] = fi.read()
        except FileNotFoundError:
            game_data["description"] = "No description on branch."
        DATA["games"].setdefault(game_data["name"], []).append(game_data)

    content_txt = ""
    for gamename, builds in DATA["games"].items():
        builds = sorted(builds, key=lambda b: b["commit-date-unix"])
        label = "|label|"
        separator = "|-|"
        branch = "|branch|"
        description = "|description|"
        time = "|Deployed on|"
        link = "|link|"
        content_txt += GAME_HEADER_TEMPLATE.format(gamename=gamename)

        for build in builds:

            dirname = game_data["dirname"]

            label += (
                f'[![{dirname}]({dirname}/label128.png)]({game_data["url"]})|'
            )
            separator += "-----|"
            branch += f'{game_data["branch"]}|'
            description += f'{game_data["description"]}|'
            time += f'{game_data["commit-date-readable"]}|'
            link += f'[play {game_data["name"]}]({game_data["url"]})|'

        content_txt += label + "\n"
        content_txt += separator + "\n"
        content_txt += branch + "\n"
        content_txt += description + "\n"
        content_txt += time + "\n"
        content_txt += link + "\n"

    with open("README.template.md", 'r') as fi:
        header = fi.read()

    with open("README.md", 'w') as fo:
        fo.write(
            header.format(contents=content_txt)
        )

    print("updated readme.")


if __name__ == "__main__":
    main()
