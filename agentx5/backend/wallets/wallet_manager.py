# wallet_manager stub: for MetaMask/Phantom integration you will later point to secure HSM or hardware wallet.
class WalletManager:
    def __init__(self):
        self.wallets = {}
    def add_wallet(self, name, info):
        self.wallets[name]=info
    def get_balance(self, name):
        return "sandbox-only"
