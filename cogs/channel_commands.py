import discord
from discord.ext import commands
import json
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

import functions.logging.convert_logging as convert_logging
import functions.common_functions.common_functions as common_functions
from functions.logging.usage import record_usage, finish_usage
from functions.other_functions.get_data import get_version
from functions.other_functions.timestamp import curr_time

load_dotenv()
# log_level = os.getenv("LOG_LEVEL")
# version = os.getenv("VERSION")
# discord_log_level = os.getenv("DISCORD_LOG_LEVEL")

log = logging.getLogger(__name__)
log = convert_logging.get_logging()

guild_ids = [876042400005505066, 805313762663333919]

version = get_version()


class ChannelCommands(
    commands.Cog, description="Administrator Commands for Bot Functions"
):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name="SetAnnouncementChannel",
        aliases=["SetStartupChannel", "SetBootUpChannel", "SAC"],
        help="Set a channel for the bot to send messages when it starts up",
    )
    @commands.before_invoke(record_usage)
    @commands.after_invoke(finish_usage)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set_announcement_channel(self, ctx, channel: discord.TextChannel):
        log.debug(f"Opening announcement_channels json file")

        with open("./data/json_data/announcement_channels.json", "r") as file:
            log.debug(f"Reading json file")
            channels = json.load(file)
            log.debug(f"Read json file")
            file.close()

        channels["announcement_channels"].append(str(channel.id))

        log.debug(f"Writing to announcement_channels.json")
        with open("./data/json_data/announcement_channels.json", "w") as file:
            log.debug(f"Dumping Prefixes to File")
            json.dump(channels, file, indent=4)
            file.close()

        log.debug("Finished setting channel for {}".format(ctx.guild.id))
        embed = discord.Embed(
            title=f"#{channel.name} has been added to announcements file",
            color=common_functions.get_random_color(),
        )
        embed.timestamp = curr_time()
        await ctx.send(embed=embed)

    @commands.command(
        name="RemoveAnnouncementChannel",
        aliases=["RemoveStartupChannel", "RemoveBootUpChannel", "RAC"],
        help="Remove a channel for the bot to send messages when it starts up",
    )
    @commands.before_invoke(record_usage)
    @commands.after_invoke(finish_usage)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def remove_announcement_channel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ):
        log.debug(f"Reading announcement_channels.json")

        with open("./data/json_data/announcement_channels.json", "r") as file:
            log.debug(f"Reading json file")
            announcement_channels = json.load(file)
            log.debug(f"Read json file")
            file.close()

        if str(channel.id) not in announcement_channels["announcement_channels"]:
            log.error(f"{str(channel.id)} is not in the json file")
            embed = discord.Embed(
                title="That channel is not in the json file", color=0xFF0000
            )
            embed.timestamp = curr_time()
            await ctx.send(embed=embed)
            return None

        log.debug(f"Removing {channel.id}")
        announcement_channels["announcement_channels"].remove(str(channel.id))
        log.debug(f"Removed {channel.id}")

        log.debug(f"Writing to JSON File")
        with open("./data/json_data/announcement_channels.json", "w") as file:
            log.debug(f"Dumping to JSON File")
            json.dump(announcement_channels, file, indent=4)
            log.debug(f"Dumped to JSON file")
            file.close()

        embed = discord.Embed(
            title=f"#{channel.name} has been removed from announcements file",
            color=common_functions.get_random_color(),
        )
        embed.timestamp = curr_time()
        await ctx.send(embed=embed)

    @set_announcement_channel.error
    async def set_announcement_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            log.error(f"{ctx.author.name} does not have required permissions")
            embed = discord.Embed(
                title="Missing Permissions", color=discord.Color.red()
            )
            embed.timestamp = curr_time()
            await ctx.send(embed=embed)

            return
        if isinstance(error, commands.MissingRequiredArgument):
            log.error(f"{ctx.author.name} did not send valid argument")
            embed = discord.Embed(
                title="Please Send a Channel Along With the Command",
                color=discord.Colour.red(),
            )
            embed.timestamp = curr_time()
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ChannelNotFound):
            log.error(f"{ctx.author.name} sent invalid channel/user")
            embed = discord.Embed(
                title="Not a Valid Channel", color=discord.Colour.red()
            )
            embed.timestamp = curr_time()
            await ctx.send(embed=embed)

    @remove_announcement_channel.error
    async def remove_announcement_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Missing Permissions", color=discord.Color.red()
            )
            embed.timestamp = curr_time()
            await ctx.send(embed=embed)
            return
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Please Send a Channel Along With the Command",
                color=discord.Colour.red(),
            )
            embed.timestamp = curr_time()
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.ChannelNotFound):
            log.error(f"{ctx.author.name} sent invalid channel/user")
            embed = discord.Embed(
                title="Not a Valid Channel", color=discord.Colour.red()
            )
            embed.timestamp = curr_time()
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(ChannelCommands(client))
