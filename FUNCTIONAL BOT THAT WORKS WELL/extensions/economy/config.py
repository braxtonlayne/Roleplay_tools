import discord
from discord.ext import commands

class ConfigSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.command(name="ecoconfig")
    @commands.has_permissions(administrator=True)
    async def ecoconfig(self, ctx, parameter: str, value: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if "config" not in guild_data:
            guild_data["config"] = {}
        
        if parameter not in ["tax_rate", "loan_interest_rate", "market_fee"]:
            await ctx.send(f"Unknown parameter: {parameter}")
            return
        
        try:
            # Convert value to float for economic parameters
            guild_data["config"][parameter] = float(value)
            await ctx.send(f"Updated {parameter} to {value}")
        except ValueError:
            await ctx.send("Invalid value. Please provide a number.")

    @commands.command(name="ecohook")
    @commands.has_permissions(administrator=True)
    async def ecohook(self, ctx, trigger: str, action: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if "eco_hooks" not in guild_data:
            guild_data["eco_hooks"] = {}
        guild_data["eco_hooks"][trigger] = action
        await ctx.send(f"Created economy hook: {trigger} -> {action}")

    @commands.command(name="show_config")
    @commands.has_permissions(administrator=True)
    async def show_config(self, ctx):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        config = guild_data.get("config", {})
        embed = discord.Embed(title="Economy Configuration", color=discord.Color.blue())
        for key, value in config.items():
            embed.add_field(name=key, value=value)
        await ctx.send(embed=embed)
