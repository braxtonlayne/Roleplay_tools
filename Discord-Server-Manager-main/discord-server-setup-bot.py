import discord
from discord.ext import commands
import os
import json
from datetime import datetime
import importlib.util
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# File to store all persistent data
DATA_FILE = os.getenv('DATA_FILE', 'bot_data.json')

# Load data from file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save data to file
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(bot_data, f)

# Load initial data
bot_data = load_data()

def get_guild_data(guild_id):
    if str(guild_id) not in bot_data:
        bot_data[str(guild_id)] = {
            "registered_aliases": {},
            "channel_tags": {},
            "message_whitelist": []
        }
    return bot_data[str(guild_id)]

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await load_extensions()

async def load_extensions():
    extensions_dir = os.path.join(os.path.dirname(__file__), 'extensions')
    if not os.path.exists(extensions_dir):
        os.makedirs(extensions_dir)
        print(f"Created extensions directory: {extensions_dir}")
    
    if not os.listdir(extensions_dir):
        print("No extensions found. The bot will run with base functionality.")
        return

    for filename in os.listdir(extensions_dir):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f"extensions.{filename[:-3]}")
                print(f'Loaded extension: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {filename[:-3]}')
                print(f'Error: {str(e)}')

@bot.command(name='reload', help='Reloads all extensions')
@commands.has_permissions(administrator=True)
async def reload_extensions(ctx):
    extensions_dir = os.path.join(os.path.dirname(__file__), 'extensions')
    if not os.path.exists(extensions_dir) or not os.listdir(extensions_dir):
        await ctx.send("No extensions found to reload.")
        return

    for filename in os.listdir(extensions_dir):
        if filename.endswith('.py'):
            try:
                await bot.reload_extension(f"extensions.{filename[:-3]}")
                await ctx.send(f'Reloaded extension: {filename[:-3]}')
            except commands.ExtensionNotLoaded:
                await ctx.send(f"Extension '{filename[:-3]}' is not loaded. Attempting to load it.")
                try:
                    await bot.load_extension(f"extensions.{filename[:-3]}")
                    await ctx.send(f'Loaded extension: {filename[:-3]}')
                except Exception as e:
                    await ctx.send(f'Failed to load extension {filename[:-3]}')
                    await ctx.send(f'Error: {str(e)}')
            except Exception as e:
                await ctx.send(f'Failed to reload extension {filename[:-3]}')
                await ctx.send(f'Error: {str(e)}')

@bot.command(name='setup_server', help='Sets up the server based on the provided configuration file')
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    if not os.path.exists('server_config.txt'):
        await ctx.send("Could not find server_config.txt file.")
        return

    with open('server_config.txt', 'r') as file:
        current_category = None
        for line in file:
            line = line.strip()
            if line.startswith('CATEGORY:'):
                category_name = line[9:].strip()
                current_category = await ctx.guild.create_category(category_name)
            elif line.startswith('CHANNEL:'):
                if current_category is None:
                    await ctx.send("Error: Channel specified without a category.")
                    return
                channel_info = line[8:].strip().split('|')
                channel_name = channel_info[0].strip()
                channel_topic = channel_info[1].strip() if len(channel_info) > 1 else ""
                await ctx.guild.create_text_channel(channel_name, category=current_category, topic=channel_topic)
            elif line.startswith('ROLE:'):
                role_info = line[5:].strip().split(',')
                role_name = role_info[0].strip()
                color = discord.Colour(int(role_info[1].strip(), 16)) if len(role_info) > 1 else discord.Colour.default()
                permissions = discord.Permissions()
                for perm in role_info[2:]:
                    perm = perm.strip()
                    if hasattr(permissions, perm):
                        setattr(permissions, perm, True)
                await ctx.guild.create_role(name=role_name, color=color, permissions=permissions)

    await ctx.send("Server setup complete!")

@bot.command(name='purge_server', help='Purges all categories, channels, and roles from the server')
@commands.has_permissions(administrator=True)
async def purge_server(ctx):
    guild = ctx.guild

    for category in guild.categories:
        await category.delete()
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            await channel.delete()

    for role in guild.roles:
        if role.name != "@everyone" and role < guild.me.top_role:
            await role.delete()

    # Clear the data for this guild
    if str(guild.id) in bot_data:
        del bot_data[str(guild.id)]
        save_data()

    try:
        await ctx.author.send("Server purge complete!")
    except discord.errors.Forbidden:
        remaining_channel = next((c for c in guild.text_channels), None)
        if remaining_channel:
            await remaining_channel.send("Server purge complete!")
        else:
            print("Server purge complete, but couldn't notify the user.")

@bot.command(name='mark', help='Marks a channel with a tag')
@commands.has_permissions(manage_channels=True)
async def mark_channel(ctx, tag: str):
    guild_data = get_guild_data(ctx.guild.id)
    channel_id = str(ctx.channel.id)
    if channel_id not in guild_data["channel_tags"]:
        guild_data["channel_tags"][channel_id] = []
    if tag not in guild_data["channel_tags"][channel_id]:
        guild_data["channel_tags"][channel_id].append(tag)
        save_data()
        await ctx.send(f'Channel marked with tag: {tag}')
    else:
        await ctx.send(f'Channel already marked with tag: {tag}')

@bot.command(name='unmark', help='Removes a tag from a channel')
@commands.has_permissions(manage_channels=True)
async def unmark_channel(ctx, tag: str):
    guild_data = get_guild_data(ctx.guild.id)
    channel_id = str(ctx.channel.id)
    if channel_id in guild_data["channel_tags"] and tag in guild_data["channel_tags"][channel_id]:
        guild_data["channel_tags"][channel_id].remove(tag)
        save_data()
        await ctx.send(f'Tag {tag} removed from channel')
    else:
        await ctx.send(f'Tag {tag} not found for this channel')

@bot.command(name='log_tagged', help='Logs messages from channels with a specific tag, starting from the specified message IDs')
async def log_tagged_messages(ctx, tag: str, *message_ids: str):
    guild_data = get_guild_data(ctx.guild.id)
    tagged_channels = [channel_id for channel_id, tags in guild_data["channel_tags"].items() if tag in tags]
    
    if not tagged_channels:
        await ctx.send(f'No channels found with tag: {tag}')
        return

    messages = []
    for i, channel_id in enumerate(tagged_channels):
        channel = ctx.guild.get_channel(int(channel_id))
        if not channel:
            continue

        start_message_id = None
        if i < len(message_ids):
            try:
                start_message_id = int(message_ids[i])
            except ValueError:
                await ctx.send(f'Invalid message ID provided for channel {channel.name}. Skipping start point for this channel.')

        async for msg in channel.history(limit=None, oldest_first=True, after=discord.Object(id=start_message_id - 1) if start_message_id else None):
            if msg.author != bot.user and is_valid_message_format(ctx.guild.id, msg.content):
                messages.append((msg.created_at, channel.name, get_registered_alias(ctx.guild.id, msg.author), msg.content))

    messages.sort(key=lambda x: x[0])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f'{tag}_log_{timestamp}.txt'
    with open(file_name, 'w', encoding='utf-8') as log_file:
        for _, channel_name, author_name, content in messages:
            log_file.write(f'[{channel_name}] {author_name}: {content}\n')

    await ctx.send(f'Logged {len(messages)} messages with tag {tag} to {file_name}')

@bot.command(name='set_whitelist', help='Sets the message format whitelist')
@commands.has_permissions(administrator=True)
async def set_whitelist(ctx, *, formats):
    guild_data = get_guild_data(ctx.guild.id)
    # Split the formats by commas and strip whitespace
    new_whitelist = [format.strip() for format in formats.split(',')]
    guild_data["message_whitelist"] = new_whitelist
    save_data()
    await ctx.send(f'Message format whitelist updated: {", ".join(new_whitelist)}')

def is_valid_message_format(guild_id, content):
    guild_data = get_guild_data(guild_id)
    if not guild_data["message_whitelist"]:
        return True
    return any(format in content for format in guild_data["message_whitelist"])

@bot.command(name='register_alias', help='Registers an alias for the user')
async def register_alias(ctx, alias: str):
    guild_data = get_guild_data(ctx.guild.id)
    guild_data["registered_aliases"][str(ctx.author.id)] = alias
    save_data()
    await ctx.send(f'Your alias has been registered as "{alias}".')

def get_registered_alias(guild_id, author):
    guild_data = get_guild_data(guild_id)
    return guild_data["registered_aliases"].get(str(author.id), author.name)

# Run the bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
