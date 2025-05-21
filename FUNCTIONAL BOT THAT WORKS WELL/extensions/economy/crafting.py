import discord
from discord.ext import commands

class CraftingSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="recipe", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def recipe(self, ctx):
        """Recipe management commands"""
        await ctx.send("Available commands: create, info, list")

    @recipe.command(name="create")
    async def recipe_create(self, ctx, name: str, *ingredients):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name in guild_data["recipes"]:
            await ctx.send(f"Recipe {name} already exists.")
            return
        recipe = {}
        for i in range(0, len(ingredients), 2):
            item = ingredients[i]
            amount = float(ingredients[i+1])
            recipe[item] = amount
        guild_data["recipes"][name] = recipe
        await ctx.send(f"Recipe {name} created with ingredients: {', '.join(f'{k}: {v}' for k, v in recipe.items())}.")

    @recipe.command(name="info")
    async def recipe_info(self, ctx, name: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["recipes"]:
            await ctx.send(f"Recipe {name} does not exist.")
            return
        recipe = guild_data["recipes"][name]
        embed = discord.Embed(title=f"Recipe Info: {name}", color=discord.Color.blue())
        for item, amount in recipe.items():
            embed.add_field(name=item, value=amount)
        await ctx.send(embed=embed)

    @recipe.command(name="list")
    async def recipe_list(self, ctx):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        embed = discord.Embed(title="Available Recipes", color=discord.Color.blue())
        for name in guild_data["recipes"].keys():
            embed.add_field(name=name, value="Use !recipe info <name> for details", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="craft")
    async def craft(self, ctx, recipe: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if recipe not in guild_data["recipes"]:
            await ctx.send(f"Recipe {recipe} does not exist.")
            return
        user_id = str(ctx.author.id)
        if "inventories" not in guild_data:
            guild_data["inventories"] = {}
        if user_id not in guild_data["inventories"]:
            guild_data["inventories"][user_id] = {}
        for item, amount in guild_data["recipes"][recipe].items():
            if guild_data["inventories"][user_id].get(item, 0) < amount:
                await ctx.send(f"You don't have enough {item} to craft this recipe.")
                return
        for item, amount in guild_data["recipes"][recipe].items():
            guild_data["inventories"][user_id][item] -= amount
        guild_data["inventories"][user_id][recipe] = guild_data["inventories"][user_id].get(recipe, 0) + 1
        await ctx.send(f"Successfully crafted {recipe}.")
