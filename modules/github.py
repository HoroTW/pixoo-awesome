from datetime import date, datetime
from os import getenv
import requests
from dotenv import load_dotenv
from cachetools import cached, TTLCache
from PIL import Image, ImageDraw

load_dotenv("local.env", verbose=True)

ENDPOINT = "https://api.github.com/graphql"
__github_token = getenv("GITHUB_TOKEN")
assert __github_token is not None, "Did you copy the example.env to local.env?"
assert __github_token != "here_goes_your_token", "Please add your github token to local.env"

HEADERS = {"Authorization": "Bearer " + __github_token}

DEBUG = False
SECONDS_TO_CACHE = 60 * 30 if not DEBUG else 1


@cached(cache=TTLCache(maxsize=1024, ttl=SECONDS_TO_CACHE))
def get_contributions_for_day(user: str, date_to_check: date = datetime.today().date()) -> int:
    """
    Return the number of contributions for a given user on a given day.
    The return is cached for 30 minutes.
    """
    date_to_check = date_to_check.strftime("%Y-%m-%dT00:00:00Z")

    query = f"""
    query {{
        user(login: "{user}") {{
            contributionsCollection(from: "{date_to_check}", to: "{date_to_check}") {{
                totalCommitContributions
            }}
        }}
    }}"""

    req = requests.post(ENDPOINT, json={"query": query}, headers=HEADERS)
    print(f"Requesting data from github should be cached for {SECONDS_TO_CACHE/60 :.1f} minutes")

    if req.status_code != 200:
        raise requests.RequestException(f"Query failed to run - return code: {req.status_code}")

    c_count = req.json()["data"]["user"]["contributionsCollection"]["totalCommitContributions"]
    return c_count


def draw_github_contribution(
    base: Image,
    username: str,
    required_contributions=1,
    colors=((0, 255, 0, 255), (255, 0, 0, 255), (255, 255, 0, 255)),  # green, red, yellow
    position=(31, 0),
):
    """
    Draw a github contribution pixel on position x, y it shows if you have
    reached your daily contribution goal.

    Colors is a dict with the following keys:
    - good, bad, error   with the default green, red, yellow\n
    You can define your own colors the values are RGBA tuples.
    """
    good, bad, error = colors

    try:
        if get_contributions_for_day(username) >= required_contributions:
            ImageDraw.Draw(base).point(position, fill=(good))
        else:
            ImageDraw.Draw(base).point(position, fill=(bad))
    except requests.RequestException:
        ImageDraw.Draw(base).point(position, fill=(error))
