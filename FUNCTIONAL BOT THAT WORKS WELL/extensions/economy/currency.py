import discord
from discord.ext import commands

class CurrencySystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="currency", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def currency(self, ctx):
        """Currency management commands"""
        await ctx.send("Available commands: create, adjust, info")

    @currency.command(name="create")
    async def currency_create(self, ctx, name: str, symbol: str, exchange_rate: float = 1.0):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name in guild_data["currencies"]:
            await ctx.send(f"Currency {name} already exists.")
            return
        guild_data["currencies"][name] = {
            "symbol": symbol,
            "exchange_rate": exchange_rate,
            "total_supply": 0,
            "in_circulation": 0
        }
        await ctx.send(f"Currency {name} ({symbol}) created with exchange rate {exchange_rate}.")

    @currency.command(name="adjust")
    async def currency_adjust(self, ctx, name: str, amount: float):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["currencies"]:
            await ctx.send(f"Currency {name} does not exist.")
            return
        guild_data["currencies"][name]["total_supply"] += amount
        await ctx.send(f"Adjusted {name} supply by {amount}. New total supply: {guild_data['currencies'][name]['total_supply']}")

    @currency.command(name="info")
    async def currency_info(self, ctx, name: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["currencies"]:
            await ctx.send(f"Currency {name} does not exist.")
            return
        currency = guild_data["currencies"][name]
        embed = discord.Embed(title=f"Currency Info: {name}", color=discord.Color.blue())
        embed.add_field(name="Symbol", value=currency["symbol"])
        embed.add_field(name="Exchange Rate", value=currency["exchange_rate"])
        embed.add_field(name="Total Supply", value=currency["total_supply"])
        embed.add_field(name="In Circulation", value=currency["in_circulation"])
        await ctx.send(embed=embed)