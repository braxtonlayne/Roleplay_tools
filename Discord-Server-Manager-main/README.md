# Advanced Discord Server Manager Bot

## Overview
This Discord Server Manager Bot is not your average server management tool. It's a system I designed for managing my own servers as standard management bots simply lacked the features I wanted.

## Standout Features

### 1. Cross-Channel Chronological Logging (`!log_tagged`)
Unlike typical logging bots that operate on a per-channel basis, this bot offers a different approach:
- Logs messages across multiple channels simultaneously
- Compiles logs in strict chronological order, regardless of the source channel
- Allows for a cohesive narrative across your entire server
- Start logging from specific message IDs in each channel, allowing for precise historical records

Example use:
```
!log_tagged important 123456789 987654321 543216789
```
This command would log all channels tagged as "important" across your server, starting from the specified message IDs in each channel, all compiled into a single, chronological log file.

### 2. Flexible Channel Tagging System (`!mark` and `!unmark`)
Create a custom organizational structure that transcends Discord's standard categories:
- Tag channels with any label you choose
- A single channel can have multiple tags
- Tags can span across categories, allowing for multi-dimensional organization

Example:
```
!mark project-alpha
!mark urgent
```
Now this channel is tagged with both "project-alpha" and "urgent", allowing it to be included in logs or operations for either tag.

### 3. Message Format Whitelisting (`!set_whitelist`)
Ensure your logs contain only the information you need:
- Set specific message formats that will be included in logs
- Any message not matching these formats will be excluded from logging
- Helps maintain clean, relevant logs without manual filtering

Example:
```
!set_whitelist [UPDATE], [ALERT], [DECISION]
```
Now, only messages starting with these tags will be included in your logs.

### 4. User Alias System (`!register_alias`)
Maintain consistent identity management across your server:
- Users can set aliases that replace their username in logs
- Aliases can represent roles, positions, or any other identifier
- Helps maintain immersion or organizational structure in logs

### 5. Automated Server Setup (`!setup_server`)
Rapidly deploy complex server structures:
- Set up categories, channels, and roles all at once
- Useful for creating standardized server layouts or quick deployment of new servers
- Customizable through a simple configuration file

### 6. Server Reset Functionality (`!purge_server`)
Start fresh without leaving the server:
- Removes all custom channels and roles
- Resets the server to a blank slate
- Useful for major reorganizations or cleaning up test configurations

### 7. Dynamic Extension System
Adapt the bot to your specific needs:
- Add custom commands and functionalities
- Hot-reload extensions without restarting the bot
- Easily expandable for unique server requirements

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/braxtonlayne/Discord-Server-Manager.git
   cd Discord-Server-Manager
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   DATA_FILE=bot_data.json
   ```

4. (Optional) Create a `server_config.txt` for the `!setup_server` command. Example:
   ```
   CATEGORY: Command Center
   CHANNEL: mission-control | Central hub for all operations
   CHANNEL: alerts | Time-sensitive information
   CATEGORY: Projects
   CHANNEL: project-alpha | Discussions for Project Alpha
   CHANNEL: project-beta | Discussions for Project Beta
   ROLE: Commander, FF0000, administrator
   ROLE: Operator, 00FF00, manage_messages, read_message_history
   ```

## Usage

Run the bot:
```
python main.py
```

Key Commands:
- `!setup_server`: Initialize complex server structure from config file
- `!mark <tag>`: Add a tag to the current channel for organizational purposes
- `!unmark <tag>`: Remove a tag from the current channel
- `!log_tagged <tag> [message_id1] [message_id2] ...`: Compile chronological log from all channels with the specified tag, optionally starting from specific message IDs in each channel
- `!register_alias <alias>`: Set a custom alias for logging purposes
- `!set_whitelist <format1>, <format2>, ...`: Set required message formats for logging
- `!purge_server`: Reset server to default state (admin only, use with caution)
- `!reload`: Hot-reload bot extensions (admin only)

## Extending the Bot

The bot's modular design allows for easy addition of new features:

1. Create a new Python file in the `extensions` folder.
2. Define a class inheriting from `commands.Cog`.
3. Add new commands within this class.
4. Include a `setup` function to add the Cog to the bot.

Example extension:
```python
from discord.ext import commands

class AdvancedLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def log_between(self, ctx, start_id: int, end_id: int):
        """Log all tagged messages between two message IDs."""
        # Implementation here

async def setup(bot):
    await bot.add_cog(AdvancedLogging(bot))
```

## Contributing
I welcome contributions that enhance the bot's unique capabilities. Whether it's improving the logging system, adding new organizational features, or optimizing performance, your input is valuable.

## License
This project is licensed under the GNU General Public License v3 (GPLv3). See the [LICENSE](LICENSE) file for details.

## Acknowledgements
- Claude 3.5 Sonnet for assistance in development and documentation
