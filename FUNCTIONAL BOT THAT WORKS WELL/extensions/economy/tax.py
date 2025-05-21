import discord
from discord.ext import commands

class TaxSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="tax", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def tax(self, ctx):
        """Tax management commands"""
        await ctx.send("Available commands: set, info")

    @tax.command(name="set")
    async def tax_set(self, ctx, rate: float):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if "config" not in guild_data:
            guild_data["config"] = {}
        guild_data["config"]["tax_rate"] = rate
        await ctx.send(f"Tax rate set to {rate}.")

    @tax.command(name="info")
    async def tax_info(self, ctx):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        tax_rate = guild_data.get("config", {}).get("tax_rate", 0)
        await ctx.send(f"Current tax rate: {tax_rate}")

    async def collect_taxes(self):
        for guild in self.bot.guilds:
            guild_data = self.economy.get_guild_data(guild.id)
            tax_rate = guild_data.get("config", {}).get("tax_rate", 0)
            if tax_rate > 0:
                for user_id, wallet in guild_data["wallets"].items():
                    for currency, amount in wallet.items():
                        tax = amount * tax_rate
                        wallet[currency] -= tax
                        guild_data["currencies"][currency]["in_circulation"] -= tax
