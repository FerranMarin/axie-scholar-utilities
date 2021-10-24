LOG_FILE_PATH = '/opt/app/results.log'


def cleanup_log_file():
    """ Cleans up log file to avoid logs leaking from test to test. Called
    at the end of the test as a teardown """
    with open(LOG_FILE_PATH, 'w') as f:
        f.write('')


async def async_cleanup_log_file():
    """ Cleans up log file to avoid logs leaking from test to test. Called
    at the end of the test as a teardown """
    with open(LOG_FILE_PATH, 'w') as f:
        f.write('')
