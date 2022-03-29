import os
import json
import logging


def load_json(json_file):
    # This is a safeguard, it should never raise as we check this in the CLI.
    if not os.path.isfile(json_file):
        raise Exception(f"File path {json_file} does not exist. "
                        f"Please provide a correct one")
    try:
        with open(json_file, encoding='utf-8') as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        raise Exception(f"File in path {json_file} is not a correctly encoded JSON.")
    return data


class ImportantLogsFilter(logging.Filter):
    """ Logging filter used to only keep important messages which will be
    written to the log file """
    def filter(self, record):
        return record.getMessage().startswith('Important:')


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def clear(cls):
        # We need this for testing purposes!
        try:
            del Singleton._instance
        except AttributeError:
            pass
