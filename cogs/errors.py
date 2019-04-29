import humanize

import discord
from discord.ext import commands

class Errors(commands.Cog):
    """Error cog"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Command error handler"""
        ignored_errors = (commands.CommandNotFound)

        if isinstance(error, ignored_errors):
            return
        if isinstance(error, commands.CommandOnCooldown):
            hou, rem = divmod(error.retry_after, 3600)
            min, sec = divmod(rem, 60)
            day, hou = divmod(hou, 24)
            s = ""
            if day:
                s += f"{day:.0f} days"
            if hou:
                s += f"{hou:.0f} hours"
            if min:
                s += f"{min:.0f} minutes"
            if sec:
                s += f"{sec:.0f} seconds"
            return await ctx.send(f"This command is on cooldown, retry in {s}")
        return await ctx.send(f"Oops! Something went wrong. {error}")

def setup(bot):
    bot.add_cog(Errors(bot))