import requests
from datetime import date, datetime
from os import getenv
from dotenv import load_dotenv
from cachetools import cached, TTLCache
from PIL import Image, ImageDraw

load_dotenv("local.env")

ENDPOINT = 'https://api.github.com/graphql'
HEADERS = {'Authorization': 'Bearer ' + getenv('GITHUB_TOKEN')}

DEBUG = False
SECONDS_TO_CACHE = 60 * 30 if not DEBUG else 1


@cached(cache=TTLCache(maxsize=1024, ttl=SECONDS_TO_CACHE))
def get_contributions_for_day(
    user: str, date: date = datetime.today().date()) -> int:
    """
    Return the number of contributions for a given user on a given day.
    The return is cached for 30 minutes.
    """
    date = date.strftime('%Y-%m-%dT00:00:00Z')

    query = f"""
    query {{
        user(login: "{user}") {{
            contributionsCollection(from: "{date}", to: "{date}") {{
                totalCommitContributions
            }}
        }}
    }}"""

    r = requests.post(ENDPOINT, json={'query': query}, headers=HEADERS)

    if r.status_code != 200:
        raise Exception(f"Query failed to run - return code: {r.status_code}")

    r = r.json()["data"]
    c_count = r['user']['contributionsCollection']['totalCommitContributions']
    return c_count


def draw_github_contribution(
        base: Image,
        username: str,
        required_contributions=1,
        colors={
            "good": (0, 255, 0, 255),  # green
            "bad": (255, 0, 0, 255),  # red
            "error": (255, 255, 0, 255)  # yellow
        },
        x=31,
        y=0):
    """
    Draw a github contribution pixel on position x, y it shows if you have
    reached your daily contribution goal.

    Colors is a dict with the following keys:
    - good, bad, error   with the default green, red, yellow\n
    You can define your own colors the values are RGBA tuples.
    """

    try:
        if get_contributions_for_day(username) >= required_contributions:
            ImageDraw.Draw(base).point((x, y), fill=(colors["good"]))
        else:
            ImageDraw.Draw(base).point((x, y), fill=(colors["bad"]))
    except:
        ImageDraw.Draw(base).point((x, y), fill=(colors["error"]))