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
COMIC_TITLE = ""
BASE_DIRECTORY = os.path.basename(os.getcwd())
LINKS_LIST = []


def path(rel_path: str):
    if rel_path.startswith("/"):
        return "/" + BASE_DIRECTORY + rel_path
    return rel_path


def get_links_list(comic_info: RawConfigParser):
    link_list = []
    for option in comic_info.options("Links Bar"):
        link_list.append({"name": option, "url": path(comic_info.get("Links Bar", option))})
    return link_list


def delete_output_file_space():
    shutil.rmtree("comic", ignore_errors=True)
    for f in ["index.html", "archive.html"]:
        if os.path.isfile(f):
            os.remove(f)


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


def create_comic_data(comic_info: RawConfigParser, page_info: dict,
                 first_id: str, previous_id: str, next_id: str, last_id: str):
    print("Building page {}...".format(page_info["page_name"]))
    with open("your_content/comics/{}/post.html".format(page_info["page_name"]), "rb") as f:
        post_html = f.read().decode("utf-8")
    return {
        "page_name": page_info["page_name"],
        "comic_path": "../your_content/comics/{}/{}".format(
            page_info["page_name"],
            page_info["Filename"]
        ),
        "alt_text": html.escape(page_info["Alt text"]),
        "first_id": first_id,
        "previous_id": previous_id,
        "next_id": next_id,
        "last_id": last_id,
        "page_title": page_info["Title"],
        "post_date": page_info["Post date"],
        "tags": [tag.strip() for tag in page_info["Tags"].strip().split(",")],
        "post_html": post_html
    }


def build_comic_data_dicts(comic_info: RawConfigParser, page_info_list: List[Dict]) -> List[Dict]:
    comic_data_dicts = []
    for i, page_info in enumerate(page_info_list):
        comic_dict = create_comic_data(comic_info, page_info, **get_ids(page_info_list, i))
        comic_data_dicts.append(comic_dict)
    return comic_data_dicts


def write_to_template(template_path, html_path, data_dict):
    template = JINJA_ENVIRONMENT.get_template(template_path)
    with open(html_path, "wb") as f:
        rendered_template = template.render(
            comic_title=COMIC_TITLE,
            base_dir=BASE_DIRECTORY,
            links=LINKS_LIST,
            **data_dict
        )
        f.write(bytes(rendered_template, "utf-8"))


def write_comic_pages(comic_data_dicts: List[Dict], create_index_file=True):
    # Write individual comic pages
    for comic_data_dict in comic_data_dicts:
        html_path = "comic/{}.html".format(comic_data_dict["page_name"])
        write_to_template("comic.tpl", html_path, comic_data_dict)
    if create_index_file:
        # Write index redirect HTML page
        print("Building index page...")
        index_dict = {
            "last_id": comic_data_dicts[-1]["page_name"]
        }
        write_to_template("index.tpl", "index.html", index_dict)


def write_archive_page(comic_info: RawConfigParser, comic_data_dicts: List[Dict]):
    print("Building archive page...")
    archive_sections = []
    for section in comic_info.get("Archive", "Archive sections").strip().split(","):
        section = section.strip()
        pages = [comic_data for comic_data in comic_data_dicts
                 if section in comic_data["tags"]]
        archive_sections.append({
            "name": section,
            "pages": pages
        })
    write_to_template("archive.tpl", "archive.html", {"page_title": "Archive", "archive_sections": archive_sections})


def main():
    global COMIC_TITLE, LINKS_LIST
    # Setup output file space
    setup_output_file_space()
    # Get site-wide settings for this comic
    comic_info = read_info("your_content/comic_info.ini")
    COMIC_TITLE = comic_info.get("Comic Settings", "Comic name")
    LINKS_LIST = get_links_list(comic_info)
    # Get the info for all pages, sorted by Post Date
    page_info_list = get_page_info_list(comic_info.get("Comic Settings", "Date format"))
    print([p["page_name"] for p in page_info_list])
    # Save page_info_list.json file for use by other pages
    with open("comic/page_info_list.json", "w") as f:
        f.write(dumps(page_info_list))
    # Build full comic data dicts, to build templates with
    comic_data_dicts = build_comic_data_dicts(comic_info, page_info_list)
    # Write page info to comic HTML pages
    write_comic_pages(comic_data_dicts)
    write_archive_page(comic_info, comic_data_dicts)


if __name__ == "__main__":
    main()
