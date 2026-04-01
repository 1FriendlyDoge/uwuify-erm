import discord
from discord import app_commands
from discord.ext import commands

from erm import is_management, is_admin
from utils.constants import BLANK_COLOR, GREEN_COLOR
from utils.utils import generator
from menus import (
    ChannelSelect,
    CustomModalView,
    CustomSelectMenu,
    EmbedCustomisation,
    MessageCustomisation,
    RemoveCustomCommand,
    YesNoColourMenu,
    CustomCommandOptionSelect,
    CustomCommandModification,
    CounterButton,
    ViewVotersButton,
)
from utils.autocompletes import command_autocomplete
from utils.utils import (
    interpret_content,
    interpret_embed,
    invis_embed,
    request_response,
    log_command_usage,
)


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="custom")
    @is_admin()
    async def custom(self, ctx):
        pass

    @commands.guild_only()
    @custom.command(
        name="manage",
        description="Manage uw custom commands~ uwu",
        extras={"category": "Custom Commands >w<"},
    )
    @is_admin()
    async def custom_manage(self, ctx):
        bot = self.bot
        Data = await bot.custom_commands.find_by_id(ctx.guild.id)
        await log_command_usage(self.bot, ctx.guild, ctx.author, f"Custom Manage")
        if Data is None:
            Data = {"_id": ctx.guild.id, "commands": []}

        embeds = []
        current_embed = (
            discord.Embed(title="Custom Commands~", color=BLANK_COLOR)
            .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            .set_thumbnail(url=ctx.guild.icon)
        )

        for item in Data["commands"]:
            if len(current_embed.fields) >= 10:
                embeds.append(current_embed)
                current_embed = discord.Embed(
                    title="Custom Commands (cont.)~", color=BLANK_COLOR
                )

            current_embed.add_field(
                name=f"{item['name']}",
                value=f"> **Name:** {item['name']}\n"
                f"> **Command ID:** `{item['id']}`\n"
                f"> **Creator:** {'<@{}>'.format(item.get('author') if item.get('author') is not None else '1')}\n"
                f"> **Defauwt Channew:** {'<#{}>'.format(item.get('channel')) if item.get('channel') is not None else 'Nyone sewected~'}",
                inline=False,
            )

        if len(current_embed.fields) == 0:
            current_embed.add_field(
                name="Nyo Custom Commands uwu~",
                value=f"> Nyo Custom Commands wewe found to be associated with dis sewvew~ >w<",
            )

        embeds.append(current_embed)

        view = CustomCommandOptionSelect(ctx.author.id)

        new_msg = await ctx.reply(
            embeds=embeds,
            view=view,
        )

        timeout = await view.wait()
        if timeout:
            return

        if view.value == "create":
            name = view.modal.name.value
            data = {
                "name": name,
                "id": next(generator),
                "message": None,
                "author": ctx.author.id,
            }
            view = CustomCommandModification(ctx.author.id, data)
            # timeout = await view.wait()
            # if timeout:
            #     return
            await new_msg.edit(
                view=view,
                embed=discord.Embed(
                    title="Custom Commands~",
                    description=(
                        "**Command Infowmation**\n"
                        f"> **Command ID:** `{data['id']}`\n"
                        f"> **Command Name:** {data['name']}\n"
                        f"> **Cweatow:** <@{data.get('author', '0')}>\n"  # this is just to be sure that author actually exists!
                        f"> **Defauwt Channew:** {'<#{}>'.format(data.get('channel')) if data.get('channel') is not None else 'Nyone sewected~'}\n"
                        f"\n**Message:**\n"
                        f"View da message bewow by cwicking 'View Message'~ uwu"
                    ),
                    color=BLANK_COLOR,
                ),
            )
            await view.wait()
            data = view.command_data

            for item in Data["commands"]:
                if item["name"] == name:
                    return await ctx.reply(
                        embed=discord.Embed(
                            title="Command Mismatch >w<",
                            description="Dis custom command awweady exists~ >w<",
                            color=BLANK_COLOR,
                        )
                    )

            custom_command_data = {
                "_id": ctx.guild.id,
                "commands": [data],
            }

            if Data:
                Data["commands"].append(data)
            else:
                Data = custom_command_data

            await bot.custom_commands.upsert(Data)
            await new_msg.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Command Cweated~",
                    description="Dis custom command has been s-successfuwwy cweated~ hehe uwu~",
                    color=GREEN_COLOR,
                ),
                view=None,
            )
        elif view.value == "edit":
            try:
                id_var = int(view.modal.id.value)
            except ValueError:
                return await new_msg.edit(
                    embed=discord.Embed(
                        title="Invawid Fowmat owo~",
                        description="A Custom Command ID may onwy contain numbews, nyot wettews~ >w<",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )
            command_id = None
            existing_command_data = None
            for item in Data["commands"]:
                if item["id"] == id_var:
                    command_id = item["id"]
                    existing_command_data = item
                    break

            if command_id is None:
                await new_msg.edit(
                    embed=discord.Embed(
                        title="Command Mismatch >w<",
                        description="Dis custom command doesn't exist~ nyaa~",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )
                return

            if existing_command_data is None:
                await new_msg.edit(
                    embed=discord.Embed(
                        title="Command Mismatch >w<",
                        description="Dis custom command doesn't exist~ nyaa~",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )
                return

            data = {}
            try:
                data = existing_command_data
            except KeyError:
                await new_msg.edit(
                    embed=discord.Embed(
                        title="Command Mismatch >w<",
                        description="Dis custom command doesn't exist~ nyaa~",
                        color=BLANK_COLOR,
                    )
                )
                return
            view = CustomCommandModification(ctx.author.id, data)
            await new_msg.edit(
                view=view,
                embed=discord.Embed(
                    title="Custom Commands~",
                    description=(
                        "**Command Infowmation**\n"
                        f"> **Command ID:** `{data['id']}`\n"
                        f"> **Command Name:** {data['name']}\n"
                        f"> **Cweatow:** <@{data['author']}>\n"
                        f"> **Defauwt Channew:** {'<#{}>'.format(data.get('channel')) if data.get('channel') is not None else 'Nyone sewected~'}\n"
                        f"\n**Message:**\n"
                        f"View da message bewow by cwicking 'View Message'~ uwu"
                    ),
                    color=BLANK_COLOR,
                ),
            )
            await view.wait()
            data = view.command_data
            for index, item in enumerate(Data["commands"]):
                if item["id"] == command_id:
                    Data["commands"][index] = data
                    break
            await bot.custom_commands.upsert(Data)
            return await new_msg.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Command Edited~",
                    description="Dis custom command has been s-successfuwwy edited~ hehe >w<",
                    color=GREEN_COLOR,
                ),
                view=None,
            )
        elif view.value == "delete":
            identifier = view.modal.name.value

            for index, item in enumerate(Data["commands"]):
                if str(item["name"]).strip() == str(identifier).strip():
                    Data["commands"].pop(index)
                    await bot.custom_commands.update_by_id(Data)
                    break
            else:
                return await new_msg.edit(
                    embed=discord.Embed(
                        title="Command Mismatch >w<",
                        description="Dis custom command doesn't exist~ nyaa~",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )

            return await new_msg.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Deweted Command~",
                    description="Dis custom command has been s-successfuwwy deweted~ nyaa uwu~",
                    color=GREEN_COLOR,
                ),
                view=None,
            )

    @custom.command(
        name="run",
        description="Wun a custom command~ owo",
        extras={"category": "Custom Commands >w<", "ephemeral": True},
    )
    @app_commands.autocomplete(command=command_autocomplete)
    @is_admin()
    @app_commands.describe(command="What custom command wouwd u wike to wun? owo")
    @app_commands.describe(
        channel="Whewe do u want dis custom command's output to go? (e.g. #genewaw)~ uwu"
    )
    async def run(self, ctx, command: str, channel: discord.TextChannel = None):
        bot = self.bot
        Data = await bot.custom_commands.find_by_id(ctx.guild.id)
        if Data is None:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Nyo Commands >w<",
                    description="Dewe awe nyo custom commands in dis sewvew~ >w<",
                )
            )

        is_command = False
        selected = None
        if isinstance(Data.get("commands"), list):
            for cmd in Data["commands"]:
                if cmd["name"].lower().replace(" ", "") == command.lower().replace(
                    " ", ""
                ):
                    is_command = True
                    selected = cmd

        if not is_command:
            return await ctx.reply(
                embed=discord.Embed(
                    title="Command Mismatch >w<",
                    description="Dis custom command doesn't exist. uwu~",
                    color=BLANK_COLOR,
                )
            )

        if selected.get("channel") and channel is None:
            try:
                channel = await ctx.guild.fetch_channel(selected["channel"])
            except discord.HTTPException:
                channel = None

            if channel is None:  # Channel doesn't exist
                channel = ctx.channel
        elif channel is None:
            channel = ctx.channel

        embeds = []
        if selected["message"]["embeds"] is not None:
            for embed in selected["message"]["embeds"]:
                embeds.append(
                    await interpret_embed(bot, ctx, channel, embed, selected["id"])
                )
        elif selected["message"]["embeds"] is None:
            pass

        view = discord.ui.View()
        for item in selected.get("buttons", []):
            if item["label"] == "0" and "row" in item:
                counter_button = CounterButton(row=item["row"])
                view_voters_button = ViewVotersButton(
                    row=item["row"], counter_button=counter_button
                )
                view.add_item(counter_button)
                view.add_item(view_voters_button)
            else:
                view.add_item(
                    discord.ui.Button(
                        label=item["label"],
                        url=item["url"],
                        row=item["row"],
                        style=discord.ButtonStyle.url,
                    )
                )

        if ctx.interaction:
            if (
                selected["message"]["content"] in [None, ""]
                and len(selected["message"]["embeds"]) == 0
            ):
                return await ctx.interaction.followup.send(
                    embed=discord.Embed(
                        title="Empty Command uwu~",
                        description="Due to Discowd wimitations, I am unabwe to send uw wemindew~ Uw message is most wikewy empty~ >w<",
                        color=BLANK_COLOR,
                    )
                )
            await ctx.interaction.followup.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Command Wan~",
                    description=f"I've just wan da custom command in {channel.mention}~ hehe",
                    color=GREEN_COLOR,
                )
            )
            msg = await channel.send(
                content=await interpret_content(
                    bot, ctx, channel, selected["message"]["content"], selected["id"]
                ),
                embeds=embeds,
                view=view,
                allowed_mentions=discord.AllowedMentions(
                    everyone=True, users=True, roles=True, replied_user=True
                ),
            )

            # Fetch ICS entry
            doc = await bot.ics.find_by_id(selected["id"]) or {}
            if doc is None:
                return
            doc["associated_messages"] = (
                [(channel.id, msg.id)]
                if not doc.get("associated_messages")
                else doc["associated_messages"] + [(channel.id, msg.id)]
            )
            doc["_id"] = [ctx.guild.id]
            await bot.ics.update_by_id(doc)
        else:
            if (
                selected["message"]["content"] in [None, ""]
                and len(selected["message"]["embeds"]) == 0
            ):
                return await ctx.reply(
                    embed=discord.Embed(
                        title="Empty Command uwu~",
                        description="Due to Discowd wimitations, I am unabwe to send uw wemindew~ Uw message is most wikewy empty~ >w<",
                        color=BLANK_COLOR,
                    )
                )
            await ctx.reply(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Command Wan~",
                    description=f"I've just wan da custom command in {channel.mention}~ hehe",
                    color=GREEN_COLOR,
                )
            )

            msg = await channel.send(
                content=await interpret_content(
                    bot, ctx, channel, selected["message"]["content"], selected["id"]
                ),
                embeds=embeds,
                view=view,
                allowed_mentions=discord.AllowedMentions(
                    everyone=True, users=True, roles=True, replied_user=True
                ),
            )

            # Fetch ICS entry
            doc = await bot.ics.find_by_id(selected["id"]) or {}
            if doc is None:
                return
            doc["associated_messages"] = (
                [(channel.id, msg.id)]
                if not doc.get("associated_messages")
                else doc["associated_messages"] + [(channel.id, msg.id)]
            )
            doc["_id"] = doc.get("_id") or selected["id"]
            await bot.ics.update_by_id(doc)


async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
