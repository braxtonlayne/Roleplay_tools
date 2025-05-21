import discord
from discord.ext import commands

class BankSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="bank", invoke_without_command=True)
    async def bank(self, ctx):
        """Bank management commands"""
        await ctx.send("Available commands: create, deposit, withdraw, balance")

    @bank.command(name="create")
    @commands.has_permissions(administrator=True)
    async def bank_create(self, ctx, name: str, interest_rate: float):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name in guild_data["banks"]:
            await ctx.send(f"Bank {name} already exists.")
            return
        guild_data["banks"][name] = {
            "interest_rate": interest_rate,
            "accounts": {}
        }
        await ctx.send(f"Bank {name} created with interest rate {interest_rate}.")

    @bank.command(name="deposit")
    async def bank_deposit(self, ctx, name: str, amount: float, currency: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["banks"]:
            await ctx.send(f"Bank {name} does not exist.")
            return
        if currency not in guild_data["currencies"]:
            await ctx.send(f"Currency {currency} does not exist.")
            return
        user_id = str(ctx.author.id)
        if user_id not in guild_data["wallets"]:
            guild_data["wallets"][user_id] = {cur: 0 for cur in guild_data["currencies"]}
        if guild_data["wallets"][user_id][currency] < amount:
            await ctx.send("Insufficient funds.")
            return
        if user_id not in guild_data["banks"][name]["accounts"]:
            guild_data["banks"][name]["accounts"][user_id] = {}
        if currency not in guild_data["banks"][name]["accounts"][user_id]:
            guild_data["banks"][name]["accounts"][user_id][currency] = 0
        guild_data["wallets"][user_id][currency] -= amount
        guild_data["banks"][name]["accounts"][user_id][currency] += amount
        await ctx.send(f"Deposited {amount} {currency} into {name}.")

    @bank.command(name="withdraw")
    async def bank_withdraw(self, ctx, name: str, amount: float, currency: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["banks"]:
            await ctx.send(f"Bank {name} does not exist.")
            return
        if currency not in guild_data["currencies"]:
            await ctx.send(f"Currency {currency} does not exist.")
            return
        user_id = str(ctx.author.id)
        if user_id not in guild_data["banks"][name]["accounts"]:
            await ctx.send("You don't have an account in this bank.")
            return
        if currency not in guild_data["banks"][name]["accounts"][user_id]:
            await ctx.send(f"You don't have any {currency} in this bank.")
            return
        if guild_data["banks"][name]["accounts"][user_id][currency] < amount:
            await ctx.send("Insufficient funds in the bank account.")
            return
        guild_data["banks"][name]["accounts"][user_id][currency] -= amount
        guild_data["wallets"][user_id][currency] += amount
        await ctx.send(f"Withdrawn {amount} {currency} from {name}.")

    @bank.command(name="balance")
    async def bank_balance(self, ctx, name: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["banks"]:
            await ctx.send(f"Bank {name} does not exist.")
            return
        user_id = str(ctx.author.id)
        if user_id not in guild_data["banks"][name]["accounts"]:
            await ctx.send("You don't have an account in this bank.")
            return
        embed = discord.Embed(title=f"Bank Balance: {name}", color=discord.Color.green())
        for currency, amount in guild_data["banks"][name]["accounts"][user_id].items():
            embed.add_field(name=currency, value=amount)
        await ctx.send(embed=embed)

    async def process_interest(self):
        for guild in self.bot.guilds:
            guild_data = self.economy.get_guild_data(guild.id)
            for bank_name, bank_data in guild_data["banks"].items():
                for account_id, account in bank_data["accounts"].items():
                    for currency, amount in account.items():
                        interest = amount * bank_data["interest_rate"] / 24  # Hourly interest
                        account[currency] += interest
