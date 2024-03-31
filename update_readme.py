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
    text = ""
    for d in subdirs:
        game_json = next(t for t in os.listdir(d) if t.endswith(".game.json"))
        game_url = URL_TEMPLATE.format(
            gh_user=username,
            reponame=reponame,
            dirname=d,
            gamejson=game_json,
        )
        text += CONTENT_TEMPLATE.format(
            dirname=d,
            game_url=game_url,
        )

    with open("README.template.md", 'r') as fi:
        header = fi.read()

    with open("README.md", 'w') as fo:
        fo.write(
            header.format(contents=text)
        )

    print("updated readme.")


if __name__ == "__main__":
    main()
