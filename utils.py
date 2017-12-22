import yaml
import os


def load_api_config(config_file_name):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file_name)
    with open(path) as config:
        return yaml.load(config)["api_keys"]
