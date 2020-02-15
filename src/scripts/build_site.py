import html
import os
import re
import shutil
from configparser import RawConfigParser
from glob import glob
from json import dumps
from time import strptime
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

JINJA_ENVIRONMENT = Environment(
    loader=FileSystemLoader("src/templates")
)


def delete_output_file_space():
    shutil.rmtree("comic", ignore_errors=True)
    if os.path.isfile("index.html"):
        os.remove("index.html")


def setup_output_file_space():
    # Clean workspace, i.e. delete old files
    delete_output_file_space()
    # Create directories if needed
    os.makedirs("comic", exist_ok=True)


def read_info(filepath, to_dict=False):
    with open(filepath) as f:
        info_string = f.read()
    if not re.search("^\[.*?\]", info_string):
        # print(filepath + " has no section")
        info_string = "[DEFAULT]\n" + info_string
    info = RawConfigParser()
    info.optionxform = str
    info.read_string(info_string)
    if to_dict:
        # TODO: Support multiple sections
        if not list(info.keys()) == ["DEFAULT"]:
            raise NotImplementedError("Configs with multiple sections not yet supported")
        return dict(info["DEFAULT"])
    return info


def get_page_info_list(date_format: str) -> List[Dict]:
    page_info_list = []
    for page_path in glob("your_content/comics/*"):
        page_info = read_info("{}/info.ini".format(page_path), to_dict=True)
        page_info["page_name"] = os.path.basename(page_path)
        page_info_list.append(page_info)

    page_info_list = sorted(
        page_info_list,
        key=lambda x: (strptime(x["Post date"], date_format), x["page_name"])
    )
    return page_info_list


def get_ids(comic_list: List[Dict], index):
    first_id = comic_list[0]["page_name"]
    last_id = comic_list[-1]["page_name"]
    return {
        "first_id": first_id,
        "previous_id": first_id if index == 0 else comic_list[index - 1]["page_name"],
        "next_id": last_id if index == (len(comic_list) - 1) else comic_list[index + 1]["page_name"],
        "last_id": last_id
    }


def get_page_title(comic_info: RawConfigParser, page_info: dict):
    return page_info["Title"] + " - " + comic_info.get("Comic Settings", "Comic name")


def get_links_list(comic_info: RawConfigParser):
    link_list = []
    for option in comic_info.options("Links Bar"):
        link_list.append({"name": option, "url": comic_info.get("Links Bar", option)})
    return link_list


def create_comic(comic_info: RawConfigParser, page_info: dict,
                 first_id: str, previous_id: str, next_id: str, last_id: str):
    print("Building page {}...".format(page_info["page_name"]))
    with open("your_content/comics/{}/post.html".format(page_info["page_name"]), "rb") as f:
        post_html = f.read().decode("utf-8")
    return {
        "page_title": get_page_title(comic_info, page_info),
        "links": get_links_list(comic_info),
        "comic_path": "../your_content/comics/{}/{}".format(
            page_info["page_name"],
            page_info["Filename"]
        ),
        "alt_text": html.escape(page_info["Alt text"]),
        "first_id": first_id,
        "previous_id": previous_id,
        "next_id": next_id,
        "last_id": last_id,
        "comic_title": page_info["Title"],
        "post_date": page_info["Post date"],
        "tags": [tag.strip() for tag in page_info["Tags"].strip().split(",")],
        "post_html": post_html
    }


def write_comic_pages(comic_info: RawConfigParser, page_info_list: List[Dict]):
    # Write individual comic pages
    comic_template = JINJA_ENVIRONMENT.get_template("comic.tpl")
    for i, page_info in enumerate(page_info_list):
        comic_dict = create_comic(comic_info, page_info, **get_ids(page_info_list, i))
        with open("comic/{}.html".format(page_info["page_name"]), "wb") as f:
            f.write(bytes(comic_template.render(**comic_dict), "utf-8"))
    # Write index redirect HTML page
    print("Building index page...")
    index_template = JINJA_ENVIRONMENT.get_template("index.tpl")
    index_dict = {
        "comic_title": comic_info.get("Comic Settings", "Comic name"),
        "last_id": page_info_list[-1]["page_name"]
    }
    with open("index.html", "wb") as f:
        f.write(bytes(index_template.render(**index_dict), "utf-8"))


def main():
    # Setup output file space
    setup_output_file_space()
    # Get site-wide settings for this comic
    comic_info = read_info("your_content/comic_info.ini")
    # Get the info for all pages, sorted by Post Date
    page_info_list = get_page_info_list(comic_info.get("Comic Settings", "Date format"))
    print([p["page_name"] for p in page_info_list])
    # Save page_info_list.json file for use by other pages
    with open("comic/page_info_list.json", "w") as f:
        f.write(dumps(page_info_list))
    # Write page info to comic HTML pages
    write_comic_pages(comic_info, page_info_list)


if __name__ == "__main__":
    main()
