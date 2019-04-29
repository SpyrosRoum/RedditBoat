import discord
from discord.ext import commands

class Misc(commands.Cog):
    """Misc commands"""

    def __init__(self, bot):
        self.bot = bot
        self._ignored_cogs = ["Jishaku", "Errors", "Owner", "Guild"]
        self._allowed_cogs = {"misc": "Misc", "player": "Player"}

    def get_command_arguments(self, command):
        """Get the arguments for a command"""
        to_ret = ""
        if not command.clean_params:
            return ""
        payload = command.clean_params
        for item in payload.keys():
            if "none" not in str(payload[item]).lower():
                to_ret += f"<{item}>"
            else:
                to_ret += f"[{item}]"
        return to_ret

    def prepare_arguments(self, command):
        """Get the arguments for a command but in a format for looking at specific commands"""
        to_ret = ""
        if not command.clean_params:
            return "\nNo arguments"
        payload = command.clean_params
        for item in payload.keys():
            if "none" in str(payload[item]):
                to_ret += f"\n`{item}` : Not required"
            else:
                to_ret += f"\n`{item}` : Is required"
        return to_ret

    @commands.command(name="help")
    async def help_(self, ctx, *, command=None):
        """Get help on a command, or command category"""
        if not command:
            desc = ""
            for item in self.bot.cogs:
                if item in self._ignored_cogs:
                    continue
                desc += f"\n**{item} Category**"
                cog = self.bot.cogs[item]
                for command in cog.walk_commands():
                    desc += f"\n**{command} {self.get_command_arguments(command)}**\n> {command.help}\n\> Aliases: {', '.join(command.aliases) if command.aliases else 'None'}"
                desc += "\n"
            embed = discord.Embed(
                title="Help",
                colour=discord.Colour.red(),
                description=f"**Bot Help\n---\nKey:\n[argument] : Not a required command argument\n<argument> : A required command argument\n---**\n{desc}",
                timestamp=ctx.message.created_at
            ).set_thumbnail(url=ctx.guild.me.avatar_url).set_footer(text="Use hike help <command or category> for more info.")
            return await ctx.send(embed=embed)
        else:
            desc = ""
            try:
                if command.lower() in self._allowed_cogs:
                    command = self._allowed_cogs[command]
            except KeyError:
                pass
            command = self.bot.get_cog(command) or self.bot.get_command(command)
            if isinstance(command, commands.Cog):
                cog = command
                for cog_command in cog.walk_commands():
                    to_append = self.get_command_arguments(cog_command)
                    desc += f"\n**{cog_command} {to_append}**\n> {cog_command.help}\n\> Aliases: {', '.join(cog_command.aliases) if cog_command.aliases else 'None'}"
            elif isinstance(command, commands.Command):
                desc += f"\n**Arguments**\n{self.prepare_arguments(command)}\n\n**Description**\n{command.help}\n\n**Aliases**\n{', '.join(command.aliases) if command.aliases else 'None'}"
            else:
                return await ctx.send(f"Command or category was not found")
            embed = discord.Embed(
                title="Help",
                colour=discord.Colour.red(),
                description=f"**Help for {command.__class__.__name__.lower() if isinstance(command, commands.Cog) else '%s' % command.name}\n---\nKey:\n(argument) : Not a required command argument\n[argument] : A required command argument\n---**\n{desc}"
            ).set_thumbnail(url=ctx.guild.me.avatar_url).set_footer(text=f"Help for {command.__class__.__name__ if isinstance(command, commands.Cog) else command.name}")
            return await ctx.send(embed=embed)
    
    @commands.command(name="ping")
    async def ping_(self, ctx):
        """Get the bot latency"""
        return await ctx.send(f"Messages will be posted at about `{round(self.bot.latency*1000)}`ms")
    
    @commands.command(name="invite")
    async def invite_(self, ctx):
        """Get a few links for the bot"""
        embed = discord.Embed(description=f"Invite Bot : [link](https://discordapp.com/api/oauth2/authorize?client_id=570633678447968257&permissions=48&scope=bot)\nSupport Guild : [link](https://discord.gg/WT2nAr4)", colour=discord.Colour.red(), timestamp=ctx.message.created_at).set_footer(icon_url=ctx.guild.me.avatar_url)
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))