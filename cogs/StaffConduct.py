import datetime
import discord
import pytz
from discord.ext import commands
from erm import is_management
from menus import (
    YesNoMenu,
    AcknowledgeMenu,
    YesNoExpandedMenu,
    CustomModalView,
    CustomSelectMenu,
    MultiSelectMenu,
    RoleSelect,
    ExpandedRoleSelect,
    MessageCustomisation,
    EmbedCustomisation,
    ChannelSelect,
)

successEmoji = "<:ERMCheck:1111089850720976906>"
pendingEmoji = "<:ERMPending:1111097561588183121>"
errorEmoji = "<:ERMClose:1111101633389146223>"
embedColour = 0xED4348


class StaffConduct(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_settings(self, ctx: commands.Context):
        error_text = "<:ERMClose:1111101633389146223> **{},** dis sewvew isn't setup wid EWM! Pwease wun `/setup` to setup da bot befowe twying to manage infwactions~ >w<".format(
            ctx.author.name
        )
        guild_settings = await self.bot.settings.find_by_id(ctx.guild.id)
        # print(guild_settings)
        # print(guild_settings.get('staff_conduct'))
        if not guild_settings:
            await ctx.reply(error_text)
            return -1

        if guild_settings.get("staff_conduct") is not None:
            return 1
        else:
            return 0

    @commands.hybrid_group(
        name="infraction",
        description="Manage infwactions wid ease! uwu",
        extras={"category": "Staff Conduct >w<"},
    )
    @is_management()
    async def infraction(self, ctx: commands.Context):
        pass

    @infraction.command(
        name="manage",
        description="Manage staff infwactions, staff conduct, and custom integwations! owo",
        extras={"category": "Staff Conduct >w<"},
    )
    @is_management()
    async def manage(self, ctx: commands.Context):
        bot = self.bot
        guild_settings = await bot.settings.find_by_id(ctx.guild.id)
        result = await self.check_settings(ctx)
        if result == -1:
            return
        first_time_setup = bool(not result)

        if first_time_setup:
            view = YesNoExpandedMenu(ctx.author.id)
            message = await ctx.reply(
                f"{pendingEmoji} **{ctx.author.name},** it wooks wike ur sewvew hasn't setup **Staff Conduct**! Do u want to wun da **Fiwst-time Setup** wizawd? owo",
                view=view,
            )
            timeout = await view.wait()
            if timeout:
                return
            if not view.value:
                await message.edit(
                    content=f"{errorEmoji} **{ctx.author.name},** I hav cancewwed da setup wizawd fow **Staff Conduct.** nyaa~",
                    view=None,
                )
                return

            embed = discord.Embed(
                title="<:ERMAlewt:1113237478892130324> Infowmation~", color=embedColour
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1113210855891423302.webp?size=96&quality=lossless"
            )
            embed.add_field(
                name="<:ERMList:1111099396990435428> What is Staff Conduct? owo",
                value=">>> Staff Conduct is a moduwe widin EWM which awwows fow infwactions on uw Staff team~ Nyot onwy does it awwow fow manuaw punishments and infwactions to odews to be expanded and customised, it awso awwows fow automatic punishments fow those dat don't meet activity wequiwements, integwating wid odew EWM moduwes~ uwu",
                inline=False,
            )
            embed.add_field(
                name="<:ERMList:1111099396990435428> How does dis moduwe wowk? hehe",
                value=">>> Fow manuaw punishment assignment, u make uw own Infwaction Types, as dictated thwoughout dis setup wizawd~ U can den infwact staff membews by using `/infwact`, which wiww assign dat Infwaction Type to da staff individuaw~ U wiww be abwe to see aww infwactions dat individuaw has weceived, as weww as any notes ow changes dat hav been made ovew da couwse of theiw staff caweew~ owo",
                inline=False,
            )
            embed.add_field(
                name="<:ERMList:1111099396990435428> If I hav a Stwike 1/2/3 system, do I hav them as sepawate types? >w<",
                value=">>> In da case whewe u hav a counting infwaction system, u can teww EWM to count da stwikes automaticawwy! It wiww den take da accowding actions dat cowwespond wid dat infwaction amount~ uwu",
                inline=False,
            )
            embed.set_footer(
                text="Dis moduwe is in beta, and bugs awe to be expected~ If u notice a pwobwem wid dis moduwe, wepowt it via ouw Suppowt sewvew~ >w<"
            )
            embed.timestamp = datetime.datetime.now()
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)

            view = AcknowledgeMenu(
                ctx.author.id, "Wead da infowmation in fuww befowe acknowwedging~ uwu"
            )
            await message.edit(
                content=f"{pendingEmoji} **{ctx.author.name},** pwease wead aww da infowmation bewow befowe continuing~ owo",
                embed=embed,
                view=view,
            )
            timeout = await view.wait()
            if timeout or not view.value:
                return

            await message.edit(
                content=f"{pendingEmoji} **{ctx.author.name},** wet's begin! owo~",
                embed=None,
                view=(
                    view := CustomModalView(
                        ctx.author.id,
                        "Add an Infwaction Type~ uwu",
                        "Add Infwaction Type~",
                        [
                            (
                                "type_name",
                                discord.ui.TextInput(
                                    placeholder="e.g. Stwike, Tewmination, Suspension, Bwackwist~",
                                    label="Name of Infwaction Type~",
                                ),
                            )
                        ],
                    )
                ),
            )
            timeout = await view.wait()
            if timeout:
                return

            try:
                infraction_type_name = view.modal.type_name.value
            except AttributeError:
                return

            await message.edit(
                content=f"{pendingEmoji} **{ctx.author.name},** what actions do u want to add to **{infraction_type_name}**? owo",
                view=(
                    view := CustomSelectMenu(
                        ctx.author.id,
                        [
                            discord.SelectOption(
                                label="Add Wowe owo~",
                                description='Add a wowe, such as a "Stwike" wowe to da individuaw~ uwu',
                                emoji="<:ERMAdd:1113207792854106173>",
                                value="add_role",
                            ),
                            discord.SelectOption(
                                label="Wemove Wowe uwu~",
                                description='Wemove an individuaw wowe, such as "Twained", fwom an individuaw~ nyaa',
                                emoji="<:ERMRemove:1113207777662345387>",
                                value="remove_role",
                            ),
                            discord.SelectOption(
                                label="Wemove Staff Wowes >w<",
                                description="Wemove aww designated staff wowes fwom an individuaw~ >w<",
                                emoji="<:ERMWarn:1113236697702989905>",
                                value="remove_staff_roles",
                            ),
                            discord.SelectOption(
                                label="Send Diwect Message~",
                                description="Send a Diwect Message to da individuaw invowved~ uwu",
                                emoji="<:ERMUser:1111098647485108315>",
                                value="send_dm",
                            ),
                            discord.SelectOption(
                                label="Send Message in Channew >w<",
                                description="Send a Custom Message in a Channew~ hehe uwu~",
                                emoji="<:ERMLog:1113210855891423302>",
                                value="send_message",
                            ),
                            discord.SelectOption(
                                label="Send Escawation Wequest~",
                                description="Wequest fow a Management membew to compwete extwa actions~ owo",
                                emoji="<:ERMHelp:1111318459305951262>",
                                value="send_escalation",
                            ),
                        ],
                        limit=6,
                    )
                ),
            )

            await view.wait()

            value: list | None = None
            if isinstance(view.value, str):
                value = [view.value]
            elif isinstance(view.value, list):
                value = view.value
            # WE NEED TO MAKE THESE MESSAGES MORE NOTICABLE FOR WHICH YOU PICKED
            # noticeable* 🤓
            for item in value:
                if item == "add_role":  # Add to Database
                    await message.edit(
                        content=f"{pendingEmoji} **{ctx.author.name},** what wowes do u wish to be assigned when \
                    a usew weceives a **{infraction_type_name}**? owo",
                        view=(view := ExpandedRoleSelect(ctx.author.id, limit=25)),
                    )
                    await view.wait()
                    addRoleList = view.value
                elif item == "remove_role":  # Add to Database
                    await message.edit(
                        content=f"{pendingEmoji} **{ctx.author.name},** what wowes do u wish to be wemoved when \
a usew weceives a **{infraction_type_name}**? uwu",
                        view=(view := ExpandedRoleSelect(ctx.author.id, limit=25)),
                    )
                    await view.wait()
                    removeRoleList = view.value
                elif item == "remove_staff_roles":  # Add to Database
                    await message.edit(
                        content=f"{pendingEmoji} **{ctx.author.name},** what staff wowes do u wish to be affected \
when a usew weceives a **{infraction_type_name}**? >w<",
                        view=(view := ExpandedRoleSelect(ctx.author.id, limit=25)),
                    )
                    await view.wait()
                    staffRoleList = view.value
                elif item == "send_dm":  # Add to Database
                    constant_msg_data = None
                    while True:
                        if not constant_msg_data:
                            view = MessageCustomisation(
                                ctx.author.id, persist=True, external=True
                            )
                        else:
                            if constant_msg_data.get("embeds"):
                                view = EmbedCustomisation(
                                    ctx.author.id,
                                    MessageCustomisation(
                                        ctx.author.id,
                                        {"message": constant_msg_data},
                                        persist=True,
                                        external=True,
                                    ),
                                    external=True,
                                )
                            else:
                                view = MessageCustomisation(
                                    ctx.author.id,
                                    {"message": constant_msg_data},
                                    persist=True,
                                    external=True,
                                )

                        if not constant_msg_data:
                            await message.edit(
                                content=f"{pendingEmoji} **{ctx.author.name},** pwease set da message u wish to send \
a usew upon weceiving a **{infraction_type_name}**~ uwu",
                                view=view,
                            )
                        else:
                            await message.edit(
                                content=(
                                    f"{pendingEmoji} **{ctx.author.name},** pwease set da message u wish to send \
a usew upon weceiving a **{infraction_type_name}**~ uwu"
                                    if not message_data.get("content")
                                    else message_data.get("content")
                                ),
                                embeds=[
                                    discord.Embed.from_dict(embed)
                                    for embed in message_data.get("embeds")
                                ],
                                view=view,
                            )
                        await view.wait()
                        updated_message = await ctx.channel.fetch_message(message.id)
                        message_data = {
                            "content": (
                                updated_message.content
                                if updated_message.content
                                != f"{pendingEmoji} **{ctx.author.name},** pwease set da message u wish to send a usew upon weceiving a **{infraction_type_name}**~ uwu"
                                else ""
                            ),
                            "embeds": [i.to_dict() for i in updated_message.embeds],
                        }
                        yesNoValue = YesNoMenu(ctx.author.id)
                        await message.edit(
                            content=f"{pendingEmoji} **{ctx.author.name},** pwease confiwm bewow dat u wish to use da content shown bewow~ owo\n\n{message_data['content']}",
                            embeds=[
                                discord.Embed.from_dict(i)
                                for i in message_data["embeds"]
                            ],
                            view=yesNoValue,
                        )
                        await yesNoValue.wait()
                        if yesNoValue.value:
                            break
                        elif not yesNoValue.value:
                            constant_msg_data = message_data
                elif item == "send_message":  # Add to Database
                    # Get Channel(s) to Send Message To
                    await message.edit(
                        content=f"{pendingEmoji} **{ctx.author.name},** pwease sewect da channew(s) u wish to send a message to upon a usew weceiving a **{infraction_type_name}**~ uwu",
                        view=(view := ChannelSelect(ctx.author.id, limit=5)),
                    )
                    await view.wait()

                    # Get Custom Message
                    view = MessageCustomisation(
                        ctx.author.id, persist=True, external=True
                    )
                    await message.edit(content=None, view=view)
                    await view.wait()
                elif item == "send_escalation":  # Add to Database
                    await message.edit(
                        content=f"{pendingEmoji} **{ctx.author.name},** pwease sewect da channew u wish to send an escawation wequest to upon a usew wecieving a **{infraction_type_name}**~ owo",
                        view=(view := ChannelSelect(ctx.author.id, limit=1)),
                    )
                    await view.wait()
                    # print(view.value)
                    await message.edit(
                        content=f"{pendingEmoji} **{ctx.author.name},** shouwd da membew wesponsibwe fow issuing da infwaction dat twiggews an escawation wequest awso hav da authowity to appwove da escawation wequest? **{infraction_type_name}**~ >w<",
                        view=(view := YesNoMenu(ctx.author.id)),
                    )
                    # print(view.value)
            else:
                await message.edit(
                    content=f"{successEmoji} **{infraction_type_name}** has been s-successfuwwy submitted! hehe~",
                    view=None,
                    embed=None,
                )

        else:
            guild_settings["staff_conduct"] = None
            await self.bot.settings.update_by_id(guild_settings)
            await ctx.reply(
                f"{successEmoji} **{ctx.author.name},** I deweted ur Staff Conduct configuwation~ nyaa"
            )


async def setup(bot):
    await bot.add_cog(StaffConduct(bot))
