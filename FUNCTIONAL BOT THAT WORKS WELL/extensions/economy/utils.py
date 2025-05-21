from discord.ext import commands
import discord

def check_staff(ctx):
    return ctx.author.guild_permissions.administrator or discord.utils.get(ctx.author.roles, name="Economy Staff")

def format_currency(amount, symbol):
    return f"{amount:.2f} {symbol}"

def check_negative(amount):
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    return amount

async def send_paginated_embed(ctx, title, fields, color=discord.Color.blue(), fields_per_page=10):
    pages = [fields[i:i + fields_per_page] for i in range(0, len(fields), fields_per_page)]
    current_page = 0

    async def create_embed(page_num):
        embed = discord.Embed(title=f"{title} (Page {page_num + 1}/{len(pages)})", color=color)
        for name, value in pages[page_num]:
            embed.add_field(name=name, value=value, inline=False)
        return embed

    message = await ctx.send(embed=await create_embed(0))

    if len(pages) > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "➡️" and current_page < len(pages) - 1:
                    current_page += 1
                    await message.edit(embed=await create_embed(current_page))
                elif str(reaction.emoji) == "⬅️" and current_page > 0:
                    current_page -= 1
                    await message.edit(embed=await create_embed(current_page))

                await message.remove_reaction(reaction, user)

            except:
                break

        await message.clear_reactions()

async def setup(bot):
    # This setup function is empty because utils.py doesn't define a cog.
    # However, we still need it for the extension loading system to work.
    pass