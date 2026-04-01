import datetime
import discord
import pytz
from discord.ext import commands
from discord import app_commands

from erm import is_staff, management_predicate, is_management
from utils.constants import BLANK_COLOR
from utils.paginators import SelectPagination, CustomPage
from utils.utils import require_settings, get_roblox_by_username
from utils.autocompletes import user_autocomplete, infraction_type_autocomplete


class Infractions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_manager_role(self, ctx):
        """Helpew medod to check if usew has managew rowe fwom settings"""
        settings = await self.bot.settings.find_by_id(ctx.guild.id)
        if not settings or "infractions" not in settings:
            return False

        manager_roles = settings["infractions"].get("manager_roles", [])
        return any(role.id in manager_roles for role in ctx.author.roles)

    @commands.hybrid_group(name="infractions")
    @is_staff()
    async def infractions(self, ctx):
        """Base command fow infwactions~"""
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                embed=discord.Embed(
                    title="Invawid Subcommand owo~",
                    description="Pwease specify a vawid subcommand~ >w<",
                    color=BLANK_COLOR,
                )
            )

    @commands.guild_only()
    @commands.hybrid_command(
        name="myinfractions",
        description="View uw infwactions~ uwu",
        extras={"category": "Infwactions >w<"},
    )
    @is_staff()
    @require_settings()
    async def myinfractions(self, ctx):
        """View ur infwactions owo~"""
        settings = await self.bot.settings.find_by_id(ctx.guild.id)
        if not settings:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Setup owo~",
                    description="Uw sewvew is nyot setup~ >w<",
                    color=BLANK_COLOR,
                )
            )

        if not settings.get("infractions"):
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Enabwed uwu~",
                    description="Infwactions awe nyot enabwed on dis sewvew~ nyaa uwu~",
                    color=BLANK_COLOR,
                )
            )

        infractions = []
        async for infraction in self.bot.db.infractions.find(
            {"guild_id": ctx.guild.id, "user_id": ctx.author.id}
        ).sort("timestamp", -1):
            infractions.append(infraction)

        if len(infractions) == 0:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyo Infwactions owo~",
                    description="U hav nyo infwactions~ owo",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        def setup_embed() -> discord.Embed:
            embed = discord.Embed(title="Uw Infwactions~", color=BLANK_COLOR)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            return embed

        embeds = []
        for infraction in infractions:
            if len(embeds) == 0 or len(embeds[-1].fields) >= 4:
                embeds.append(setup_embed())

            embed = embeds[-1]
            issuer = "System >w<"
            if infraction.get("issuer_id"):
                issuer = f"<@{infraction['issuer_id']}>"

            embed.add_field(
                name=f"Infraction #{infraction.get('_id', 'Unknown uwu~')}",
                value=(
                    f"> **Type:** {infraction['type']}\n"
                    f"> **Reason:** {infraction['reason']}\n"
                    f"> **Issuer:** {issuer}\n"
                    f"> **Date:** <t:{int(infraction['timestamp'])}:F>\n"
                    f"> **Status:** {'Wevoked~' if infraction.get('revoked', False) else 'Active >w<'}"
                ),
                inline=False,
            )

        pages = [
            CustomPage(embeds=[embed], identifier=str(index + 1))
            for index, embed in enumerate(embeds)
        ]

        if len(pages) > 1:
            paginator = SelectPagination(self.bot, ctx.author.id, pages=pages)
            await ctx.send(embed=embeds[0], view=paginator)
        else:
            await ctx.send(embed=embeds[0])

    @commands.guild_only()
    @infractions.command(
        name="view",
        description="View a usew's infwactions~ owo",
        extras={"category": "Infwactions >w<"},
    )
    @is_staff()
    @require_settings()
    @app_commands.describe(user="Da usew to check infwactions fow~ uwu")
    async def infractions_view(self, ctx, user: discord.Member):
        """View a usew's infwactions owo~"""
        if user.id != ctx.author.id:
            has_manager_role = await self.check_manager_role(ctx)
            if not has_manager_role and not await management_predicate(ctx):
                return await ctx.send(
                    embed=discord.Embed(
                        title="Pewmission Denied >w<",
                        description="U need management pewmissions to view odew usews' infwactions~ >w<",
                        color=BLANK_COLOR,
                    )
                )

        settings = await self.bot.settings.find_by_id(ctx.guild.id)
        if not settings:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Setup owo~",
                    description="Uw sewvew is nyot setup~ >w<",
                    color=BLANK_COLOR,
                )
            )

        if not settings.get("infractions"):
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Enabwed uwu~",
                    description="Infwactions awe nyot enabwed on dis sewvew~ nyaa uwu~",
                    color=BLANK_COLOR,
                )
            )

        target_id = user.id

        infractions = []
        async for infraction in self.bot.db.infractions.find(
            {"guild_id": ctx.guild.id, "user_id": target_id}
        ).sort("timestamp", -1):
            infractions.append(infraction)

        if len(infractions) == 0:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyo Infwactions owo~",
                    description=f"{'U hav owo~' if target_id == ctx.author.id else 'Dis usew has >w<'} nyo infwactions~ owo",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        def setup_embed() -> discord.Embed:
            name = None
            try:
                if target_id:
                    member = ctx.guild.get_member(target_id)
                    if member:
                        name = member.name
                    else:
                        user = self.bot.get_user(target_id)
                        if user:
                            name = user.name
            except:
                pass

            if not name:
                name = str(target_id)

            embed = discord.Embed(title=f"Infwactions fow {name}~", color=BLANK_COLOR)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            return embed

        embeds = []
        for infraction in infractions:
            if len(embeds) == 0 or len(embeds[-1].fields) >= 4:
                embeds.append(setup_embed())

            embed = embeds[-1]
            issuer = "System >w<"
            if infraction.get("issuer_id"):
                issuer = f"<@{infraction['issuer_id']}>"

            embed.add_field(
                name=f"Infraction #{infraction.get('_id', 'Unknown uwu~')}",
                value=(
                    f"> **Type:** {infraction['type']}\n"
                    f"> **Reason:** {infraction['reason']}\n"
                    f"> **Issuer:** {issuer}\n"
                    f"> **Date:** <t:{int(infraction['timestamp'])}:F>\n"
                    f"> **Status:** {'Wevoked~' if infraction.get('revoked', False) else 'Active >w<'}"
                ),
                inline=False,
            )

        pages = [
            CustomPage(embeds=[embed], identifier=str(index + 1))
            for index, embed in enumerate(embeds)
        ]

        if len(pages) > 1:
            paginator = SelectPagination(self.bot, ctx.author.id, pages=pages)
            await ctx.send(embed=embeds[0], view=paginator)
        else:
            await ctx.send(embed=embeds[0])

    @commands.guild_only()
    @infractions.command(name="issue", description="Issue an infwaction to a usew~ owo")
    @is_staff()
    @require_settings()
    @app_commands.autocomplete(type=infraction_type_autocomplete)
    @app_commands.describe(
        type="Da type of infwaction to give~ uwu",
        user="Da usew to issue an infwaction to~ owo",
        reason="What is uw weason fow giving dis infwaction? >w<",
    )
    async def infractions_issue(
        self, ctx, user: discord.Member, type: str, *, reason: str
    ):
        """Issue an infwaction to a usew owo~"""
        has_manager_role = await self.check_manager_role(ctx)
        if not has_manager_role and not await management_predicate(ctx):
            return await ctx.send(
                embed=discord.Embed(
                    title="Pewmission Denied >w<",
                    description="U need management pewmissions ow uw infwactions managew pewmission to issue infwactions~ >w<",
                    color=BLANK_COLOR,
                )
            )

        settings = await self.bot.settings.find_by_id(ctx.guild.id)
        if not settings:
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Setup owo~",
                    description="Uw sewvew is nyot setup~ >w<",
                    color=BLANK_COLOR,
                )
            )

        if not settings.get("infractions"):
            return await ctx.send(
                embed=discord.Embed(
                    title="Nyot Enabwed uwu~",
                    description="Infwactions awe nyot enabwed on dis sewvew~ nyaa uwu~",
                    color=BLANK_COLOR,
                )
            )

        target_id = user.id
        target_name = user.name

        infraction_config = next(
            (
                inf
                for inf in settings["infractions"]["infractions"]
                if inf["name"] == type
            ),
            None,
        )

        if not infraction_config:
            return await ctx.send(
                embed=discord.Embed(
                    title="Invawid Type uwu~",
                    description="Dis infwaction type does nyot exist~ nyaa uwu~",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        will_escalate = False
        existing_count = 0
        original_type = type
        current_type = type

        if infraction_config.get("escalation"):
            while True:
                threshold = infraction_config["escalation"].get("threshold", 0)
                next_infraction = infraction_config["escalation"].get("next_infraction")

                if not threshold or not next_infraction:
                    break

                existing_count = await self.bot.db.infractions.count_documents(
                    {
                        "user_id": target_id,
                        "guild_id": ctx.guild.id,
                        "type": current_type,
                        "revoked": {"$ne": True},
                    }
                )

                if (existing_count + 1) >= threshold:
                    next_config = next(
                        (
                            inf
                            for inf in settings["infractions"]["infractions"]
                            if inf["name"] == next_infraction
                        ),
                        None,
                    )
                    if not next_config:
                        break

                    current_type = next_infraction
                    will_escalate = True
                    infraction_config = next_config
                else:
                    break

        if will_escalate:
            type = current_type
            reason = (
                f"{reason}\n\nEscawated fwom {original_type} aftew weaching thweshowd~ owo"
            )

        # Create infraction document
        infraction_doc = {
            "user_id": target_id,
            "username": target_name,
            "guild_id": ctx.guild.id,
            "type": type,
            "original_type": original_type if will_escalate else None,
            "reason": reason,
            "timestamp": datetime.datetime.now(tz=pytz.UTC).timestamp(),
            "issuer_id": ctx.author.id,
            "issuer_username": ctx.author.name,
            "escalated": will_escalate,
            "escalation_count": existing_count + 1 if will_escalate else None,
        }

        result = await self.bot.db.infractions.insert_one(infraction_doc)
        infraction_doc["_id"] = result.inserted_id

        self.bot.dispatch("infraction_create", infraction_doc)

        target_name = str(target_id)
        try:
            member = ctx.guild.get_member(target_id)
            if member:
                target_name = member.name
            else:
                user = self.bot.get_user(target_id)
                if user:
                    target_name = user.name
                else:
                    roblox_user = await get_roblox_by_username(
                        str(target_id), self.bot, ctx
                    )
                    if roblox_user and not roblox_user.get("errors"):
                        target_name = roblox_user["name"]
        except:
            pass

        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Infwaction Issued~",
                description="S-successfuwwy issued an infwaction! hehe >w<",
                color=discord.Color.green(),
            ).add_field(
                name="Detaiws owo~",
                value=(
                    f"> **User:** {target_name}\n"
                    f"> **Type:** {type}\n"
                    f"> **Reason:** {reason}\n"
                    f"> **Issued By:** {ctx.author.mention}\n"
                    f"> **Date:** <t:{int(infraction_doc['timestamp'])}:F>\n"
                    f"> **ID:** `{result.inserted_id}`\n"
                    + (
                        f"> **Escawated:** Yes (fwom {original_type})"
                        if will_escalate
                        else ""
                    )
                ),
                inline=False,
            ),
            ephemeral=True,
        )

    @infractions.command(name="revoke", description="Wevoke an infwaction using its ID~ owo")
    @is_staff()
    @require_settings()
    @app_commands.describe(infraction_id="Da ID of da infwaction to wevoke~ uwu")
    async def infractions_revoke(self, ctx, infraction_id: str):
        """Revoke an infwaction >w<"""
        has_manager_role = await self.check_manager_role(ctx)
        if not has_manager_role and not await management_predicate(ctx):
            return await ctx.send(
                embed=discord.Embed(
                    title="Pewmission Denied >w<",
                    description="U need management pewmissions to wevoke infwactions~ >w<",
                    color=BLANK_COLOR,
                )
            )

        try:
            from bson import ObjectId

            infraction = await self.bot.db.infractions.find_one(
                {"_id": ObjectId(infraction_id)}
            )
            if not infraction:
                return await ctx.send(
                    embed=discord.Embed(
                        title="Nyot Found uwu~",
                        description="Nyo infwaction was found wid dat ID~ nyaa >w<",
                        color=BLANK_COLOR,
                    )
                )

            if infraction["guild_id"] != ctx.guild.id:
                return await ctx.send(
                    embed=discord.Embed(
                        title="Nyot Found uwu~",
                        description="Nyo infwaction was found wid dat ID in dis sewvew~ >w<",
                        color=BLANK_COLOR,
                    )
                )

            if infraction.get("revoked", False):
                return await ctx.send(
                    embed=discord.Embed(
                        title="Awweady Wevoked~",
                        description="Dis infwaction has awweady been wevoked~ nyaa owo~",
                        color=BLANK_COLOR,
                    )
                )

            await self.bot.db.infractions.update_one(
                {"_id": ObjectId(infraction_id)},
                {
                    "$set": {
                        "revoked": True,
                        "revoked_at": datetime.datetime.now(tz=pytz.UTC).timestamp(),
                        "revoked_by": ctx.author.id,
                    }
                },
            )

            infraction["revoked"] = True
            infraction["revoked_at"] = datetime.datetime.now(tz=pytz.UTC).timestamp()
            infraction["revoked_by"] = ctx.author.id
            self.bot.dispatch("infraction_revoke", infraction)

            await ctx.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Infwaction Wevoked~",
                    description="S-successfuwwy wevoked da infwaction! hehe owo~",
                    color=discord.Color.green(),
                )
            )

        except Exception as e:
            await ctx.send(
                embed=discord.Embed(
                    title="Ewwow uwu~",
                    description=f"An ewwow occuwwed whiwe wevoking da infwaction: {str(e)} >w<",
                    color=BLANK_COLOR,
                )
            )


async def setup(bot):
    await bot.add_cog(Infractions(bot))
