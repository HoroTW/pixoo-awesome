from datetime import date, datetime
from os import getenv
import requests
from dotenv import load_dotenv
from cachetools import cached, TTLCache
from PIL import Image, ImageDraw
from threading import Thread

load_dotenv("local.env", verbose=True)

ENDPOINT = "https://api.github.com/graphql"
__github_token = getenv("GITHUB_TOKEN")
assert __github_token is not None, "Did you copy the example.env to local.env?"
assert __github_token != "here_goes_your_token", "Please add your github token to local.env"

HEADERS = {"Authorization": "Bearer " + __github_token}

DEBUG = False
SECONDS_TO_CACHE = 0 if DEBUG else 60  # the rate limit is 5000 of this query per hour
USER_CONTRIBUTIONS_DICT = {}
REQ_THREAD: Thread = None


@cached(cache=TTLCache(maxsize=1024, ttl=SECONDS_TO_CACHE))
def fill_contributions_for_day_for_user(user: str, date_to_check: date = None) -> int:
    """
    Fills the `USER_CONTRIBUTIONS_DICT` for the given user with the contributions for the given date.
    The return is cached for 1 minute.
    If date_to_check is None (default case) it will return the contributions for today.
    """
    if date_to_check is None:
        date_to_check = datetime.today()

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
    print(f"Requesting data from github is cached for {SECONDS_TO_CACHE/60 :.1f} minutes")

    if req.status_code != 200:
        raise requests.RequestException(f"Query failed to run - return code: {req.status_code}")

    c_count = req.json()["data"]["user"]["contributionsCollection"]["totalCommitContributions"]
    USER_CONTRIBUTIONS_DICT[user] = c_count


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

    `colors` is a tuple of 3 tuples of the form (r, g, b, a) where the first one is the good color
    the second one is the bad color and the third one is the error color.
    Eg: ( (0, 255, 0, 255), (255, 0, 0, 255), (255, 255, 0, 255) )
    """
    good, bad, error = colors
    global REQ_THREAD

    if REQ_THREAD is None or REQ_THREAD.is_alive() is False:
        REQ_THREAD = Thread(target=fill_contributions_for_day_for_user, args=(username,))
        REQ_THREAD.start()

    eventually_correct_contributions = USER_CONTRIBUTIONS_DICT.get(username, 0)

    try:
        if eventually_correct_contributions >= required_contributions:
            ImageDraw.Draw(base).point(position, fill=(good))
        else:
            ImageDraw.Draw(base).point(position, fill=(bad))
    except requests.RequestException:
        ImageDraw.Draw(base).point(position, fill=(error))
