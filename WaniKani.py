

import logging
import traceback
import time as time_p

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

import utils


class WaniKani:

    user_info = "user_information"
    study_queue = "study-queue"
    level_progression = "level-progression"
    srs_distribution = "srs-distribution"
    recent_unlocks = "recent-unlocks"
    critical_items = "critical-items"
    radicals = "radicals"  # /level
    kanji = "kanji"  # /level
    vocabulary = "vocabulary"  # /level

    def __init__(self):
        self.key = utils.load_api_config('secrets.yaml')['wanikani']

    def scrape_wanikani(self, resource):
        url = "https://www.wanikani.com/api/user/{USER_API_KEY}/{RESOURCE}/".format(USER_API_KEY=self.key, RESOURCE=resource)
        return scrapeSite(url)


def scrapeSite(_url, use_progress_bar=False, retry=10):
    """
    Safely retrieves and returns a website using passed URL.
    If error occurs during retrieval, None will be returned instead
    @param _url: The URL of the website that will be scraped
    @type _url: str
    @param retry: Indicates How many retries are left. Starts at 10 by default.
    @type retry: int
    @return: website html if successful, otherwise None
    @rtype: str | None | requests.Response
    """

    logging.debug("Scraping " + _url)
    try:
        website = requests.get(_url)
    except requests.Timeout as e:
        website = None
        if retry > 0:
            logging.warning("Retry #{}".format(11 - retry))
            time_p.sleep(0.25 * (11 - retry))
            retry_scrape = scrapeSite(_url, retry=(retry - 1))
            try:
                data = retry_scrape.text
            except:
                data = retry_scrape
            return data
        else:
            logging.error(traceback.format_exc())
            raise requests.Timeout
    except Exception as error:
        website = None
        # printTKMSG("Uncaught Exception in scrapePlex", traceback.format_exc())

        if retry > 0:
            logging.warning("Retry #{}".format(11 - retry))
            time_p.sleep(0.33 * (11 - retry))
            retry_scrape = scrapeSite(_url, retry=(retry - 1))
            try:
                data = retry_scrape.text
            except:
                data = retry_scrape
            return data
        else:
            logging.error(traceback.format_exc())
            raise requests.RequestException

    if website is not None:
        website_data = website.text
    else:
        website_data = None

    return website_data


if __name__ == '__main__':
    wanikani = WaniKani()


