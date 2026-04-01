import discord
from discord.ext import commands

from menus import YesNoMenu, AccountLinkingMenu
from utils.constants import BLANK_COLOR, GREEN_COLOR
import asyncio
import time


class OAuth2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="link",
        description="Wink uw Wobwox account wid EWM~ owo",
        extras={"ephemeral": True},
    )
    async def link_roblox(self, ctx: commands.Context):
        msg = None
        linked_account = await self.bot.oauth2_users.db.find_one(
            {"discord_id": ctx.author.id}
        )
        if linked_account:
            user = await self.bot.roblox.get_user(linked_account["roblox_id"])
            msg = await ctx.send(
                embed=discord.Embed(
                    title="Awweady Winked owo~",
                    description=f"U hav awweady winked ur account with `{user.name}`. Awe u suwe u wouwd wike to wewink? >w<",
                    color=BLANK_COLOR,
                ),
                view=(view := YesNoMenu(ctx.author.id)),
            )
            timeout = await view.wait()
            if timeout or not view.value:
                await msg.edit(
                    embed=discord.Embed(
                        title="Cancewwed uwu~",
                        description="Dis action was cancewwed by da usew~ nyaa uwu~",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )
                return
        timestamp = time.time()
        verification_message = {
            "embed": discord.Embed(
                title="Vewify wid EWM uwu",
                description="**To wink uw account wid EWM, cwick da button bewow~ owo**\nIf u encountew an ewwow, pwease contact EWM Suppowt by wunning `/suppowt`.",
                color=BLANK_COLOR,
            ),
            "view": AccountLinkingMenu(self.bot, ctx.author, ctx.interaction),
        }

        await self.bot.pending_oauth2.db.insert_one({"discord_id": ctx.author.id})

        if msg is None:
            await ctx.send(**verification_message)
        else:
            await msg.edit(**verification_message)

        attempts = 0
        while await asyncio.sleep(3):
            if attempts > 60:
                break
            if not linked_account:
                if await self.bot.oauth2_users.db.find_one(
                    {"discord_id": ctx.author.id}
                ):
                    await msg.edit(
                        embed=discord.Embed(
                            title=f"{self.bot.emoji_controller.get_emoji('success')} Winked",
                            description="Uw Wobwox account has been s-successfuwwy winked to EWM~ hehe",
                            color=GREEN_COLOR,
                        )
                    )
                    break
            else:
                if item := await self.bot.oauth2_users.db.find_one(
                    {"discord_id": ctx.author.id}
                ):
                    if item.get("last_updated", 0) > timestamp:
                        await msg.edit(
                            embed=discord.Embed(
                                title=f"{self.bot.emoji_controller.get_emoji('success')} Linked",
                                description="Ur Roblox account has been successfuwwy linked to ERM. >w<",
                                color=GREEN_COLOR,
                            )
                        )
                        break
                else:
                    linked_account = None


async def setup(bot):
    await bot.add_cog(OAuth2(bot))
