#!/usr/bin/env python

import os
import argparse
import subprocess

__doc__ = "in case the descriptions need to be updated"


def _parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'project_root',
        type=str,
        help='Manifest files to run the updater on'
    )
    return parser.parse_args()


def main():
    args = _parse_args()

    target_dir = os.path.dirname(os.path.abspath(__file__))
    all_stuff = (
        os.path.join(target_dir, d)
        for d in os.listdir(target_dir)
    )
    subdirs = [
        d for d in all_stuff
        if os.path.isdir(d) and not d.endswith(".git")
    ]

    cmd = ["git", "config"]

    for d in subdirs:
        b = os.path.basename(d)
        b = b[b.find(".") + 1:]
        print(f"branch name: {b}")

        try:
            desc = subprocess.check_output(
                cmd + [f"branch.{b}.description"],
                cwd=args.project_root,
            ).decode("utf-8")
        except subprocess.CalledProcessError:
            print(f"no description for branch: {b}")
            continue

        desc = desc.replace("\n", "<br>")

        print(f"description: {desc}")
        with open(os.path.join(d, "description.md"), 'w') as fo:
            fo.write(desc)

    print("\n\n")
    print(
        "complete.  check `git status` to see what has changed, `git commit`"
        " to commit all the changes, and then `python update_readme.py` to"
        " update the README.md with the descriptions."
    )


if __name__ == "__main__":
    main()
