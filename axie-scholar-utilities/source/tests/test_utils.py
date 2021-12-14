from hexbytes import HexBytes


LOG_FILE_PATH = '/opt/app/'


def cleanup_log_file(file_name):
    """ Cleans up log file to avoid logs leaking from test to test. Called
    at the end of the test as a teardown """
    with open(LOG_FILE_PATH+file_name, 'w') as f:
        f.write('')


async def async_cleanup_log_file(file_name):
    """ Cleans up log file to avoid logs leaking from test to test. Called
    at the end of the test as a teardown """
    with open(LOG_FILE_PATH+file_name, 'w') as f:
        f.write('')


class MockedSignedMsg:

    def __init__(self):
        self.signature = HexBytes(b'123')
