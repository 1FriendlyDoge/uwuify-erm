import datetime

import discord
import pytz
from bson import ObjectId
from discord import app_commands
from discord.ext import commands

from erm import is_staff, admin_predicate, management_predicate, staff_predicate
from menus import CustomModalView, UserSelect
from utils.constants import BLANK_COLOR, GREEN_COLOR
from utils.timestamp import td_format
from utils.utils import invis_embed, require_settings, time_converter


class GameLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_missing(self, settings, section):
        if not settings:
            return False

        if not settings.get("game_logging"):
            return False

        if not settings.get("game_logging").get(section):
            return False

        if not settings.get("game_logging").get(section).get("enabled"):
            return False
        if not settings.get("game_logging").get(section).get("channel"):
            return False

        return True

    @commands.guild_only()
    @commands.hybrid_group(
        name="staff",
        description="Wequest mowe staff to be in-game! owo",
        extras={"category": "Game Logging owo~"},
    )
    async def staff(self, ctx: commands.Context):
        pass

    @staff.command(
        name="request",
        description="Send a Staff Wequest to get mowe staff in-game! uwu",
        extras={"category": "Game Logging owo~"},
    )
    @app_commands.describe(reason="Weason fow uw Staff Wequest! owo")
    @require_settings()
    async def staff_request(self, ctx: commands.Context, *, reason: str):
        settings = await self.bot.settings.find_by_id(ctx.guild.id)
        game_logging = settings.get("game_logging", {})
        if game_logging == {}:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Configuwed >w<",
                    description="Game Wogging is nyot configuwed widin dis sewvew~ >w<",
                    color=BLANK_COLOR,
                )
            )

        staff_requests = game_logging.get("staff_requests", {})
        if staff_requests == {}:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Configuwed >w<",
                    description="Staff Wequests is nyot configuwed widin dis sewvew~ nyaa uwu~",
                    color=BLANK_COLOR,
                )
            )
        enabled = staff_requests.get("enabled", False)
        if not enabled:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Enabwed uwu~",
                    description="Staff Wequests awe nyot enabwed widin dis sewvew~ >w<",
                    color=BLANK_COLOR,
                )
            )

        permission_level = staff_requests.get("permission_level", 4)
        has_permission = True
        if permission_level == 3:
            if not await admin_predicate(ctx):
                has_permission = False
            else:
                has_permission = True
        if permission_level == 2:
            if not await management_predicate(ctx):
                has_permission = False
            else:
                has_permission = True
        if permission_level == 1:
            if not await staff_predicate(ctx):
                has_permission = False
            else:
                has_permission = True
        if not has_permission:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Pewmitted uwu~",
                    description=f"U awe missing da **{ {1: 'Staff uwu~', 2: 'Management uwu~', 3: 'Admin uwu~'}.get(permission_level) }** pewmission to make a Staff Wequest~ >w<",
                    color=BLANK_COLOR,
                )
            )

        last_submitted_staff_request = [
            i
            async for i in self.bot.staff_requests.db.find(
                {"user_id": ctx.author.id, "guild_id": ctx.guild.id}
            )
            .sort({"_id": -1})
            .limit(1)
        ]
        if len(last_submitted_staff_request) != 0:
            last_submitted_staff_request = last_submitted_staff_request[0]
            document_id: ObjectId = last_submitted_staff_request["_id"]
            timestamp = document_id.generation_time.timestamp()
            if (
                timestamp + staff_requests.get("cooldown", 0)
                > datetime.datetime.now(tz=pytz.UTC).timestamp()
            ):
                return await ctx.send(
                    embed=discord.Embed(
                        title="Coowdown owo~",
                        description="U awe on coowdown fwom making Staff Wequests~ nyaa >w<",
                        color=BLANK_COLOR,
                    )
                )

        staff_clocked_in = await self.bot.shift_management.shifts.db.count_documents(
            {"EndEpoch": 0, "Guild": ctx.guild.id}
        )
        if (
            staff_requests.get("min_staff") is not None
            and staff_requests.get("min_staff") > 0
        ):
            if staff_clocked_in <= staff_requests.get("min_staff", 0):
                return await ctx.send(
                    embed=discord.Embed(
                        title="Minimum Staff owo~",
                        description=f"**{staff_requests.get('min_staff')}** membews of staff awe wequiwed to be in-game fow a Staff Wequest! owo",
                        color=BLANK_COLOR,
                    )
                )

        if (
            staff_requests.get("max_staff") is not None
            and staff_requests.get("max_staff") > 0
        ):
            if staff_clocked_in > staff_requests.get("max_staff", 0):
                return await ctx.send(
                    embed=discord.Embed(
                        title="Maximum Staff~",
                        description="Dewe awe mowe than da maximum numbew of staff onwine fow a Staff Wequest! >w<",
                        color=BLANK_COLOR,
                    )
                )

        document = {
            "user_id": ctx.author.id,
            "guild_id": ctx.guild.id,
            "username": ctx.author.name,
            "avatar": ctx.author.display_avatar.url.split("/")[-1].split(".")[0],
            "reason": reason,
            "active": True,
            "created_at": datetime.datetime.now(tz=pytz.UTC),
            "acked": [],
        }
        result = await self.bot.staff_requests.db.insert_one(document)
        o_id = result.inserted_id
        self.bot.dispatch("staff_request_send", o_id)
        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Sent Staff Wequest~",
                description="Uw Staff Wequest has been sent s-successfuwwy~ hehe uwu~",
                color=GREEN_COLOR,
            )
        )

    @commands.guild_only()
    @commands.hybrid_group(
        name="game",
        description="Manage uw game wid wogging such as messages, and events~ uwu",
        extras={"category": "Game Logging owo~"},
    )
    async def game(self, ctx):
        pass

    @commands.guild_only()
    @game.command(
        name="message",
        description="Wog aww announcements and messages in uw game~ owo",
        extras={"category": "Game Logging owo~"},
    )
    @app_commands.describe(announcement="Da game message u awe going to wog~ uwu")
    @is_staff()
    @require_settings()
    async def game_message(self, ctx: commands.Context, *, announcement: str):
        bot = self.bot
        configItem = await bot.settings.find_by_id(ctx.guild.id)

        check_settings = self.check_missing(configItem, "message")
        if check_settings is False:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Configuwed >w<",
                    description="Game Announcement Logging is nyot configuwed. >w<",
                    color=BLANK_COLOR,
                )
            )

        channel = ctx.guild.get_channel(
            configItem["game_logging"]["message"]["channel"]
        )
        if not channel:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Invawid Channel owo~",
                    description="Da Game Announcement logging channel is invawid. uwu~",
                    color=BLANK_COLOR,
                )
            )

        embed = discord.Embed(
            title="Message Logged owo~",
            color=BLANK_COLOR,
        )

        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

        embed.add_field(
            name="Announcement Infowmation owo~",
            value=(
                f"> **Staff:** {ctx.author.mention}\n"
                f"> **Announcement:** {announcement}\n"
                f"> **At:** <t:{int(datetime.datetime.now(tz=pytz.UTC).timestamp())}>"
            ),
            inline=False,
        )
        if channel is None:
            return
        await channel.send(embed=embed)
        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Logged Announcement",
                description="Ur Game Announcement has been successfuwwy logged!~",
                color=GREEN_COLOR,
            )
        )

    @commands.guild_only()
    @game.command(
        name="sts",
        description="Log a Shouldew-to-Shouldew in ur game~",
        extras={"category": "Game Logging owo~"},
    )
    async def game_sts(self, ctx: commands.Context, duration: str, *, reason: str):
        bot = self.bot
        configItem = await bot.settings.find_by_id(ctx.guild.id)

        settings_value = self.check_missing(configItem, "sts")
        if not settings_value:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Configuwed >w<",
                    description="Game STS Logging is nyot configuwed. >w<",
                    color=BLANK_COLOR,
                )
            )

        channel = ctx.guild.get_channel(configItem["game_logging"]["sts"]["channel"])
        if not channel:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Invawid Channel owo~",
                    description="Da Game STS logging channel is invawid. uwu~",
                    color=BLANK_COLOR,
                )
            )
        view = UserSelect(ctx.author.id)

        sts_msg = await ctx.reply(
            embed=discord.Embed(
                title="Pawticipants owo~",
                description="What staff membews took pawt in dis STS? >w<",
                color=BLANK_COLOR,
            ),
            view=view,
        )
        timeout = await view.wait()
        if timeout:
            return

        if view.value:
            members = view.value
        else:
            return

        embed = discord.Embed(
            title="STS Logged >w<",
            color=BLANK_COLOR,
        )

        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

        embed.add_field(
            name="Staff Membews owo~",
            value="\n".join(
                [
                    (f"**{index+1}.** " + member.mention)
                    for index, member in enumerate(members)
                ]
            ),
            inline=False,
        )

        try:
            duration = time_converter(duration)
        except ValueError:
            return await ctx.send(
                embed=discord.Embed(
                    title="Invawid Time~",
                    description="Dis is an invawid duwation fowmat.~",
                    color=BLANK_COLOR,
                )
            )

        embed.add_field(
            name="STS Infowmation owo~",
            value=(
                f"> **Host:** {ctx.author.mention}\n"
                f"> **Duration:** {td_format(datetime.timedelta(seconds=duration))}\n"
                f"> **Hosted At:** <t:{int(ctx.message.created_at.timestamp())}>\n"
                f"> **Reason:** {reason}"
            ),
            inline=False,
        )

        if channel is None:
            return
        await channel.send(embed=embed)

        await sts_msg.edit(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Logged STS",
                description="I hab successfuwwy logged ur STS! owo~",
                color=GREEN_COLOR,
            ),
            view=None,
        )

    @commands.guild_only()
    @game.command(
        name="priority",
        description="Log Roweplay Pewmissions and Pwiowities in ur game uwu~",
        extras={"category": "Game Logging owo~"},
    )
    @is_staff()
    async def game_priority(self, ctx: commands.Context, duration: str, *, reason):
        bot = self.bot
        configItem = await bot.settings.find_by_id(ctx.guild.id)

        check_settings = self.check_missing(configItem, "priority")
        if not check_settings:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Configuwed >w<",
                    description="Game Pwiowity Logging is nyot configuwed. owo~",
                    color=BLANK_COLOR,
                )
            )

        channel = ctx.guild.get_channel(
            configItem["game_logging"]["priority"]["channel"]
        )
        if not channel:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Invawid Channel owo~",
                    description="Da Game Pwiowity logging channel is invawid.~",
                    color=BLANK_COLOR,
                )
            )

        view = CustomModalView(
            ctx.author.id,
            "Usew List uwu~",
            "Usew List uwu~",
            [
                (
                    "users",
                    discord.ui.TextInput(
                        placeholder="Da usews involved in da Pwiowity. Sepawate by lines.~\n\nExampwe: uwu~\nRoyalCwests uwu~\ni_iMikey\nmbrinkley",
                        label="Playews owo~",
                        style=discord.TextStyle.long,
                        min_length=1,
                        max_length=600,
                    ),
                ),
            ],
        )

        prio_msg = await ctx.reply(
            embed=discord.Embed(
                title="Usews Involved uwu~",
                description="What usews awe going to be involved wid dis pwiowity? >w<",
                color=BLANK_COLOR,
            ),
            view=view,
        )
        timeout = await view.wait()
        if timeout:
            return

        if view.modal.users:
            users = view.modal.users.value
        else:
            return

        users = users.split("\n")

        embed = discord.Embed(
            title="Pwiowity Logged uwu~",
            color=BLANK_COLOR,
        )

        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

        embed.add_field(
            name="Playews owo~",
            value="\n".join(
                [(f"**{index+1}.** " + player) for index, player in enumerate(users)]
            ),
            inline=False,
        )

        try:
            duration = time_converter(duration)
        except ValueError:
            return await prio_msg.edit(
                embed=discord.Embed(
                    title="Invawid Time~",
                    description="Dis time is nyot a vawid duwation. owo~",
                    color=BLANK_COLOR,
                )
            )

        embed.add_field(
            name="Pwiowity Infowmation owo~",
            value=(
                f"> **Staff:** {ctx.author.mention}\n"
                f"> **Duration:** {td_format(datetime.timedelta(seconds=duration))}\n"
                f"> **Reason:** {reason}\n"
                f"> **At:** <t:{int(ctx.message.created_at.timestamp())}>"
            ),
            inline=False,
        )

        if channel is None:
            return

        await channel.send(embed=embed)

        await prio_msg.edit(
            view=None,
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Logged Priority",
                description="I hab successfuwwy logged da pwiowity request.~",
                color=GREEN_COLOR,
            ),
        )


async def setup(bot):
    await bot.add_cog(GameLogging(bot))
