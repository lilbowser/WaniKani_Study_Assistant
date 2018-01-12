"""

https://community.wanikani.com/t/dashboard-userscript-leech-apprentice-and-guru-detail-aka-srs-level-progress/19353/157

'leech-ness': score = NumberWrong/CorrectStreak^1.5
"""

import logging
from random import SystemRandom as random

# from crabigator.wanikani import WaniKani
from wanikani_lib import WaniKani, WaniKaniObject
from WaniKaniAuthenticatedScraper import AuthedWaniScraper

import utils

from json import load, dump
from copy import deepcopy
import os
from datetime import datetime, timedelta


class WaniKaniData:
    """Wrapper for crabigator WaniKani library"""

    # user_info = "user_information"
    # study_queue = "study_queue"
    # level_progression = "level_progression"
    # srs_distribution = "srs_distribution"
    # recent_unlocks = "recent_unlocks"
    # critical_items = "critical_items"
    # radicals = "radicals"
    # kanji = "kanji"
    # vocabulary = "vocabulary"

    def __init__(self, load_from_disk=False, scraper=None):
        self._log = logging.getLogger(self.__class__.__name__)
        self.key = utils.load_api_config('secrets.yaml')['wanikani']  # TODO: This should not be hard coded like this.

        self.scraper = scraper
        """:type : AuthedWaniScraper"""

        self.score_tolerance = 1
        self.data_archive_name = "WaniKaniData"

        self.http_cache_time = 14  # Days

        self.combined = []
        self.kanji = []
        self.radicals = []
        self.vocabulary = []

        self.data_set_ids = [
            {"name": "kanji"},
            {"name": "radicals"},
            {"name": "vocabulary"},
            {"name": "critical_items",
             "argument": 90  # Gets crit items < 90
             }
        ]

        self.assist_details_section = [
            {'name': 'skip', 'default': False},
            {'name': 'meaning_correct', 'default': 0},
            {'name': 'meaning_current_streak', 'default': 0},
            {'name': 'meaning_incorrect', 'default': 0},
            {'name': 'meaning_max_streak', 'default': 0},
            {'name': 'reading_correct', 'default': 0},
            {'name': 'reading_current_streak', 'default': 0},
            {'name': 'reading_incorrect', 'default': 0},
            {'name': 'reading_max_streak', 'default': 0},
            {'name': 'last_seen', 'default': datetime.fromtimestamp(0)},
            {'name': 'html', 'default': None},
            {'name': 'html_last_updated', 'default': datetime.fromtimestamp(0)}
        ]

        if load_from_disk:
            self.load_from_disk()
            self.wk = None
        else:
            self.wk = WaniKani(self.key)
            self.load_data_set()  # load all relevant items from wanikani and label them

    # --- Item Loading --- #
    def add_wani_assistant_score_section(self, data_id):
        for item in getattr(self, data_id['name']):
            if not hasattr(item, 'wani_assist_details'):
                item.wani_assist_details = WaniKaniObject()

            for section_item in self.assist_details_section:
                if not hasattr(item.wani_assist_details, section_item['name']):
                    setattr(item.wani_assist_details, section_item['name'], section_item['default'])

                # item.wani_assist_details.skip = False
                # item.wani_assist_details.meaning_correct = 0
                # item.wani_assist_details.meaning_current_streak = 0
                # item.wani_assist_details.meaning_incorrect = 0
                # item.wani_assist_details.meaning_max_streak = 0
                # item.wani_assist_details.reading_correct = 0
                # item.wani_assist_details.reading_current_streak = 0
                # item.wani_assist_details.reading_incorrect = 0
                # item.wani_assist_details.reading_max_streak = 0
                # item.wani_assist_details.last_seen = datetime.fromtimestamp(0)
                # item.wani_assist_details.html = None
                # item.wani_assist_details.html_last_updated = datetime.fromtimestamp(0)


    def label_items(self, name):
        for _item in getattr(self, name):
                _item.API_type = name

    def assign_scores(self, data_id):
        for item in getattr(self, data_id['name']):
            item.needs_help = False
            if item.type == 'radicals':
                continue

            if item.user_specific is None:
                # Ensures the item has been shown to user
                continue

            if item.user_specific.meaning_incorrect is None or item.user_specific.meaning_current_streak is None or \
                            item.user_specific.reading_incorrect is None or item.user_specific.meaning_current_streak is None:
                # if any of these are None, than the item is very new and has not been learned at all.
                item.needs_help = True
                continue

            item.meaning_score = (item.user_specific.meaning_incorrect + 3) / ((item.user_specific.meaning_current_streak + 1) ** 1.5)
            item.reading_score = (item.user_specific.reading_incorrect + 3) / ((item.user_specific.meaning_current_streak + 1) ** 1.5)

            if 0 <= item.meaning_score < self.score_tolerance and 0 <= item.reading_score < self.score_tolerance:
                # This indicates not leach
                continue
            item.needs_help = True

    def load_item(self, data_id, api_name=None):
        """
        Retrives data from WaniKani endpoint specified by a data_id
        :param data_id: A data_id from self.data_set_ids
        :type data_id: dict
        :param api_name:
        :type api_name:
        :return:
        :rtype:
        """
        if api_name is None:
            api_name = data_id['name']

        #  Does self.kanji = self.wk.kanji For all data items
        setattr(self, data_id['name'], getattr(self.wk, api_name))  # Should this be a copy?

        self.label_items(data_id['name'])
        self.add_url(data_id)
        self.assign_scores(data_id)
        self.add_wani_assistant_score_section(data_id)

    def load_data_set(self):
        for data_id in self.data_set_ids:
            self.load_item(data_id)
            self.combined += getattr(self, data_id['name'])

    def randomise_data_set(self):
        random().shuffle(self.combined)
        for data_id in self.data_set_ids:
            random().shuffle(getattr(self, data_id['name']))

    def save_data_set_to_disk(self, name):
        #TODO: Save data to temp file then rename/cp so we do not lose data if the dump fails
        with open("data/" + self.data_archive_name + '_' + name +'.json', mode='w') as archive:
            data_set = getattr(self, name)
            _data = [obj.dump(html=True) for obj in data_set]
            dump(_data, archive, indent=4)

    def load_data_set_from_disk(self, name):
        try:
            file_path = "data/" + self.data_archive_name + '_' + name + '.json'
            with open(file_path, mode='r') as archive:
                if os.stat(file_path).st_size < 10:
                    self._log.error('File empty when loading')
                    return []
                dict_data_set = load(archive)
                data_set = [WaniKaniObject(load_from_dict=_data) for _data in dict_data_set]
                return data_set
        except FileNotFoundError as e:
            self._log.error('File not found when loading')
            return []

    def save_to_disk(self):
        self._log.warning('Saving data to disk!')
        for data_id in self.data_set_ids:
            self.save_data_set_to_disk(data_id['name'])

    def load_from_disk(self):
        for data_id in self.data_set_ids:
            data = self.load_data_set_from_disk(data_id['name'])
            setattr(self, data_id['name'], data)

    def add_url(self, data_id):
        for item in getattr(self, data_id['name']):
            url = "https://www.wanikani.com/{type}/{slug_name}".format(type=item.type, slug_name=item.character)
            item.url = url

    # def merge_data(self, new_data):
    #     """
    #     Merge the wani_assist_details from
    #     :param new_data:
    #     :type new_data:
    #     :return:
    #     :rtype:
    #     """
    #     for data_id in self.data_set_ids:
    #         if data_id['name'] == "kanji":
    #             for disk_item in getattr(self, data_id['name']):
    #                 found = False
    #                 for new_item in getattr(new_data, data_id['name']):
    #                     if disk_item == new_item:
    #                         print("Copy over data that is to be saved")
    #                         found = True
    #                         break
    #                 if not found:
    #                     # Copy over entire old object?
    #                     print("Copy over entire old object?")

    def merge_archived_data_into_new_data(self, archived_data):
        """
        Merge the wani_assist_details from the archived data into the new data pulled from WaniKani

        :param archived_data: The archived data that was loaded from disk
        :type archived_data: WaniKaniData
        :return:
        :rtype:
        """

        """
        We are operating in freshly scraped data. 
        Prioritise wani_assist_details from archived data
        Prioritise all others from fresh data
        """
        for data_id in self.data_set_ids:
            # if data_id['name'] == "kanji":  # TODO: Should not be needed

                for fresh_item in getattr(self, data_id['name']):
                    found = False
                    for archived_item in getattr(archived_data, data_id['name']):

                        if fresh_item == archived_item:
                            # Copy wani_assist_details to fresh_item
                            try:
                                fresh_item.wani_assist_details = deepcopy(archived_item.wani_assist_details)

                                # Rerun the add section function to add any new sections not in the archive.
                                self.add_wani_assistant_score_section(data_id)
                            except AttributeError:
                                pass
                            found = True
                            break
                    if not found:
                        # Nothing to be done as there is no archived data to be copied over.
                        nice_string = "char: {} ({}), API: {}".format(fresh_item.character, fresh_item.meaning[0], fresh_item.api)
                        self._log.info("No match found for " + nice_string)

    # --- Item Modifications --- #

    def find_item(self, item):  # TODO: If we handle all the different copies by reference, which we do, than we dont need this.
        """

        :param item:
        :type item: WaniKaniObject
        :return:
        :rtype:
        """
        data_set = getattr(self, item.api)
        for data in data_set:
            if item == data:
                return data

    def set_assist_scores(self, item, question_kind, is_correct):
        """
        Used to set the scores for WaniStudyAssistance

        :param item: The item that needs to be updated
        :type item: WaniKaniObject
        :param question_kind: 'meaning' or 'reading'
        :type question_kind: str
        :param is_correct: Did the user get the question correct
        :type is_correct: bool
        :return:
        :rtype:
        """

        matched_item = self.find_item(item)
        #TODO: Finish


    def update_website(self, item):
        if (datetime.now() - item.wani_assist_details.html_last_updated) > timedelta(days=self.http_cache_time):
            print("Time to get new webpage")

            html = self.scraper.scrape_page(item.url)
            item.wani_assist_details.html = html
            self.save_to_disk()


class WaniKaniDataError(Exception):

    def __init__(self, msg):
        super(WaniKaniDataError, self).__init__('{m}'.format(m=msg))
        self.message = msg


class QuestionPool:

    def __init__(self, scraper=None):
        self.index = 0
        self.wani = WaniKaniData(scraper=scraper)
        """:type : WaniKaniData"""
        self.wani.randomise_data_set()  # TODO: This should not be needed.

        self.current_pool = []
        self.tolerance = 1

        self.archived_wani = WaniKaniData(load_from_disk=True)
        self.wani.merge_archived_data_into_new_data(self.archived_wani)
        self.wani.save_to_disk()


    def inc_index(self):

        if self.index < len(self.current_pool) - 1:
            self.index += 1
        else:
            self.index = 0

    def dec_index(self):

        if self.index == 0:
            self.index = len(self.current_pool) - 1
        else:
            self.index -= 1

    def next(self):

        if self.index == len(self.current_pool)-1:
            # At end of data
            return "end"
        else:
            self.inc_index()
            return self.current_pool[self.index]

    def previous(self):
        if self.index == 0:
            # At start of data
            return "start"
        else:
            self.dec_index()
            return self.current_pool[self.index]

    def current(self):
        return self.current_pool[self.index]

    def populate_pool(self, desired_types, only_needs_help=True):
        """
        Adds items to the pool whose API type matches the given 'desired_types'.
        :param desired_types: Can be either a single string or a list of strings.
        :type desired_types: str | list[str]
        """
        self.current_pool.clear()  # Empty the pool first
        if type(desired_types) == str:
            desired_types = [desired_types]

        for desired_type in desired_types:
            for _item in self.wani.combined:
                if _item.API_type == desired_type and _item.user_specific is not None:
                    if only_needs_help == True and _item.needs_help == True:
                        self.current_pool.append(_item)
        self.index = 0  # reset index when changing pool

    def randomize_pool(self):
        random().shuffle(self.current_pool)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING,
                        format="[%(asctime)s] %(name)s: %(funcName)s:%(lineno)d %(levelname)s:-8s %(message)s",
                        datefmt='%m-%d %H:%M:%S')#,
                        # filename='Package_Tracker.log',
                        # filemode='w')

    with AuthedWaniScraper() as wani_scraper:

        pool = QuestionPool(wani_scraper)

        pool.populate_pool(['kanji']) #, 'vocabulary'

        tmp = []

        a = pool.current_pool[0]
        # pool.wani.update_website(a)


        # b = [obj.dump() for obj in pool.current_pool]

        # wani.save_to_disk()

        # a = []
        #
        # for item in wani.combined:
        #     if item.API_type == "critical_items":
        #         a.append(item)


        print('Done')

