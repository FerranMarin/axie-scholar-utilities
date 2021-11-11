class CustomUI:
    def __init__(self, always_prompt=False, passphrase_on_host=True, passphrase=None):
        self.pinmatrix_shown = False
        self.prompt_shown = False
        self.always_prompt = always_prompt
        self.passphrase_on_host = passphrase_on_host
        self.passphrase = passphrase if passphrase else ""

    def button_request(self, code):
        if not self.prompt_shown:
            print("Please confirm action on your Trezor device.")
        
        print(code)

    def get_pin(self, code=None):
        return None

    def get_passphrase(self, available_on_device):
        return self.passphrase
