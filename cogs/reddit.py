import asyncio
import traceback
import discord
from discord.ext import commands

class Reddit(commands.Cog):
    """Upvote and Downvote images posted to the server"""

    def __init__(self, bot):
        self.bot = bot
    
    async def _get_post_channel(self, guild_id):
        """Get the channel object for a guilds post channel"""
        guild = self.bot.get_guild(guild_id)
        channel = discord.utils.get(guild.channels, name="redditboat")
        return False if not channel else channel
    
    async def _get_channel(self, payload):
        """Get the channel of a reaction add"""
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        return message

    @commands.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def setup_(self, ctx, channel: discord.TextChannel = None):
        """Setup the reddit like features of the bot"""
        post_channel_lookup = await self._get_post_channel(ctx.guild.id)
        if post_channel_lookup is False:
            try:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(send_messages=True)
                }
                channel = await ctx.guild.create_text_channel("redditboat", overwrites=overwrites)
            except Exception as error:
                raise error
            return await ctx.send(f"Post channel created! All posts will be sent to {channel.mention}")
        return await ctx.send(f"You already have a channel setup for posts, {post_channel_lookup.mention}")    
    
    @commands.command(name="post")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def post_(self, ctx, title=None, *, url = None):
        """Post an image or text to the guild reddit channel"""
        post_channel = await self._get_post_channel(ctx.guild.id)
        if post_channel is False:
            return await ctx.send(f"Looks like I dont have a post channel in this server, please see `{ctx.prefix}help setup` for info on how to set me up.")
        if title is None:
            await ctx.send("Reply to this message with the title of your post")
            try:
                response = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.guild == ctx.guild, timeout=120)
                if len(response.content) > 500:
                    return await ctx.send("Can't have a title over 500 characters")
                title = response.content
                await ctx.send("Okay, the post title has been set!")
            except asyncio.TimeoutError:
                return await ctx.send("Took too long")
        if url is None:
            if ctx.message.attachments:
                url = ctx.message.attachments
            else:
                await ctx.send("Reply to this message with the content of your post. This can be text or a url")
                try:
                    response = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.guild == ctx.guild, timeout=120)
                    url = response.content
                except asyncio.TimeoutError:
                    return await ctx.send("Took too long")
                await ctx.send("Okay, the post content has been set!")
        if isinstance(url, list):
            embed = discord.Embed(title=f"Post from {ctx.author} ({ctx.author.id})", description=f"**{title}**", colour=discord.Colour.red(), timestamp=ctx.message.created_at).set_image(url=url[0].url)
            embed.set_footer(text="Votes : 1", icon_url=ctx.author.avatar_url)
            msg = await post_channel.send(embed=embed)
            new_embed_title = f"{embed.title}, with post id {msg.id}"
            embed.title = new_embed_title
            await msg.edit(embed=embed)
            await msg.add_reaction(self.bot.custom_emojis["upvote"])
            await msg.add_reaction(self.bot.custom_emojis["downvote"])
        elif isinstance(url, str):
            if url.startswith(("http","https://")):
                embed = discord.Embed(title=f"Post from {ctx.author} ({ctx.author.id})", description=f"**{title}**", colour=discord.Colour.red(), timestamp=ctx.message.created_at).set_image(url=url)
            else:
                embed = discord.Embed(title=f"Post from {ctx.author} ({ctx.author.id})", description=f"**{title}**\n-----\n{url}", colour=discord.Colour.red(), timestamp=ctx.message.created_at)
            embed.set_footer(text="Votes : 1", icon_url=ctx.author.avatar_url)
            msg = await post_channel.send(embed=embed)
            new_embed_title = f"{embed.title}, with post id {msg.id}"
            embed.title = new_embed_title
            await msg.edit(embed=embed)
            await msg.add_reaction(self.bot.custom_emojis["upvote"])
            await msg.add_reaction(self.bot.custom_emojis["downvote"])
        return await ctx.send(f"You can now see your post in {post_channel.mention}")
    
    @commands.command(name="delete")
    async def delete_(self, ctx, post_id: int):
        """Delete a post, to get the post id, copy the message id, or see the embed's footer"""
        guild_post_channel = await self._get_post_channel(ctx.guild.id)
        if guild_post_channel is False:
            return await ctx.send(f"You can't do that! There is no post channel for this guild, please consult an admin to do `{ctx.prefix}setup`")
        message = await guild_post_channel.fetch_message(post_id)
        if not message:
            return await ctx.send(f"The post with id `{post_id}` does not exist.")
        if message.embeds:
            post_author = self.bot.get_user(int(message.embeds[0].title.split("(")[1].replace(")","").split(",")[0]))
            if ctx.author != post_author:
                return await ctx.send("The post you are trying to delete does not belong to you.")
            try:
                await message.delete()
                return await ctx.send("Post deleted")
            except exception as error:
                raise error
    
    @commands.command(name="edit")
    async def edit_(self, ctx, post_id: int, content=None):
        """Edit a post"""
        guild_post_channel = await self._get_post_channel(ctx.guild.id)
        if guild_post_channel is False:
            return await ctx.send(f"You can't do that! There is no post channel for this guild, please consult an admin to do `{ctx.prefix}setup`")
        message = await guild_post_channel.fetch_message(post_id)
        if not message:
            return await ctx.send(f"The post with id `{post_id}` does not exist.")
        if message.embeds:
            title = message.embeds[0].description.split("**")[1]
            post_author = self.bot.get_user(int(message.embeds[0].title.split("(")[1].replace(")","").split(",")[0]))
            if ctx.author != post_author:
                return await ctx.send("The post you are trying to delete does not belong to you.")
            if content is None:
                url = ctx.message.attachments
                embed = discord.Embed(title=f"Post from {ctx.author} ({ctx.author.id})", description=f"**{title}**", colour=discord.Colour.red(), timestamp=ctx.message.created_at).set_image(url=url[0].url)
            else:
                if content.startswith(("http","https://")):
                    embed = discord.Embed(title=f"Post from {ctx.author} ({ctx.author.id})", description=f"**{title}**", colour=discord.Colour.red(), timestamp=ctx.message.created_at).set_image(url=content)
                else:
                    embed = discord.Embed(title=f"Post from {ctx.author} ({ctx.author.id})", description=f"**{title}**\n-----\n{content}", colour=discord.Colour.red(), timestamp=ctx.message.created_at)
            try:
                embed.set_footer(text=message.embeds[0].footer.text, icon_url=message.embeds[0].footer.icon_url)
                await message.edit(embed=embed)
                return await ctx.send(f"Edited post `{post_id}`!")
            except Exception as error:
                await ctx.send("Something went wrong")
                raise error
                

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handles the upvote or downvote mechanic"""
        guild_post_channel = await self._get_post_channel(payload.guild_id)
        message = await self._get_channel(payload)
        user = self.bot.get_user(payload.user_id)
        if user == self.bot.user:
            return
        if guild_post_channel is False:
            return
        if message.embeds:
            try:
                if payload.user_id == int(message.embeds[0].title.split("(")[1].replace(")","")):
                    return
                post_votes = int(message.embeds[0].footer.text.split(": ")[1])
                reaction = str(payload.emoji).split(":")[2].replace(">","")
                post_author = self.bot.get_user(int(message.embeds[0].title.split("(")[1].replace(")","").split(",")[0]))
                if reaction == "571360726413738004":
                    post_votes += 1
                elif reaction == "571360727038951454":
                    post_votes -= 1
                else:
                    return
                new_embed = message.embeds[0].set_footer(text=f"Votes : {post_votes}", icon_url=post_author.avatar_url)
                await message.edit(embed=new_embed)
            except Exception as error:
                traceback.print_exc()
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Handles the upvote or downvote mechanic"""
        guild_post_channel = await self._get_post_channel(payload.guild_id)
        message = await self._get_channel(payload)
        if guild_post_channel is False:
            return
        if message.embeds:
            try:
                if payload.user_id == int(message.embeds[0].title.split("(")[1].replace(")","")):
                    return
                post_votes = int(message.embeds[0].footer.text.split(": ")[1])
                reaction = str(payload.emoji).split(":")[2].replace(">","")
                post_author = self.bot.get_user(int(message.embeds[0].title.split("(")[1].replace(")","").split(",")[0]))
                if reaction == "571360726413738004":
                    post_votes -= 1
                elif reaction == "571360727038951454":
                    post_votes += 1
                else:
                    return
                new_embed = message.embeds[0].set_footer(text=f"Votes : {post_votes}", icon_url=post_author.avatar_url)
                await message.edit(embed=new_embed)
            except Exception as error:
                traceback.print_exc()

def setup(bot):
    bot.add_cog(Reddit(bot))