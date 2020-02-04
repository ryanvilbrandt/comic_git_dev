import glob
import html
import os
from configparser import RawConfigParser
from json import loads


def build_links_bar(comic_info: RawConfigParser):
    link_list = []
    for option in comic_info.options("Links Bar"):
        link_list.append('<a class="link-bar-link" href="{}">{}</a>'.format(
            comic_info.get("Links Bar", option), option)
        )
    return "&nbsp;&nbsp;|&nbsp;&nbsp;".join(link_list)


with open("src/templates/comic.html") as f:
    comic_template = f.read()

comic_info = RawConfigParser()
comic_info.read("your_content/comic_info.ini")

with open("your_content/comics/197/info.json") as f:
    info_json = loads(f.read())

with open("your_content/comics/197/post.html", "rb") as f:
    post_html = f.read().decode("utf-8")

comic_dict = {
    "page_title": info_json["title"] + " - " + comic_info.get("Comic Settings", "Site Name"),
    "links_bar": build_links_bar(comic_info),
    "comic_path": "../your_content/comics/197/" + info_json["filename"],
    "alt_text": html.escape(info_json["alt_text"]),
    "first_id": "197",
    "previous_id": "197",
    "next_id": "199",
    "last_id": "200",
    "comic_title": info_json["title"],
    "post_date": info_json["post_date"],
    "tags": ", ".join(info_json["tags"]),
    "post_html": post_html
}

os.makedirs("comic", exist_ok=True)

with open("comic/197.html", "wb") as f:
    f.write(bytes(comic_template.format(**comic_dict), "utf-8"))
