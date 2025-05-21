import discord
from discord.ext import commands

class AnalyticsSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot
        

    @commands.command(name="economy_report")
    @commands.has_permissions(administrator=True)
    async def economy_report(self, ctx):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        embed = discord.Embed(title="Economy Report", color=discord.Color.gold())
        
        # Currency circulation
        for currency, data in guild_data["currencies"].items():
            embed.add_field(name=f"{currency} Circulation", value=data["in_circulation"])
        
        # Total market value
        total_market_value = sum(listing["amount"] * listing["price"] 
                                 for market in guild_data["markets"].values() 
                                 for listing in market["listings"])
        embed.add_field(name="Total Market Value", value=total_market_value)
        
        # Number of jobs
        embed.add_field(name="Number of Jobs", value=len(guild_data["jobs"]))
        
        # Number of active loans
        active_loans = sum(1 for loan in guild_data.get("loans", {}).values() if loan["status"] == "approved")
        embed.add_field(name="Active Loans", value=active_loans)
        
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx, currency: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if currency not in guild_data["currencies"]:
            await ctx.send(f"Currency {currency} does not exist.")
            return
        
        wallets = guild_data["wallets"]
        sorted_wallets = sorted(wallets.items(), key=lambda x: x[1].get(currency, 0), reverse=True)
        
        embed = discord.Embed(title=f"Wealth Leaderboard - {currency}", color=discord.Color.gold())
        for i, (user_id, wallet) in enumerate(sorted_wallets[:10], 1):
            user = ctx.guild.get_member(int(user_id))
            if user:
                embed.add_field(name=f"{i}. {user.name}", value=f"{wallet.get(currency, 0)} {currency}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="market_trends")
    async def market_trends(self, ctx):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        embed = discord.Embed(title="Market Trends", color=discord.Color.blue())
        
        for market_name, market_data in guild_data["markets"].items():
            if not market_data["listings"]:
                continue
            
            avg_prices = {}
            for listing in market_data["listings"]:
                item = listing["item"]
                price = listing["price"]
                currency = listing["currency"]
                if item not in avg_prices:
                    avg_prices[item] = {"total": 0, "count": 0, "currency": currency}
                avg_prices[item]["total"] += price
                avg_prices[item]["count"] += 1
            
            for item, data in avg_prices.items():
                avg_price = data["total"] / data["count"]
                embed.add_field(name=f"{item} in {market_name}", 
                                value=f"Avg Price: {avg_price:.2f} {data['currency']}")
        
        await ctx.send(embed=embed)
