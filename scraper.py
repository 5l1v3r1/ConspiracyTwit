from google_images_download import google_images_download
from bs4 import BeautifulSoup
from pathlib import Path


def initialize_soup(src: str) -> BeautifulSoup:
    return BeautifulSoup(src, "html.parser")


def select_tags(s: BeautifulSoup, tag: str):
    return s.findAll([tag])


def sanitize_text_from_tags(tags: list) -> list:
    return [t.text.strip() for t in tags]


def identify_statements(s: list) -> dict:
    return {"title": s[0], "all": s[1:]}


def get_image_link_from_article(s: BeautifulSoup) -> str:
    img_tag = select_tags(s, "img")
    return img_tag


def get_image_from_google(keyword: str):
    keyword = keyword + " conspiracy"
    # Determine if directory folder already exists for keyword
    downloads_dir = Path.home().joinpath("Projects/ConspiracyTwit/downloads")
    subdirs = [d.name for d in downloads_dir.iterdir()]
    # Skip downloading if necessary
    if keyword in subdirs:
        path = downloads_dir / keyword
        return [str(img) for img in path.iterdir()]
    else:
        response = google_images_download.googleimagesdownload()
        arguments = {
            "keywords": keyword,
            "limit": 20,
            "print_urls": True
        }
        arguments = {"keywords": keyword, "limit": 20}
        paths = response.download(arguments)
        return paths[0][keyword]

