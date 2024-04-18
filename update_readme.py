import os
import subprocess
import re

# @TODO:
# - fetch the human readable game name out of the game.json
# - read a description out of the game.json

URL_TEMPLATE = (
    "https://morgan3d.github.io/quadplay/console/quadplay.html"
    "?game=https://{gh_user}.github.io/{reponame}/{dirname}/{gamejson}"
)


GAME_HEADER_TEMPLATE = """

### {gamename}

"""


def main():
    # @TODO: this should just be a parameter.  Then this can be a freestanding
    #        script
    target_dir = os.path.dirname(os.path.abspath(__file__))
    all_stuff = (os.path.join(target_dir, d) for d in os.listdir(target_dir))
    subdirs = [
        d for d in all_stuff
        if os.path.isdir(d) and not d.endswith(".git")
    ]
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
        dirname = os.path.basename(d)

        # should only be one game.json
        game_data["jsonpath"] = next(
            t for t in os.listdir(d) if t.endswith(".game.json")
        )
        game_data["url"] = URL_TEMPLATE.format(
            gh_user=username,
            reponame=reponame,
            dirname=dirname,
            gamejson=game_data["jsonpath"],
        )

        m = re.match(r"(?P<game_name>.*?)\.(?P<branch_name>.*)", dirname)
        game_data["name"] = m.group("game_name")
        game_data["branch"] = m.group("branch_name")
        game_data["dirname"] = dirname

        game_data["commit-date-unix"] = subprocess.check_output(
            [
                "git",
                "log",
                "-n", "1",
                "--pretty=format:%ct",
                d
            ],
            cwd=d,
        ).decode("utf-8")
        game_data["commit-date-readable"] = subprocess.check_output(
            [
                "git",
                "log",
                "-n", "1",
                "--date=format-local:%m/%d/%Y",
                "--pretty=format:%cd",
                d
            ],
            cwd=d
        ).decode("utf-8")
        # @TODO: this needs to be left in the source repo, maybe a small json
        #        blob? or into a file
        try:
            with open(os.path.join(d, "description.md"), 'r') as fi:
                game_data["description"] = fi.read().strip()
        except FileNotFoundError:
            game_data["description"] = "No description on branch."
        DATA["games"].setdefault(game_data["name"], []).append(game_data)

    content_txt = ""
    for gamename, builds in DATA["games"].items():
        builds = reversed(sorted(builds, key=lambda b: b["commit-date-unix"]))
        label = "|label|"
        separator = "|-|"
        branch = "|branch|"
        description = "|description|"
        time = "|Deployed on|"
        link = "|link|"
        content_txt += GAME_HEADER_TEMPLATE.format(gamename=gamename)

        for build in builds:
            dirname = build["dirname"]

            fname = (
                "preview"
                if os.path.exists(os.path.join(dirname, "preview.png"))
                else "label128"
            )

            label += (
                f'[![{dirname}]({dirname}/{fname}.png)]({build["url"]})|'
            )
            separator += "-----|"
            branch += f'{build["branch"]}|'
            description += f'{build["description"]}|'
            time += f'{build["commit-date-readable"]}|'
            link += f'[play {build["branch"]}]({build["url"]})|'

        content_txt += label + "\n"
        content_txt += separator + "\n"
        content_txt += branch + "\n"
        content_txt += description + "\n"
        content_txt += time + "\n"
        content_txt += link + "\n"

    with open(os.path.join(target_dir, "README.template.md"), 'r') as fi:
        header = fi.read()

    with open(os.path.join(target_dir, "README.md"), 'w') as fo:
        fo.write(
            header.format(contents=content_txt)
        )

    print("updated readme.")


if __name__ == "__main__":
    main()
