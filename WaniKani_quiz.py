"""

https://community.wanikani.com/t/dashboard-userscript-leech-apprentice-and-guru-detail-aka-srs-level-progress/19353/157

'leech-ness': score = NumberWrong/CorrectStreak^1.5
"""

import logging
from random import SystemRandom as random

# from crabigator.wanikani import WaniKani
from wanikani_lib import WaniKani, WaniKaniObject
import utils

from json import load, dump

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

    def __init__(self):
        self.key = utils.load_api_config('secrets.yaml')['wanikani']  # TODO: This should not be hard coded like this.
        self.wk = WaniKani(self.key)

        self.score_tolerance = 1
        self.data_archive_name = "WaniKaniData"

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
        self.load_data_set()  # load all relevant items from wanikani and label them

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
        setattr(self, data_id['name'], getattr(self.wk, api_name))
        self.label_items(data_id['name'])
        self.add_url(data_id)
        self.assign_scores(data_id)


    def load_data_set(self):
        for data_id in self.data_set_ids:
            self.load_item(data_id)
            self.combined += getattr(self, data_id['name'])

    def randomise_data_set(self):
        random().shuffle(self.combined)
        for data_id in self.data_set_ids:
            random().shuffle(getattr(self, data_id['name']))

    def save_data_set_to_disk(self, name):

        with open(self.data_archive_name + '_' + name +'.json', mode='w') as archive:
            data_set = getattr(self, name)
            _data = [obj.dump() for obj in data_set]
            dump(_data, archive, indent=4)

    def load_data_set_from_disk(self, name):
        with open(self.data_archive_name + '_' + name + '.json', mode='r') as archive:
            dict_data_set = load(archive)
            data_set = [WaniKaniObject(load_from_dict=_data) for _data in dict_data_set]
            return data_set

    def save_to_disk(self):
        for data_id in self.data_set_ids:
            self.save_data_set_to_disk(data_id['name'])



    def add_url(self, data_id):
        for item in getattr(self, data_id['name']):
            url = "https://www.wanikani.com/{type}/{slug_name}".format(type=item.type, slug_name=item.character)
            item.url = url


class WaniKaniDataError(Exception):

    def __init__(self, msg):
        super(WaniKaniDataError, self).__init__('{m}'.format(m=msg))
        self.message = msg


class QuestionPool:

    def __init__(self, data_set):
        self.index = 0
        self.wani = data_set
        """:type : WaniKaniData"""
        self.current_pool = []
        self.tolerance = 1


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
    wani = WaniKaniData()
    #data = wani.seperate()
    wani.randomise_data_set()

    pool = QuestionPool(wani)

    pool.populate_pool(['kanji', 'vocabulary'])

    tmp = []

    a = pool.current_pool[0]

    # b = [obj.dump() for obj in pool.current_pool]

    wani.save_to_disk()

    # a = []
    #
    # for item in wani.combined:
    #     if item.API_type == "critical_items":
    #         a.append(item)


    print('Done')

