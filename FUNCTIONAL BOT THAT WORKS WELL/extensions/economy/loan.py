import discord
from discord.ext import commands
from datetime import datetime, timedelta

class LoanSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="loan", invoke_without_command=True)
    async def loan(self, ctx):
        """Loan management commands"""
        await ctx.send("Available commands: request, approve, repay, info")

    @loan.command(name="request")
    async def loan_request(self, ctx, amount: float, currency: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if currency not in guild_data["currencies"]:
            await ctx.send(f"Currency {currency} does not exist.")
            return
        user_id = str(ctx.author.id)
        if "loans" not in guild_data:
            guild_data["loans"] = {}
        if user_id in guild_data["loans"]:
            await ctx.send("You already have an outstanding loan.")
            return
        guild_data["loans"][user_id] = {
            "amount": amount,
            "currency": currency,
            "status": "pending"
        }
        await ctx.send(f"Loan request for {amount} {currency} submitted for approval.")

    @loan.command(name="approve")
    @commands.has_permissions(administrator=True)
    async def loan_approve(self, ctx, user: discord.Member, interest: float, term: int):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if "loans" not in guild_data:
            await ctx.send("No pending loan requests.")
            return
        user_id = str(user.id)
        if user_id not in guild_data["loans"]:
            await ctx.send("This user doesn't have a pending loan request.")
            return
        if guild_data["loans"][user_id]["status"] != "pending":
            await ctx.send("This loan is not pending approval.")
            return
        guild_data["loans"][user_id]["status"] = "approved"
        guild_data["loans"][user_id]["interest"] = interest
        guild_data["loans"][user_id]["term"] = term
        guild_data["loans"][user_id]["due_date"] = (datetime.now() + timedelta(days=term)).isoformat()
        
        currency = guild_data["loans"][user_id]["currency"]
        amount = guild_data["loans"][user_id]["amount"]
        
        if user_id not in guild_data["wallets"]:
            guild_data["wallets"][user_id] = {cur: 0 for cur in guild_data["currencies"]}
        guild_data["wallets"][user_id][currency] += amount
        
        await ctx.send(f"Loan approved for {user.name}. {amount} {currency} has been added to their wallet.")

    @loan.command(name="repay")
    async def loan_repay(self, ctx, amount: float):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if "loans" not in guild_data:
            await ctx.send("You don't have any loans.")
            return
        user_id = str(ctx.author.id)
        if user_id not in guild_data["loans"]:
            await ctx.send("You don't have an outstanding loan.")
            return
        loan = guild_data["loans"][user_id]
        if loan["status"] != "approved":
            await ctx.send("Your loan is not in a state to be repaid.")
            return
        
        currency = loan["currency"]
        if guild_data["wallets"][user_id][currency] < amount:
            await ctx.send("Insufficient funds to make this repayment.")
            return
        
        guild_data["wallets"][user_id][currency] -= amount
        loan["amount"] -= amount
        
        if loan["amount"] <= 0:
            del guild_data["loans"][user_id]
            await ctx.send("Loan fully repaid!")
        else:
            await ctx.send(f"Repayment of {amount} {currency} made. Remaining balance: {loan['amount']} {currency}")

    @loan.command(name="info")
    async def loan_info(self, ctx):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if "loans" not in guild_data:
            await ctx.send("You don't have any loans.")
            return
        user_id = str(ctx.author.id)
        if user_id not in guild_data["loans"]:
            await ctx.send("You don't have an outstanding loan.")
            return
        loan = guild_data["loans"][user_id]
        embed = discord.Embed(title="Loan Information", color=discord.Color.blue())
        embed.add_field(name="Amount", value=f"{loan['amount']} {loan['currency']}")
        embed.add_field(name="Status", value=loan["status"])
        if loan["status"] == "approved":
            embed.add_field(name="Interest Rate", value=f"{loan['interest']}%")
            embed.add_field(name="Term", value=f"{loan['term']} days")
            embed.add_field(name="Due Date", value=loan["due_date"])
        await ctx.send(embed=embed)

    async def process_loans(self):
        for guild in self.bot.guilds:
            guild_data = self.economy.get_guild_data(guild.id)
            if "loans" not in guild_data:
                continue
            for user_id, loan_data in guild_data["loans"].items():
                if loan_data["status"] == "approved":
                    due_date = datetime.fromisoformat(loan_data["due_date"])
                    if datetime.now() > due_date:
                        # Apply penalty or take other actions for overdue loans
                        penalty = loan_data["amount"] * 0.1  # 10% penalty for example
                        loan_data["amount"] += penalty
                        # You might want to notify the user or take other actions here
