import requests
import base64
import time
import random

from nltk.tag import pos_tag
from tweepy.error import TweepError

from auth import api, user_id
from utils import get_arguments
from scraper import (
    initialize_soup,
    select_tags,
    sanitize_text_from_tags,
    identify_statements,
    get_image_link_from_article,
    get_image_from_google,

)

args = get_arguments()


def get_query_codes():
    """
    verifiedfacts.org uses base64 encoded strings in place of
    the categories it uses as context for generating articles
    about a topic.
    """
    codes = {}
    queries = [
        "famous_person",
        "organization",
        "company",
        "government_org",
        "government_person",
        "dangerous_noun",
        "malady",
        "place",
        "event",
        "country",
    ]
    for query in queries:
        codes[query] = base64.b64encode(query.encode("ascii")).decode("utf-8")
    return codes


def get_verified_facts_html(query=None, query_type=None) -> str:
    """
    If called without parameter, generates random article from verifiedfacts.org
    
    Optionally, use both parameters
    :param query: str
    :param query_type: str, must be from list of queries in get_query_codes
    """
    global args
    try:
        query, query_type = args.query, args.type
    except NameError as e:
        pass

    url = f"http://www.verifiedfacts.org"
    if query and query_type:
        query_codes = get_query_codes()
        url += f"/s/{query}?c={query_codes[query_type]}"
        images = get_image_from_google(args.query)
    else:
        images = None
    r = requests.get(url)
    r.raise_for_status()
    return r.text, images


def get_statements_from_html(article):
    soup = initialize_soup(article)
    p_tags = select_tags(soup, "p")
    statements = sanitize_text_from_tags(p_tags)
    data = identify_statements(statements)

    img = get_image_link_from_article(soup)
    data["img_url"] = img[0].attrs["src"].strip()
    return data


def get_last_tweet(client):
    return client.user_timeline(id=user_id, count=1)[0]


def handle_tweet_too_long(s: str) -> list:
    sentences = [l.strip() + "." for l in s.split(".")]
    for status in sentences:
        if len(status) > 1:
            api.update_status(status)
        else:
            return


def replace_proper_nouns_with_hashtag(s: str) -> str:
    tagged_sent = pos_tag(s.split())
    proper_nouns = [word for word, pos in tagged_sent if pos == "NNP"]
    for nnp in proper_nouns:
        s = s.replace(nnp, f"#{nnp}")
    return s


def replace_proper_nouns_with_hashtag_new(s: str) -> str:
    tagged_sent = pos_tag(s.split())
    proper_nouns = [word for word, pos in tagged_sent if pos == "NNP"]
    for nnp in proper_nouns:
        s = s.replace(nnp, f"#{nnp}")
    return s


if __name__ == "__main__":

    if not args.test:
        html, images = get_verified_facts_html()
        data = get_statements_from_html(html)
        if images:
            data["local_images"] = images

        for tweet in data["all"]:
            try:
                filename = random.choice(data["local_images"])
            except KeyError as e:
                filename = None
            status = tweet
            status = replace_proper_nouns_with_hashtag(status)
            if len(status) > 280:
                handle_tweet_too_long(status)
            else:
                print(f"Attempting to post")
                print(status)
                if filename:
                    print(filename)
                    api.update_with_media(filename=filename, status=status)
                else:
                    try:
                        api.update_status(status)
                    except TweepError:
                        pass
                print("Posted\n")
                time.sleep(10)
