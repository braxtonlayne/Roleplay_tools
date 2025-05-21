import discord
from discord.ext import commands

class WalletSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.command(name="balance")
    async def balance(self, ctx, currency: str = None):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        user_id = str(ctx.author.id)
        if user_id not in guild_data["wallets"]:
            guild_data["wallets"][user_id] = {cur: 0 for cur in guild_data["currencies"]}
        
        if currency:
            if currency not in guild_data["currencies"]:
                await ctx.send(f"Currency {currency} does not exist.")
                return
            balance = guild_data["wallets"][user_id][currency]
            await ctx.send(f"Your balance for {currency}: {balance} {guild_data['currencies'][currency]['symbol']}")
        else:
            embed = discord.Embed(title=f"Wallet Balance for {ctx.author.name}", color=discord.Color.green())
            for cur, amount in guild_data["wallets"][user_id].items():
                embed.add_field(name=cur, value=f"{amount} {guild_data['currencies'][cur]['symbol']}")
            await ctx.send(embed=embed)

    @commands.command(name="pay")
    async def pay(self, ctx, recipient: discord.Member, amount: float, currency: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if currency not in guild_data["currencies"]:
            await ctx.send(f"Currency {currency} does not exist.")
            return
        
        sender_id, recipient_id = str(ctx.author.id), str(recipient.id)
        if sender_id not in guild_data["wallets"]:
            guild_data["wallets"][sender_id] = {cur: 0 for cur in guild_data["currencies"]}
        if recipient_id not in guild_data["wallets"]:
            guild_data["wallets"][recipient_id] = {cur: 0 for cur in guild_data["currencies"]}
        
        if guild_data["wallets"][sender_id][currency] < amount:
            await ctx.send("Insufficient funds.")
            return
        
        guild_data["wallets"][sender_id][currency] -= amount
        guild_data["wallets"][recipient_id][currency] += amount
        await ctx.send(f"Transferred {amount} {guild_data['currencies'][currency]['symbol']} to {recipient.name}")
