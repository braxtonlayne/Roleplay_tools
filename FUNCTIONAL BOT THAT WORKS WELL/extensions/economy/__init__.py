import json
import os
from .currency import CurrencySystem
from .wallet import WalletSystem
from .item import ItemSystem
from .market import MarketSystem
from .job import JobSystem
from .bank import BankSystem
from .resource import ResourceSystem
from .crafting import CraftingSystem
from .tax import TaxSystem
from .loan import LoanSystem
from .analytics import AnalyticsSystem
from .permissions import PermissionSystem
from .config import ConfigSystem

class EconomySystem:
    def __init__(self, bot):
        self.bot = bot
        self.currency = CurrencySystem(self)
        self.wallet = WalletSystem(self)
        self.item = ItemSystem(self)
        self.market = MarketSystem(self)
        self.job = JobSystem(self)
        self.bank = BankSystem(self)
        self.resource = ResourceSystem(self)
        self.crafting = CraftingSystem(self)
        self.tax = TaxSystem(self)
        self.loan = LoanSystem(self)
        self.analytics = AnalyticsSystem(self)
        self.permissions = PermissionSystem(self)
        self.config = ConfigSystem(self)
        self.data = {}

    async def save_data(self):
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            if guild_id not in self.data:
                continue
            filename = f'data/economy_{guild_id}.json'
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(self.data[guild_id], f)

    async def load_data(self):
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            filename = f'data/economy_{guild_id}.json'
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    self.data[guild_id] = json.load(f)
            else:
                self.data[guild_id] = {
                    "currencies": {},
                    "wallets": {},
                    "items": {},
                    "markets": {},
                    "jobs": {},
                    "banks": {},
                    "resources": {},
                    "recipes": {},
                    "loans": {},
                    "config": {}
                }

    def get_guild_data(self, guild_id):
        guild_id = str(guild_id)
        if guild_id not in self.data:
            self.data[guild_id] = {
                "currencies": {},
                "wallets": {},
                "items": {},
                "markets": {},
                "jobs": {},
                "banks": {},
                "resources": {},
                "recipes": {},
                "loans": {},
                "config": {}
            }
        return self.data[guild_id]