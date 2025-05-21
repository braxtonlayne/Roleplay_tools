import discord
from discord.ext import commands

class ItemSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="item", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def item(self, ctx):
        """Item management commands"""
        await ctx.send("Available commands: create, info")

    @item.command(name="create")
    async def item_create(self, ctx, name: str, *properties):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name in guild_data["items"]:
            await ctx.send(f"Item {name} already exists.")
            return
        guild_data["items"][name] = {prop.split('=')[0]: prop.split('=')[1] for prop in properties}
        await ctx.send(f"Item {name} created with properties: {', '.join(properties)}")

    @item.command(name="info")
    async def item_info(self, ctx, name: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["items"]:
            await ctx.send(f"Item {name} does not exist.")
            return
        item = guild_data["items"][name]
        embed = discord.Embed(title=f"Item Info: {name}", color=discord.Color.blue())
        for prop, value in item.items():
            embed.add_field(name=prop, value=value)
        await ctx.send(embed=embed)

    @commands.command(name="inventory")
    async def inventory(self, ctx):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        user_id = str(ctx.author.id)
        if "inventories" not in guild_data:
            guild_data["inventories"] = {}
        if user_id not in guild_data["inventories"]:
            guild_data["inventories"][user_id] = {}
        
        embed = discord.Embed(title=f"Inventory for {ctx.author.name}", color=discord.Color.gold())
        for item, amount in guild_data["inventories"][user_id].items():
            embed.add_field(name=item, value=amount)
        await ctx.send(embed=embed)

    @commands.command(name="give")
    @commands.has_permissions(administrator=True)
    async def give(self, ctx, user: discord.Member, item: str, amount: int):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if item not in guild_data["items"]:
            await ctx.send(f"Item {item} does not exist.")
            return
        
        if "inventories" not in guild_data:
            guild_data["inventories"] = {}
        user_id = str(user.id)
        if user_id not in guild_data["inventories"]:
            guild_data["inventories"][user_id] = {}
        
        guild_data["inventories"][user_id][item] = guild_data["inventories"][user_id].get(item, 0) + amount
        await ctx.send(f"Gave {amount} {item} to {user.name}")
