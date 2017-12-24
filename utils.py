import yaml
import os

def load_api_config(config_file_name):
    with open(os.path.dirname(os.path.abspath(__file__)) + config_file_name, 'r') as config:
        return yaml.load(config)["api_keys"]