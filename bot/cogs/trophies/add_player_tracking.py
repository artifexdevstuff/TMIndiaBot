import json
from typing import Dict

import discord
from discord import ApplicationContext
from discord.commands import Option, permissions
from discord.ext import commands
from trackmania import Player

from bot import constants
from bot.bot import Bot
from bot.log import get_logger, log_command

log = get_logger(__name__)


class AddPlayerTracking(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command(
        guild_ids=constants.Bot.default_guilds,
        name="addplayertracking",
        description="Adds a player to the trophy tracking list",
    )
    @discord.has_any_role(
        805318382441988096, 858620171334057994, guild_id=constants.Guild.tmi_server
    )
    @discord.has_any_role(
        940194181731725373, 941215148222341181, guild_id=constants.Guild.testing_server
    )
    async def _add_player_tracking(
        self,
        ctx: ApplicationContext,
        username: Option(str, "The username of the player to add.", required=True),
    ):
        log_command(ctx, "add_player_tracking")

        await ctx.defer()

        log.debug(f"Searching for Player with the username -> {username}")
        search_result = await Player.search(username)

        if search_result is None:
            await ctx.respond("This player does not exist.")
            return

        player_id = search_result[0].player_id

        log.debug("Getting Trophy Count of Player")
        player_data = await Player.get_player(player_id)

        trophy_count = player_data.trophies.score()

        log.debug(f"Trophy Count of {username} is {trophy_count}")

        log.debug("Opening File")
        with open("./bot/resources/json/trophy_tracking.json", "r") as file:
            tracking_data = json.load(file)

        log.debug("Adding Player to List")
        tracking_data["tracking"].extend(
            [
                {
                    "username": player_data.name,
                    "player_id": player_data.player_id,
                    "score": trophy_count,
                },
            ],
        )

        log.debug("Sorting tracking data based on trophy count")
        # sort tracking data based on trophy_count
        tracking_data["tracking"] = sorted(
            tracking_data["tracking"], key=lambda k: k["score"], reverse=True
        )

        log.debug("Dumping to File")
        with open("bot/resources/json/trophy_tracking.json", "w") as file:
            json.dump(tracking_data, file, indent=4)

        await ctx.respond(f"{username} has been added to the trophy tracking list.")


def setup(bot: Bot):
    bot.add_cog(AddPlayerTracking(bot))