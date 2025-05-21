import discord
from discord.ext import commands

class PermissionSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.command(name="ecorole")
    @commands.has_permissions(administrator=True)
    async def ecorole(self, ctx, user: discord.Member, role: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if "eco_roles" not in guild_data:
            guild_data["eco_roles"] = {}
        guild_data["eco_roles"][str(user.id)] = role
        await ctx.send(f"Assigned economic role '{role}' to {user.name}")

    def check_permission(self, ctx, required_role):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        user_id = str(ctx.author.id)
        if "eco_roles" not in guild_data or user_id not in guild_data["eco_roles"]:
            return False
        return guild_data["eco_roles"][user_id] == required_role
