from trezorlib.ui import ClickUI

class CustomUI(ClickUI):
    def __init__(self, passphrase=None, *args, **kwargs):
        self.passphrase = passphrase
        super().__init__(*args, **kwargs)

    def get_passphrase(self, *args, **kwargs):
        return self.passphrase
