import asyncpg
import discord
from discord.ext import commands

import config

class RedditBoat(commands.Bot):
    """Bot"""

    def __init__(self):
        super().__init__(command_prefix="rb ")
        self._prepare(["jishaku", "cogs.user", "cogs.reddit", "cogs.misc", "cogs.guild", "cogs.errors"])
        self.custom_emojis = {"upvote": ":upvote:571360726413738004", "downvote": ":downvote:571360727038951454"}

    def _prepare(self, payload: list):
        """Prepare extensions and stuff"""
        self.remove_command("help")
        for cog in payload:
            try:
                self.load_extension(cog)
                print(cog)
            except Exception as error:
                print(error)
    
    async def on_ready(self):
        """Tell us the bot is ready"""
        await self.change_presence(activity=discord.Game(name="RedditBoat | rb help"))
        print("Connected")

if __name__ == "__main__":
    RedditBoat().run(config.TOKEN, reconnect=True)
    