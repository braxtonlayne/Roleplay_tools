import discord
from discord.ext import commands
from datetime import datetime

class ResourceSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="resource", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def resource(self, ctx):
        """Resource management commands"""
        await ctx.send("Available commands: create, info")

    @resource.command(name="create")
    async def resource_create(self, ctx, name: str, regen_rate: float, max_amount: float):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name in guild_data["resources"]:
            await ctx.send(f"Resource {name} already exists.")
            return
        guild_data["resources"][name] = {
            "amount": max_amount,
            "regen_rate": regen_rate,
            "max_amount": max_amount,
            "last_update": datetime.now().isoformat()
        }
        await ctx.send(f"Resource {name} created with regen rate {regen_rate} and max amount {max_amount}.")

    @resource.command(name="info")
    async def resource_info(self, ctx, name: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["resources"]:
            await ctx.send(f"Resource {name} does not exist.")
            return
        resource = guild_data["resources"][name]
        self.update_resource(guild_data, name)
        embed = discord.Embed(title=f"Resource Info: {name}", color=discord.Color.blue())
        embed.add_field(name="Amount", value=f"{resource['amount']:.2f}")
        embed.add_field(name="Regeneration Rate", value=f"{resource['regen_rate']:.2f}")
        embed.add_field(name="Maximum Amount", value=f"{resource['max_amount']:.2f}")
        await ctx.send(embed=embed)

    @commands.command(name="gather")
    async def gather(self, ctx, resource: str, amount: float):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if resource not in guild_data["resources"]:
            await ctx.send(f"Resource {resource} does not exist.")
            return
        self.update_resource(guild_data, resource)
        if guild_data["resources"][resource]["amount"] < amount:
            await ctx.send("Not enough of this resource available.")
            return
        user_id = str(ctx.author.id)
        if "inventories" not in guild_data:
            guild_data["inventories"] = {}
        if user_id not in guild_data["inventories"]:
            guild_data["inventories"][user_id] = {}
        guild_data["resources"][resource]["amount"] -= amount
        guild_data["inventories"][user_id][resource] = guild_data["inventories"][user_id].get(resource, 0) + amount
        await ctx.send(f"Gathered {amount} {resource}.")

    def update_resource(self, guild_data, resource):
        now = datetime.now()
        last_update = datetime.fromisoformat(guild_data["resources"][resource]["last_update"])
        elapsed_time = (now - last_update).total_seconds() / 60  # Convert to minutes
        regen_amount = guild_data["resources"][resource]["regen_rate"] * elapsed_time
        guild_data["resources"][resource]["amount"] = min(
            guild_data["resources"][resource]["amount"] + regen_amount,
            guild_data["resources"][resource]["max_amount"]
        )
        guild_data["resources"][resource]["last_update"] = now.isoformat()
