from discord.ext import commands
from .economy import (CurrencySystem, WalletSystem, ItemSystem, MarketSystem,
                      JobSystem, BankSystem, ResourceSystem, CraftingSystem,
                      TaxSystem, LoanSystem, AnalyticsSystem, PermissionSystem,
                      ConfigSystem)

class Economy(commands.Cog):
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

    @commands.command(name="eco_test")
    async def eco_test(self, ctx):
        await ctx.send("Economy system is working!")

async def setup(bot):
    await bot.add_cog(Economy(bot))