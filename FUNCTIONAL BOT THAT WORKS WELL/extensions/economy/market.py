import discord
from discord.ext import commands

class MarketSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="market", invoke_without_command=True)
    async def market(self, ctx):
        """Market commands"""
        await ctx.send("Available commands: create, list, buy, browse")

    @market.command(name="create")
    @commands.has_permissions(administrator=True)
    async def market_create(self, ctx, name: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name in guild_data["markets"]:
            await ctx.send(f"Market {name} already exists.")
            return
        guild_data["markets"][name] = {"listings": []}
        await ctx.send(f"Market {name} created.")

    @market.command(name="list")
    async def market_list(self, ctx, market: str, item: str, amount: int, price: float, currency: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if market not in guild_data["markets"]:
            await ctx.send(f"Market {market} does not exist.")
            return
        if item not in guild_data["items"]:
            await ctx.send(f"Item {item} does not exist.")
            return
        if currency not in guild_data["currencies"]:
            await ctx.send(f"Currency {currency} does not exist.")
            return
        
        user_id = str(ctx.author.id)
        if "inventories" not in guild_data:
            guild_data["inventories"] = {}
        if user_id not in guild_data["inventories"]:
            guild_data["inventories"][user_id] = {}
        
        if guild_data["inventories"][user_id].get(item, 0) < amount:
            await ctx.send("You don't have enough of this item to list.")
            return
        
        listing_id = len(guild_data["markets"][market]["listings"])
        guild_data["markets"][market]["listings"].append({
            "id": listing_id,
            "seller": user_id,
            "item": item,
            "amount": amount,
            "price": price,
            "currency": currency
        })
        guild_data["inventories"][user_id][item] -= amount
        await ctx.send(f"Listed {amount} {item} for {price} {currency} in {market}. Listing ID: {listing_id}")

    @market.command(name="buy")
    async def market_buy(self, ctx, market: str, listing_id: int):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if market not in guild_data["markets"]:
            await ctx.send(f"Market {market} does not exist.")
            return
        
        listings = guild_data["markets"][market]["listings"]
        listing = next((l for l in listings if l["id"] == listing_id), None)
        if not listing:
            await ctx.send("Listing not found.")
            return
        
        buyer_id = str(ctx.author.id)
        if buyer_id not in guild_data["wallets"]:
            guild_data["wallets"][buyer_id] = {cur: 0 for cur in guild_data["currencies"]}
        if "inventories" not in guild_data:
            guild_data["inventories"] = {}
        if buyer_id not in guild_data["inventories"]:
            guild_data["inventories"][buyer_id] = {}
        
        if guild_data["wallets"][buyer_id][listing["currency"]] < listing["price"]:
            await ctx.send("Insufficient funds.")
            return
        
        guild_data["wallets"][buyer_id][listing["currency"]] -= listing["price"]
        guild_data["wallets"][listing["seller"]][listing["currency"]] += listing["price"]
        guild_data["inventories"][buyer_id][listing["item"]] = guild_data["inventories"][buyer_id].get(listing["item"], 0) + listing["amount"]
        
        listings.remove(listing)
        await ctx.send(f"Bought {listing['amount']} {listing['item']} for {listing['price']} {listing['currency']}")

    @market.command(name="browse")
    async def market_browse(self, ctx, market: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if market not in guild_data["markets"]:
            await ctx.send(f"Market {market} does not exist.")
            return
        
        listings = guild_data["markets"][market]["listings"]
        if not listings:
            await ctx.send("No active listings in this market.")
            return
        
        embed = discord.Embed(title=f"Market Listings: {market}", color=discord.Color.blue())
        for listing in listings:
            embed.add_field(
                name=f"ID: {listing['id']} - {listing['item']}",
                value=f"Amount: {listing['amount']}, Price: {listing['price']} {listing['currency']}",
                inline=False
            )
        await ctx.send(embed=embed)
