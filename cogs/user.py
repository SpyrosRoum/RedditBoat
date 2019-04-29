import humanize
from datetime import datetime

import discord
from discord.ext import commands

class User(commands.Cog):
    """User commands"""

    def __init__(self, bot):
        self.bot = bot
    
    async def _build_info(self, ctx, member):
        """Used in userinfo_ to give the info of a given user"""
        last_channel_message_timestamp = [message.created_at async for message in ctx.channel.history()][0]
        return f"```cpp\n{member} ({member.id})\n\
Created At : {str(member.created_at).split('.')[0]} ({humanize.naturaltime(datetime.utcnow() - member.created_at)})\n\
Joined At : {str(member.joined_at).split('.')[0]} ({humanize.naturaltime(datetime.utcnow() - member.joined_at)})\n\
Roles : {', '.join([role.name for role in member.roles])}\n\
Last active in channel : {humanize.naturaltime(datetime.utcnow() - last_channel_message_timestamp)}\n\
Messages sent in guild while I've been online: {len([message for message in self.bot._connection._messages if message.author.id == ctx.author.id and message.guild.id == ctx.guild.id])}```"

    @commands.command(name="userinfo")
    async def userinfo_(self, ctx, member: discord.Member = None):
        """Get the information of a user, or yourself"""
        member = member if member is not None else ctx.author
        info = await self._build_info(ctx, member)
        return await ctx.send(info)

def setup(bot):
    bot.add_cog(User(bot))