import datetime

import discord
from discord.ext import commands

class Guild(commands.Cog):
    """Specific stuff for the RedditBoat guild"""

    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(571360666179469314)
    
    def _build_member_embed(self, member):
        """Build a user embed"""
        embed = discord.Embed(title=f"Member {member} ({member.id}) joined", description=f"Welcome to the RedditBoat guild! Please read #rules and #info for information. Need help? Read the #faq or contact the support team.\nThe server is now at {ctx.guild.member_count}", colour=discord.Colour.red(), timestamp=member.joined_at).set_footer(icon_url=member.avatar_url)
        return embed
    
    def _build_guild_embed(self, guild):
        """Build a guild ember"""
        embed = discord.Embed(title=f"Guild {guild} ({guild.id}) invited the bot", description=f"Thank you for inviting the bot! We are now at {len(bot.guilds)} guilds!", colour=discord.Colour.red(), timestamp=datetime.datetime.now()).set_footer(icon_url=guild.icon_url)
        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Adding roles and logging member joins"""
        if member.guild != self.guild:
            return
        await self.guild.get_channel(572023190537371649).send(embed=self._build_member_embed(member))
        await member.add_roles(self.guild.get_role(572018920186183681))
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Loggin guild joins"""
        await self.guild.get_channel(572024423947698197).send(embed=self._build_guild_embed(guild))

def setup(bot):
    bot.add_cog(Guild(bot))