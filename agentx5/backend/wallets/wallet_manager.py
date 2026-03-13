class WalletManager:
    def __init__(self):
        self.wallets = {}

    def add_wallet(self, name, info):
        self.wallets[name] = info
        return True

    def get_balance(self, name):
        if name not in self.wallets:
            return None
        return "sandbox-balance: $500.00"

    def list_wallets(self):
        return list(self.wallets.keys())

    def remove_wallet(self, name):
        if name in self.wallets:
            del self.wallets[name]
            return True
        return False
