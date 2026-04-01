import datetime
import logging

import asyncio
import discord
import httpcore
import pytz
import roblox
from discord.ext import commands
from discord.ui import Button, View
from discord.ext.commands import HybridCommandError
from sentry_sdk import capture_exception, push_scope
from aiohttp import ClientConnectorSSLError
from decouple import config
from utils.constants import BLANK_COLOR, RED_COLOR
from utils.utils import error_gen, GuildCheckFailure
from utils.prc_api import ServerLinkNotFound, ResponseFailure


class OnCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx, error):
        ctx.bot.internal_command_storage.pop(ctx, None)
        do_not_send = getattr(ctx, "dnr", False)
        bot = self.bot
        error_id = error_gen()

        if isinstance(error, commands.CommandInvokeError):
            error = error.original
            return await self.on_command_error(ctx, error)

        if isinstance(error, commands.CommandOnCooldown):
            return (
                await ctx.reply(
                    embed=discord.Embed(
                        title="Coowdown >w<",
                        description=f"Dis command is on coowdown~ Pwease twy again in {error.retry_after:.2f} seconds owo~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

        if (
            "Invalid Webhook Token" in str(error)
            or "Unknown Message" in str(error)
            or "Unknown message" in str(error)
            or isinstance(error, asyncio.TimeoutError)
        ):
            return

        if isinstance(
            error, HybridCommandError
        ) and "RemoteProtocolError: Server disconnected without sending a response." in str(
            error
        ):
            return (
                await ctx.reply(
                    embed=discord.Embed(
                        title="Connection Ewwow >w<",
                        description="Da sewvew disconnected without sending a wesponse~ Ur issue wiww be fixed if u twy again owo~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

        if isinstance(error, httpcore.ConnectTimeout):
            return (
                await ctx.reply(
                    embed=discord.Embed(
                        title="HTTP Ewwow >w<",
                        description="I couwd nyot connect to da WOBLOX API~ Pwease twy again watew uwu~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

        if isinstance(error, ResponseFailure):
            (
                await ctx.reply(
                    embed=discord.Embed(
                        title=f"PRC Wesponse Faiwuwe ({error.status_code}) >w<",
                        description=(
                            "Ur sewvew seems to be offwine~ If dis is incowwect, PRC's API may be down owo~"
                            if error.status_code == 422
                            else "Thewe seems to be issues with da PRC API~ Stand by and wait a few minutes befowe twying again uwu~"
                        ),
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

            with push_scope() as scope:
                scope.set_tag("error_id", error_id)
                scope.set_tag("guild_id", ctx.guild.id)
                scope.set_tag("user_id", ctx.author.id)
                if isinstance(ctx.bot, commands.AutoShardedBot):
                    scope.set_tag("shard_id", ctx.guild.shard_id)
                scope.set_level("error")
                await bot.errors.insert(
                    {
                        "_id": error_id,
                        "error": str(error),
                        "time": datetime.datetime.now(tz=pytz.UTC).strftime(
                            "%m/%d/%Y, %H:%M:%S"
                        ),
                        "channel": ctx.channel.id,
                        "guild": ctx.guild.id,
                    }
                )

                capture_exception(error)
            return

        if isinstance(error, commands.BadArgument):
            return (
                await ctx.reply(
                    embed=discord.Embed(
                        title="Invawid Awgument >w<",
                        description="U pwovided an invawid awgument to dis command~ nyaa~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

        if "Invalid username" in str(error):
            return (
                await ctx.reply(
                    embed=discord.Embed(
                        title="Pwayew nyot found >w<",
                        description="I couwd nyot find a WOBLOX pwayew with dat cowwesponding usewname~ uwu~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

        if isinstance(error, roblox.UserNotFound):
            return (
                await ctx.reply(
                    embed=discord.Embed(
                        title="Pwayew nyot found >w<",
                        description="I couwd nyot find a WOBLOX pwayew with dat cowwesponding usewname~ uwu~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

        if isinstance(error, discord.Forbidden):
            if "Cannot send messages to this user" in str(error):
                return

        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(
                title="Diwect Messages owo",
                description=f"I wouwd wuv to tawk to u mowe pewsonawwy, "
                f"but I can't do dat in DMs~ Pwease use me in a sewvew uwu~",
                color=BLANK_COLOR,
            )
            if not do_not_send:
                await ctx.send(embed=embed)
            return

        if isinstance(error, GuildCheckFailure):
            return (
                await ctx.send(
                    embed=discord.Embed(
                        title="Nyot Setup >w<",
                        description="Dis command wequiwes fow da bot to be configuwed befowe dis command is wan~ Pwease use `/setup` fiwst uwu~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, ServerLinkNotFound):
            aliases = {
                "mc": "Maple County",
                "erlc": "ER:LC",
            }
            if error.code == 9999 and not do_not_send:
                await ctx.send(
                    embed=discord.Embed(
                        title="API Vewsioning Change owo",
                        description="Due to a new change with PRC's Pwivate Sewvew API, in owdew to use API featuwes, da pwivate sewvew has to be __fuwwy westawted__. If thewe is nyo one in-game, a pwayew has to join da game fow da API featuwes to wowk effectivewy~\n\nIf da sewvew is cuwwentwy active, when aww usews weave da game and when one pewson joins back, da API featuwes wiww begin wowking again~\n\nSowwy fow da inconvenience,\nERM Team uwu~",
                        color=BLANK_COLOR,
                    ).set_footer(text=f"{error.code} | {error_id}")
                )
            elif error.code in [2000, 2001, 2002, 401] and not do_not_send:
                await ctx.send(
                    embed=discord.Embed(
                        title="Nyot Winked >w<",
                        description=f"Dis sewvew does nyot hav an {aliases[error.platform]} sewvew connected~ \nTo wink ur {aliases[error.platform]} sewvew, wun **/{error.platform} link** owo~",
                        color=BLANK_COLOR,
                    ).set_footer(text=error_id)
                )
            else:
                if not do_not_send:
                    await ctx.send(
                        embed=discord.Embed(
                            title="API Fataw Ewwow >w<",
                            description=f"Da {aliases[error.platform]} API encountewed a fataw ewwow which has wesuwted in us being unabwe to fetch {aliases[error.platform]} data~ uwu~",
                            color=BLANK_COLOR,
                        ).set_footer(text=f"{error.code} | {error_id}")
                    )
            with push_scope() as scope:
                scope.set_tag("error_id", error_id)
                scope.set_tag("guild_id", ctx.guild.id)
                scope.set_tag("user_id", ctx.author.id)
                if isinstance(ctx.bot, commands.AutoShardedBot):
                    scope.set_tag("shard_id", ctx.guild.shard_id)
                scope.set_level("error")
                await bot.errors.insert(
                    {
                        "_id": error_id,
                        "error": str(error),
                        "time": datetime.datetime.now(tz=pytz.UTC).strftime(
                            "%m/%d/%Y, %H:%M:%S"
                        ),
                        "channel": ctx.channel.id,
                        "guild": ctx.guild.id,
                    }
                )

                capture_exception(error)
            return

        if isinstance(error, commands.CheckFailure):
            return (
                await ctx.send(
                    embed=discord.Embed(
                        title="Nyot Pewmitted >w<",
                        description="U awe nyot pewmitted to wun dis command~ uwu~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )
        if isinstance(error, OverflowError):
            return (
                await ctx.reply(
                    embed=discord.Embed(
                        title="Ovewfwow Ewwow >w<",
                        description="A usew has inputted an awbitwawy time amount of time into ERM and we wewe unabwe to dispway da wequested data because of dis~ Pwease find da souwce of dis, and wemove da excess amount of time uwu~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )
        if isinstance(error, commands.MissingRequiredArgument):
            return (
                await ctx.send(
                    embed=discord.Embed(
                        title="Missing Awgument >w<",
                        description="U awe missing a wequiwed awgument to wun dis command~ nyaa~",
                        color=BLANK_COLOR,
                    )
                )
                if not do_not_send
                else None
            )

        if not isinstance(
            error,
            (
                commands.CommandNotFound,
                commands.CheckFailure,
                commands.MissingRequiredArgument,
                discord.Forbidden,
            ),
        ):

            with push_scope() as scope:
                scope.set_tag("error_id", error_id)
                scope.set_tag("guild_id", ctx.guild.id)
                scope.set_tag("user_id", ctx.author.id)
                if isinstance(ctx.bot, commands.AutoShardedBot):
                    scope.set_tag("shard_id", ctx.guild.shard_id)
                scope.set_level("error")
                await bot.errors.insert(
                    {
                        "_id": error_id,
                        "error": str(error),
                        "time": datetime.datetime.now(tz=pytz.UTC).strftime(
                            "%m/%d/%Y, %H:%M:%S"
                        ),
                        "channel": ctx.channel.id,
                        "guild": ctx.guild.id,
                    }
                )

                error_link = capture_exception(error)


            if not do_not_send:
                await ctx.send(
                    embed=discord.Embed(
                        title=f"{self.bot.emoji_controller.get_emoji('error')} Command Faiwuwe >w<",
                        description="Da command u wewe attempting to wun faiwed~\nContact ERM Suppowt fow assistance uwu~",
                        color=RED_COLOR,
                    ).add_field(name="Ewwow ID", value=f"[`{error_id}`]({config('SENTRY_BASE_URL') + error_link})", inline=False),
                    view=View().add_item(
                        Button(
                            label="Contact ERM Suppowt uwu",
                            style=discord.ButtonStyle.link,
                            url="https://discord.gg/FAC629TzBy",
                        )
                    ),
                )

async def setup(bot):
    await bot.add_cog(OnCommandError(bot))
