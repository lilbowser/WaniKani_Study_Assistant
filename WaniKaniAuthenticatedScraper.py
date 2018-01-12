"""
Utility for scraping the portions of WaniKani's website that require a user login

"""
import requests, lxml.html
from contextlib import ContextDecorator
from utils import load_login_config



class AuthedWaniScraper(ContextDecorator):

    def __init__(self):
        """
        Scrape the portions of WaniKani's website that require a user login
        """
        self.s = requests.session()

        self.timeout = 5  # sec
        self.login_url = "https://www.wanikani.com/login"
        self.login_credentials = load_login_config('secrets.yaml')['wanikani']

        self.authenticated = False
        self.authenticate()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.close()


    def authenticate(self):
        login_page = self.s.get(self.login_url)
        login_html = lxml.html.fromstring(login_page.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

        credentials = {**form, **self.login_credentials}
        response = self.s.post(self.login_url, data=credentials)

        # TODO: check response to ensure authentication was successful.
        self.authenticated = True

    def scrape_page(self, url):
        page_response = self.s.get(url, timeout=self.timeout)
        # html = lxml.html.fromstring(page_response.text)

        # print('')
        return page_response.text


# class ContextMan:
#
#     def __init__(self):
#
#         self.cr = [1, 2, 3, 4, 5]
#         print('ContextMan has been initialized')
#
#     def __enter__(self):
#
#         print('ContextMan has been entered')
#         return self
#
#     def __exit__(self, type, value, traceback):
#
#         print('ContextMan has been exited')
#         self.cr = "None"


if __name__ == '__main__':
    with AuthedWaniScraper() as wani_scraper:
        print(type(wani_scraper))
        print('Done')
