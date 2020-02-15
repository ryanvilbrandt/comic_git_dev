import html
import os
import re
from collections import OrderedDict
from configparser import RawConfigParser
from glob import glob
from time import strptime
from typing import Dict, List

from jinja2 import Environment, PackageLoader, FileSystemLoader, Template

JINJA_ENVIRONMENT = Environment(
    loader=FileSystemLoader("src/templates")
)


def read_info(filepath):
    with open(filepath) as f:
        info_string = f.read()
    if not re.search("^\[.*?\]", info_string):
        print(filepath + " has no section")
        info_string = "[nosection]\n" + info_string
    info = RawConfigParser()
    info.optionxform = str
    info.read_string(info_string)
    return info


def get_comic_list(date_format: str) -> "OrderedDict[str, RawConfigParser]":
    comic_info_dicts = {}
    for comic_name in glob("your_content/comics/*"):
        comic_info_dicts[os.path.basename(comic_name)] = read_info("{}/info.ini".format(comic_name))

    print(comic_info_dicts.keys())
    comic_info_dicts = OrderedDict(sorted(
        comic_info_dicts.items(),
        key=lambda t: (strptime(t[1].get("nosection", "Post date"), date_format), t[0])
    ))
    print(comic_info_dicts.keys())
    return comic_info_dicts


def get_ids(comic_list: List, index):
    return {
        "first_id": comic_list[0],
        "previous_id": comic_list[0] if index == 0 else comic_list[index - 1],
        "next_id": comic_list[-1] if index == (len(comic_list) - 1) else comic_list[index + 1],
        "last_id": comic_list[-1]
    }


def get_links_list(comic_info: RawConfigParser):
    link_list = []
    for option in comic_info.options("Links Bar"):
        link_list.append({"name": option, "url": comic_info.get("Links Bar", option)})
    return link_list


def create_comic(comic_info: RawConfigParser, page, page_info, first_id, previous_id, next_id, last_id):
    print("Building page {}...".format(page))
    with open("your_content/comics/{}/post.html".format(page), "rb") as f:
        post_html = f.read().decode("utf-8")
    return {
        "page_title": page_info.get("nosection", "Title") + " - " + comic_info.get("Comic Settings", "Comic name"),
        "links": get_links_list(comic_info),
        "comic_path": "../your_content/comics/{}/{}".format(page, page_info.get("nosection", "Filename")),
        "alt_text": html.escape(page_info.get("nosection", "Alt text")),
        "first_id": first_id,
        "previous_id": previous_id,
        "next_id": next_id,
        "last_id": last_id,
        "comic_title": page_info.get("nosection", "Title"),
        "post_date": page_info.get("nosection", "Post date"),
        "tags": [tag.strip() for tag in page_info.get("nosection", "Tags").strip().split(",")],
        "post_html": post_html
    }


def write_comics(comics: Dict[str, Dict]):
    comic_template = JINJA_ENVIRONMENT.get_template("comic.tpl")
    for page_name, comic_dict in comics.items():
        with open("comic/{}.html".format(page_name), "wb") as f:
            f.write(bytes(comic_template.render(**comic_dict), "utf-8"))


def main():
    os.makedirs("comic", exist_ok=True)
    comic_info = read_info("your_content/comic_info.ini")
    comic_info_dicts = get_comic_list(comic_info.get("Comic Settings", "Date format"))
    comic_output_dict = {}
    comic_list = [os.path.basename(comic_name) for comic_name in comic_info_dicts.keys()]
    for i, k in enumerate(comic_list):
        ids = get_ids(comic_list, i)
        comic_output_dict[k] = create_comic(comic_info, k, comic_info_dicts[k], **ids)
    write_comics(comic_output_dict)


if __name__ == "__main__":
    main()
