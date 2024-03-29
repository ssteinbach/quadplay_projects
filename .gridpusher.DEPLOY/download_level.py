#!/usr/bin/env python

import argparse
import requests
import csv

import yaml
from yaml.representer import SafeRepresenter

"""Download google sheet-backed level designs."""

TOC_SHEET_NAME = "ORDER"
TOC_FILENAME = "spreadsheets_backups/level_order.csv"
SHEET_FILENAME_TEMPLATE = "spreadsheets_backups/level_{name}.csv"
OUTPUT_YML = "levels.yml"

# URL to the root spreadsheet with a template for the GID, which is fetched
# from the ToC tab
BASE_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "16pJ0JVJ1VOictFhZKmA3dBeFgfAgGcpTTCFIojBuRGA/"
    "export?format=csv&gid={gid}"
)


# for formatting the level data in the yaml file more readably
class literal_str_pipe(str):
    pass


def change_style(style, representer):
    def new_representer(dumper, data):
        scalar = representer(dumper, data)
        scalar.style = style
        return scalar
    return new_representer


REPRESENT_LITERAL_STR = change_style('|', SafeRepresenter.represent_str)
yaml.add_representer(literal_str_pipe, REPRESENT_LITERAL_STR)


def download_file_at(
        url,
        to_filename,
        download=True
):
    if not download:
        print(f"Would have downloaded {to_filename}")
        return to_filename

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(to_filename, 'wb') as fo:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                fo.write(chunk)

    return to_filename


def write_yaml(thing_to_serialize, outpath):
    with open(outpath, 'w') as fo:
        fo.write(yaml.dump(thing_to_serialize))


def read_csv(filename, as_list=False):
    # parse the CSV file
    result = []
    with open(filename, 'r') as fi:
        r = csv.reader(fi, delimiter=",")
        for row in r:
            # flatten out single item lists
            result.append(row)

    return result


def _parsed_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-d',
        '--download',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Whether or not to download new files.'
    )
    return parser.parse_args()


def main():
    args = _parsed_args()

    # download the TOC
    download_file_at(
        # TOC is always at GID 0
        BASE_URL.format(gid=0),
        TOC_FILENAME,
        args.download,
    )

    # skip the header row
    order = read_csv(TOC_FILENAME, as_list=True)[1:]

    result = {
        'level_order': [name for name, _ in order],
        'levels': {}
    }

    # download the level CSV files
    for lvlname, gid in order:
        if gid == "#NAME?":
            raise RuntimeError(
                f"Gid is {gid}, which suggests a google sheets error."
                "  Try loading the spreadsheet interactively and jiggling "
                "the handle on it."
            )

        fname = SHEET_FILENAME_TEMPLATE.format(name=lvlname)

        print(f"downloading: {fname}")

        download_file_at(
            BASE_URL.format(gid=gid),
            fname,
            args.download,
        )

        lvl_dat = read_csv(fname)

        lvl_lst = []
        for row in lvl_dat:
            if not row:
                continue
            row_str = ""
            for c in row:
                if c == "":
                    row_str += "."
                else:
                    row_str += c

            lvl_lst.append(row_str)

        result['levels'][lvlname] = literal_str_pipe("\n".join(lvl_lst))

    write_yaml(result, OUTPUT_YML)
    print(f"wrote: {OUTPUT_YML}")


if __name__ == "__main__":
    main()
