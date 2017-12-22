import logging
from random import SystemRandom as random

# from crabigator.wanikani import WaniKani
from wanikani_lib import WaniKani
import utils


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
        self.key = utils.load_api_config('secrets.yaml')['wanikani']
        self.wk = WaniKani(self.key)
        self.combined = []
        self.kanji = []
        self.radicals = []
        self.vocabulary = []

        self.data_set_names = ["kanji", "radicals", "vocabulary", "critical_items"]
        self.load_data_set()  # load all relevant items from wanikani and label them


    def label_items(self, name):
        for _item in getattr(self, name):
                _item.API_type = name

    def load_item(self, name, api_name=None):
        if api_name is None:
            api_name = name
        setattr(self, name, getattr(self.wk, api_name))
        self.label_items(name)

    def load_data_set(self):
        for item_name in self.data_set_names:
            self.load_item(item_name)
            self.combined += getattr(self, item_name)

    def randomise_data_set(self):
        random().shuffle(self.combined)
        for _item in self.data_set_names:
            random().shuffle(getattr(self, _item))


class WaniKaniDataError(Exception):
    """Errors returned by the WaniKani API itself.

    Contains all of the information in the "error" field returned by the API.
    """

    def __init__(self, msg):
        super(WaniKaniDataError, self).__init__('{m}'.format(m=msg))
        self.message = msg


class QuestionPool:

    def __init__(self, data_set):
        self.index = 0
        self.wani = data_set
        """:type : WaniKaniData"""
        self.current_pool = []


    def inc_index(self):

        if self.index < len(self.wani.combined) - 1:
            self.index += 1
        else:
            self.index = 0

    def dec_index(self):

        if self.index == 0:
            self.index = len(self.wani.combined) - 1
        else:
            self.index -= 1

    def next(self):

        if self.index == len(self.wani.combined)-1:
            # At end of data
            return "End"
        else:
            self.inc_index()
            return self.current_pool[self.index]

    def previous(self):
        if self.index == 0:
            # At start of data
            return "Start"
        else:
            self.dec_index()
            return self.current_pool[self.index]

    def current(self):
        return self.current_pool[self.index]

    def populate_pool(self, desired_types):
        if type(desired_types) == str:
            desired_types = [desired_types]

        for desired_type in desired_types:
            for _item in self.wani.combined:
                if _item.API_type == desired_type:
                    self.current_pool.append(_item)
        self.index = 0  # reset index when changing pool

    def randomize_pool(self):
        random().shuffle(self.current_pool)

if __name__ == '__main__':
    wani = WaniKaniData()
    #data = wani.seperate()
    wani.randomise_data_set()

    pool = QuestionPool(wani)
    a = []

    for item in wani.combined:
        if item.API_type == "critical_items":
            a.append(item)
    print('Done')

