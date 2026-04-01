from copy import copy
from pprint import pformat

import discord
from discord import HTTPException
from discord.ext import commands
from copy import deepcopy

from erm import check_privacy, generator, is_management
from utils.constants import blank_color, BLANK_COLOR
from menus import (
    ChannelSelect,
    CustomSelectMenu,
    ERLCIntegrationConfiguration,
    RoleSelect,
    YesNoColourMenu,
    NextView,
    BasicConfiguration,
    LOAConfiguration,
    ShiftConfiguration,
    RAConfiguration,
    PunishmentsConfiguration,
    GameSecurityConfiguration,
    GameLoggingConfiguration,
    AntipingConfiguration,
    ActivityNoticeManagement,
    PunishmentManagement,
    ShiftLoggingManagement,
    ERMCommandLog,
    WhitelistVehiclesManagement,
    PriorityRequestConfiguration,
)
from ui.MapleCounty import MapleCountyConfiguration
from utils.paginators import CustomPage, SelectPagination
from utils.utils import require_settings, generator, log_command_usage


class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.hybrid_command(
        name="setup",
        description="Begin using ERM!~",
        extras={"category": "Configuwation~"},
    )
    @is_management()
    async def _setup(self, ctx: commands.Context):
        await log_command_usage(self.bot, ctx.guild, ctx.author, f"Setup")
        bot = self.bot
        from utils.constants import base_configuration

        current_settings = None
        # del base_configuration['_id']
        modifications = {
            "_id": ctx.guild.id,
            **deepcopy(base_configuration),
        }  # we create a deep copy because we don't want to modify the base configuration
        msg = None

        current_settings = await bot.settings.find_by_id(ctx.guild.id)
        if current_settings:
            msg = await ctx.send(
                embed=discord.Embed(
                    title="Alweady Setup uwu~",
                    description="U've alweady setup ERM in dis sewvew! Awe u suwe u wouwd like to go thwough da setup pwocess again?",
                    color=blank_color,
                ),
                view=(confirmation_view := YesNoColourMenu(ctx.author.id)),
            )
            timeout = await confirmation_view.wait()
            if confirmation_view.value is False:
                return await msg.edit(
                    embed=discord.Embed(
                        title="Successfuwwy Cancewwed owo~",
                        description="Cancewwed da setup pwocess fow dis sewvew. Aww settings hab been kept.",
                        color=blank_color,
                    ),
                    view=None,
                )

        if msg is None:
            msg = await ctx.send(
                embed=discord.Embed(
                    title="Let's get stawted!~",
                    description="To setup ERM, pwess da awwow button bewow! owo~",
                    color=blank_color,
                ),
                view=(next_view := NextView(bot, ctx.author.id)),
            )
        else:
            await msg.edit(
                embed=discord.Embed(
                    title="Let's get stawted!~",
                    description="To setup ERM, pwess da awwow button bewow! owo~",
                    color=blank_color,
                ),
                view=(next_view := NextView(bot, ctx.author.id)),
            )

        timeout = await next_view.wait()
        if timeout or not next_view.value:
            await msg.edit(
                embed=discord.Embed(
                    title="Cancewwed >w<",
                    description="U hab took too long to complete dis pawt of da setup. uwu~",
                    color=blank_color,
                ),
                view=None,
            )
            return

        secret_key = next(generator)

        def get_active_view_state() -> discord.ui.View | None:
            return self.bot.view_state_manager.get(secret_key)

        def set_active_view_state(view: discord.ui.View):
            self.bot.view_state_manager[secret_key] = view

        async def discard_unlock_override(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return
            await interaction.response.defer()

        async def check_unlock_override(interaction: discord.Interaction):
            view = get_active_view_state()
            if interaction.user != ctx.author:
                return
            # if view is None:
            #     return
            await interaction.response.defer()

            impurities = []
            for item in view.children:
                if (
                    isinstance(item, discord.ui.Select)
                    or isinstance(item, discord.ui.RoleSelect)
                    or isinstance(item, discord.ui.ChannelSelect)
                ):
                    if item.callback != discard_unlock_override:
                        if len(item.values) == 0:
                            impurities.append(item)
            # print(impurities)
            if len(impurities) == 0:
                buttons = list(
                    filter(lambda x: isinstance(x, discord.ui.Button), view.children)
                )
                # print(buttons)
                if len(buttons) != 0:
                    buttons[0].disabled = False
                    for item in view.children:
                        if isinstance(item, discord.ui.Select):
                            value = item.values[0]
                            stored_index = 0
                            for index, obj in enumerate(item.options):
                                if obj.value == value:
                                    stored_index = index
                            item.options[stored_index].default = True
                            for select_opt in item.options:
                                if item.options[stored_index] != select_opt:
                                    select_opt.default = False
                            # print(f'defaults: {len([i for i in item.options if i.default is True])}')
                    await interaction.message.edit(view=view)
            else:
                buttons = list(
                    filter(lambda x: isinstance(x, discord.ui.Button), view.children)
                )
                # print(buttons)
                if len(buttons) != 0:
                    if buttons[0].disabled is False:
                        buttons[0].disabled = True
                        await interaction.message.edit(view=view)

        async def callback_override(interaction: discord.Interaction, *args, **kwargs):
            await interaction.response.defer()

        basic_settings = discord.ui.View()
        next_button = NextView(bot, ctx.author.id).children[0]
        next_button.row = 4
        next_button.disabled = True

        staff_roles = RoleSelect(ctx.author.id).children[0]
        staff_roles.row = 0
        staff_roles.placeholder = "Staff Rowes >w<"
        staff_roles.callback = check_unlock_override
        staff_roles.min_values = 0

        admin_roles = RoleSelect(ctx.author.id).children[0]
        admin_roles.row = 1
        admin_roles.placeholder = "Admin Rowes >w<"
        admin_roles.callback = discard_unlock_override
        admin_roles.min_values = 0

        management_roles = RoleSelect(ctx.author.id).children[0]
        management_roles.row = 2
        management_roles.placeholder = "Management Rowes >w<"
        management_roles.callback = check_unlock_override
        management_roles.min_values = 0

        prefix_view = CustomSelectMenu(
            ctx.author.id,
            [
                discord.SelectOption(
                    label="!", description="Use '!' as ur custom pwefix.~"
                ),
                discord.SelectOption(
                    label=">", description="Use '>' as ur custom pwefix.~"
                ),
                discord.SelectOption(
                    label="?", description="Use '?' as ur custom pwefix. owo~"
                ),
                discord.SelectOption(
                    label=":", description="Use ':' as ur custom pwefix. >w<"
                ),
                discord.SelectOption(
                    label="-", description="Use '-' as ur custom pwefix. >w<"
                ),
            ],
        )
        prefix = prefix_view.children[0]
        prefix.row = 3
        prefix.placeholder = "Pwefix~"
        prefix.callback = check_unlock_override

        async def stop_override(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return
            await interaction.response.defer()
            get_active_view_state().stop()

        # prefix.callback = callback_override
        next_button.callback = stop_override

        for item in [staff_roles, admin_roles, management_roles, prefix, next_button]:
            basic_settings.add_item(item)

        set_active_view_state(basic_settings)

        await msg.edit(
            embed=discord.Embed(
                title="Basic Settings >w<",
                description=(
                    "**Staff Rowe:** A staff rowe is da rowe dat is going to be abwe to use most ERM commands. U'd assign dis rowe to da peopwe u want to be abwe to use ERM's cowe functionawities.\n\n"
                    "**Admin Rowe:** An admin rowe is da rowe dat can manage LOAs, RAs & odew peoples' shifts but it can nyot use sewvew manage and config.\n\n"
                    "**Management Rowe:** A management rowe is da rowes of ur sewvew management membews. These peopwe wiww be abwe to dewete punishments, modify peopwe's shift time, and accept LOA Requests.\n\n"
                    "**Pwefix:** Dis wiww be a pwefix u awe abwe to use instead of ouw slash command system. U can use dis pwefix to execute commands slightwy fastew and to take advantage of some extwa featuwes."
                ),
                color=blank_color,
            ),
            view=basic_settings,
        )
        await basic_settings.wait()

        for item in basic_settings.children:
            if isinstance(item, discord.ui.Select) or isinstance(
                item, discord.ui.RoleSelect
            ):
                if len(item.values) > 0:
                    if item.placeholder == "Staff Rowes >w<":
                        modifications["staff_management"]["role"] = [
                            i.id for i in item.values
                        ]
                    if item.placeholder == "Pwefix~":
                        modifications["customisation"]["prefix"] = item.values[0]
                    elif item.placeholder == "Management Rowes >w<":
                        modifications["staff_management"]["management_role"] = [
                            i.id for i in item.values
                        ]
                    elif item.placeholder == "Admin Rowes >w<":
                        modifications["staff_management"]["admin_role"] = [
                            i.id for i in item.values
                        ]

        loa_requests_settings = discord.ui.View()

        loa_channel_view = ChannelSelect(ctx.author.id, limit=1)
        loa_channel_select = loa_channel_view.children[0]
        loa_channel_select.placeholder = "LOA Channel uwu~"
        loa_channel_select.row = 1

        loa_role_view = RoleSelect(ctx.author.id, limit=1)
        loa_role_select = loa_role_view.children[0]
        loa_role_select.placeholder = "LOA Rowe uwu~"
        loa_role_select.row = 2

        loa_enabled_view = CustomSelectMenu(
            ctx.author.id,
            [
                discord.SelectOption(
                    label="Enabled >w<",
                    value="enabled",
                    description="LOA Requests awe enabled. owo~",
                ),
                discord.SelectOption(
                    label="Disabled owo~",
                    value="disabled",
                    description="LOA Requests awe disabled. uwu~",
                ),
            ],
        )
        loa_enabled_select = loa_enabled_view.children[0]
        loa_enabled_select.callback = callback_override
        loa_enabled_select.row = 0
        loa_enabled_select.placeholder = "LOA Requests uwu~"

        next_view = NextView(bot, ctx.author.id)
        next_button = next_view.children[0]
        next_button.callback = stop_override
        next_button.row = 4

        for item in [
            loa_enabled_select,
            loa_role_select,
            loa_channel_select,
            next_button,
        ]:
            loa_requests_settings.add_item(item)

        await msg.edit(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('loa')} LOA Requests",
                description=(
                    "**Enabled:** Dis setting enables ow disables da LOA Requests moduwe. When enabled, dis awwows ur staff membews to fiww out Leave of Absence requests fow ur management membews to appwove.\n\n"
                    "**LOA Rowe:** Dis rowe is given to those who awe on Leave of Absence, and is removed when they go off Leave of Absence.\n\n"
                    "**LOA Channel:** Dis channel wiww be whewe Leave of Absence requests wiww be logged, and whewe they wiww be accepted ow denied. Make suwe dis is a channel dat Management membews can see, so dat they can appwove LOA requests."
                ),
                color=blank_color,
            ),
            view=loa_requests_settings,
        )

        set_active_view_state(loa_requests_settings)
        await loa_requests_settings.wait()

        for item in loa_requests_settings.children:
            if (
                isinstance(item, discord.ui.Select)
                or isinstance(item, discord.ui.RoleSelect)
                or isinstance(item, discord.ui.ChannelSelect)
            ):
                if len(item.values) > 0:
                    if item.placeholder == "LOA Rowe uwu~":
                        modifications["staff_management"]["loa_role"] = [
                            r.id for r in item.values
                        ]
                    elif item.placeholder == "LOA Channel uwu~":
                        modifications["staff_management"]["channel"] = item.values[0].id
                    elif item.placeholder == "LOA Requests uwu~":
                        modifications["staff_management"]["enabled"] = bool(
                            item.values[0] == "enabled"
                        )

        ra_requests_settings = discord.ui.View()

        ra_role_view = RoleSelect(ctx.author.id, limit=1)
        ra_role_select = ra_role_view.children[0]
        ra_role_select.placeholder = "RA Rowe uwu~"
        ra_role_select.row = 2
        ra_role_select.min_values = 0

        next_view = NextView(bot, ctx.author.id)
        next_button = next_view.children[0]
        next_button.callback = stop_override
        next_button.row = 4

        for item in [ra_role_select, next_button]:
            ra_requests_settings.add_item(item)

        await msg.edit(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('loa')} RA Requests",
                description=(
                    "**What awe RA Requests?** RA Requests, also cawwed Reduced Activity Requests, awe a fowm of Leave of Absence whewe da staff membew isn't requiwed to complete da fuww quota, but expects dat they wiww be abwe to complete it pawtiawwy.\n\n"
                    "**RA Rowe:** Dis rowe is given to those who awe on Reduced Activity, and is removed when they go off Reduced Activity.\n\n"
                ),
                color=blank_color,
            ),
            view=ra_requests_settings,
        )
        set_active_view_state(ra_requests_settings)

        await ra_requests_settings.wait()

        for item in ra_requests_settings.children:
            if isinstance(item, discord.ui.Select) or isinstance(
                item, discord.ui.RoleSelect
            ):
                if len(item.values) > 0:
                    if item.placeholder == "RA Rowe uwu~":
                        modifications["staff_management"]["ra_role"] = item.values[0].id

        punishment_settings = discord.ui.View()

        next_view = NextView(bot, ctx.author.id)
        next_button = next_view.children[0]
        next_button.callback = stop_override
        next_button.row = 4

        punishment_channel_view = ChannelSelect(ctx.author.id, limit=1)
        punishment_channel_select: discord.ui.ChannelSelect = (
            punishment_channel_view.children[0]
        )
        punishment_channel_select.min_values = 0
        punishment_channel_select.placeholder = "Punishments Channel owo~"
        punishment_channel_select.row = 1

        punishments_enabled_view = CustomSelectMenu(
            ctx.author.id,
            [
                discord.SelectOption(
                    label="Enabled >w<",
                    value="enabled",
                    description="ROBLOX Punishments awe enabled. >w<",
                ),
                discord.SelectOption(
                    label="Disabled owo~",
                    value="disabled",
                    description="ROBLOX Punishments awe disabled. >w<",
                ),
            ],
        )
        punishments_enabled_item = punishments_enabled_view.children[0]
        punishments_enabled_item.placeholder = "ROBLOX Punishments uwu~"
        punishments_enabled_item.row = 0
        punishments_enabled_item.callback = callback_override

        for item in [punishments_enabled_item, punishment_channel_select, next_button]:
            punishment_settings.add_item(item)

        await msg.edit(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('log')} ROBLOX Punishments",
                description=(
                    "**What is da ROBLOX Punishments moduwe?** Da ROBLOX Punishments moduwe awwows fow membews of ur Staff Team to log punishments against a ROBLOX playew using ERM! U can specify custom types of punishments, whewe they wiww go, as weww as manage and seawch individuaw punishments.\n\n"
                    "**Enabled:** Dis setting toggles da ROBLOX Punishments moduwe. When enabled, staff membews wiww be abwe to use `/punish`, and management membews wiww be abwe to additionawwy use `/punishment manage`.\n\n"
                    "**Punishments Channel:** Dis is whewe most punishments made wid da ROBLOX Punishments go. Any logged actions of a ROBLOX playew wiww go to dis channel."
                ),
                color=blank_color,
            ),
            view=punishment_settings,
        )
        set_active_view_state(punishment_settings)
        await punishment_settings.wait()

        for item in punishment_settings.children:
            if (
                isinstance(item, discord.ui.Select)
                or isinstance(item, discord.ui.RoleSelect)
                or isinstance(item, discord.ui.ChannelSelect)
            ):
                if len(item.values) > 0:
                    if item.placeholder == "ROBLOX Punishments uwu~":
                        if not modifications.get("punishments"):
                            modifications["punishments"] = {}
                        modifications["punishments"]["enabled"] = bool(
                            item.values[0] == "enabled"
                        )
                    elif item.placeholder == "Punishments Channel owo~":
                        if not modifications.get("punishments"):
                            modifications["punishments"] = {}
                        modifications["punishments"]["channel"] = item.values[0].id

        shift_management_settings = discord.ui.View()

        shift_enabled_view = CustomSelectMenu(
            ctx.author.id,
            [
                discord.SelectOption(
                    label="Enabled >w<",
                    value="enabled",
                    description="Enabwe da Shift Management moduwe. >w<",
                ),
                discord.SelectOption(
                    label="Disabled owo~",
                    value="disabled",
                    description="Disabwe da Shift Management moduwe. uwu~",
                ),
            ],
        )
        shift_enabled_select = shift_enabled_view.children[0]
        shift_enabled_select.placeholder = "Shift Management~"
        shift_enabled_select.row = 0
        shift_enabled_select.callback = callback_override

        shift_channel_view = ChannelSelect(ctx.author.id, limit=1)
        shift_channel_select = shift_channel_view.children[0]
        shift_channel_select.row = 1
        shift_channel_select.placeholder = "Shift Channel~"
        shift_channel_select.min_values = 0

        shift_role_view = RoleSelect(ctx.author.id, limit=5)
        shift_role_select = shift_role_view.children[0]
        shift_role_select.row = 2
        shift_role_select.placeholder = "On-Duty Rowe~"
        shift_channel_select.min_values = 0

        next_menu = NextView(bot, ctx.author.id)
        next_button = next_menu.children[0]
        next_button.disabled = False
        next_button.callback = stop_override
        next_button.row = 4

        for item in [
            shift_enabled_select,
            shift_role_select,
            shift_channel_select,
            next_button,
        ]:
            shift_management_settings.add_item(item)

        await msg.edit(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('shift')} Shift Management",
                description=(
                    "**What is Shift Management?** Da Shift Management moduwe awwows fow staff membews to log how much time they wewe in-game, ow modewating, ow on as a staff membew. It awwows fow a compwehensive guide of who is da most active in ur staff team.\n\n"
                    "**Enabled:** When enabled, staff membews wiww be abwe to run `/duty` commands to manage theiw shift, see how much time they hab, as weww as see how much time odew peopwe hab. Management membews wiww be abwe to administwate peopwe's shifts, add time, remove time, and cleaw peopwe's shifts.\n\n"
                    "**Shift Channel:** Dis is whewe aww shift logs wiww go to. Dis channel wiww be used fow aww modifications to shifts, any pewson dat may be stawting ow ending theiw shift.\n\n"
                    "**On-Duty Rowe:** When someone is on shift, they wiww be given dis rowe. When da staff membew goes off shift, dis rowe wiww be removed fwom them."
                ),
                color=blank_color,
            ),
            view=shift_management_settings,
        )
        set_active_view_state(shift_management_settings)
        await shift_management_settings.wait()

        for item in shift_management_settings.children:
            if (
                isinstance(item, discord.ui.Select)
                or isinstance(item, discord.ui.RoleSelect)
                or isinstance(item, discord.ui.ChannelSelect)
            ):
                if len(item.values) > 0:
                    if item.placeholder == "Shift Management~":
                        modifications["shift_management"]["enabled"] = bool(
                            item.values[0] == "enabled"
                        )
                    elif item.placeholder == "Shift Channel~":
                        modifications["shift_management"]["channel"] = item.values[0].id
                    elif item.placeholder == "On-Duty Rowe~":
                        modifications["shift_management"]["role"] = [
                            role.id for role in item.values
                        ]

        new_configuration = copy(base_configuration)
        new_configuration.update(modifications)
        new_configuration["_id"] = ctx.guild.id
        await bot.settings.upsert(new_configuration)
        await msg.edit(
            embed=discord.Embed(
                title=f'{self.bot.emoji_controller.get_emoji("success")} Success!',
                description="U awe now setup wid ERM, and hab finished da Setup Wizawd! U shouwd now be abwe to use ERM in ur staff team. If u'd like to change any of these settings, use `/config`!\n\n**ERM has lots mowe moduwes than what's mentioned hewe! U can enabwe them by going into `/config`!**",
                color=0x1FD373,
            ),
            view=None,
        )

    @commands.guild_only()
    @commands.hybrid_command(
        name="config",
        description="View ur ERM settings~",
        aliases=["settings"],
        extras={"category": "Configuwation~"},
    )
    @require_settings()
    @is_management()
    async def _config(self, ctx: commands.Context):
        bot = self.bot
        settings = await bot.settings.find_by_id(ctx.guild.id)

        await log_command_usage(self.bot, ctx.guild, ctx.author, f"Config")

        basic_settings_view = BasicConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "Staff Rowes >w<",
                    [
                        discord.utils.get(ctx.guild.roles, id=role)
                        for role in settings["staff_management"].get("role") or [0]
                    ],
                ),
                (
                    "Admin Rowe >w<",
                    [
                        discord.utils.get(ctx.guild.roles, id=role)
                        for role in settings["staff_management"].get("admin_role")
                        or [0]
                    ],
                ),
                (
                    "Management Rowes >w<",
                    [
                        discord.utils.get(ctx.guild.roles, id=role)
                        for role in settings["staff_management"].get(
                            "management_role", []
                        )
                        or [0]
                    ],
                ),
                (
                    "Pwefix~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            settings["customisation"].get("prefix")
                            if settings["customisation"].get("prefix")
                            in ["!", ">", "?", ":", "-"]
                            else None
                        ),
                    ],
                ),
            ],
        )

        loa_config = settings["staff_management"].get("loa_role")
        if isinstance(loa_config, list):
            loa_roles = [discord.utils.get(ctx.guild.roles, id=i) for i in loa_config]
        elif isinstance(loa_config, int):
            loa_roles = [discord.utils.get(ctx.guild.roles, id=loa_config)]
        else:
            loa_roles = [0]

        loa_configuration_view = LOAConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "LOA Requests uwu~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings["staff_management"].get("enabled") is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
                ("LOA Rowe uwu~", loa_roles),
                (
                    "LOA Channel uwu~",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (channel := settings["staff_management"].get("channel"))
                            else 0
                        )
                    ],
                ),
            ],
        )

        shift_management_view = ShiftConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "On-Duty Rowe~",
                    [
                        discord.utils.get(ctx.guild.roles, id=role)
                        for role in (settings["shift_management"].get("role") or [0])
                    ],
                ),
                (
                    "Shift Channel~",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (channel := settings["shift_management"].get("channel"))
                            else 0
                        )
                    ],
                ),
                (
                    "Shift Management~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings["shift_management"].get("enabled") is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
            ],
        )

        ra_config = settings["staff_management"].get("ra_role")
        if isinstance(ra_config, list):
            ra_roles = [discord.utils.get(ctx.guild.roles, id=i) for i in ra_config]
        elif isinstance(ra_config, int):
            ra_roles = [discord.utils.get(ctx.guild.roles, id=ra_config)]
        else:
            ra_roles = [0]

        ra_view = RAConfiguration(bot, ctx.author.id, [("RA Rowe uwu~", ra_roles)])

        roblox_punishments = PunishmentsConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "Punishments Channel owo~",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (channel := settings["punishments"].get("channel"))
                            else 0
                        )
                    ],
                ),
                (
                    "ROBLOX Punishments uwu~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings["punishments"].get("enabled") is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
            ],
        )

        security_view = GameSecurityConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "Game Secuwity owo~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings.get("game_security", {}).get("enabled") is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
                (
                    "Alewt Channel uwu~",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (
                                channel := settings.get("game_security", {}).get(
                                    "channel"
                                )
                            )
                            else 0
                        )
                    ],
                ),
                (
                    "Webhook Channel owo~",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (
                                channel := settings.get("game_security", {}).get(
                                    "webhook_channel"
                                )
                            )
                            else 0
                        )
                    ],
                ),
                (
                    "Mentionables >w<",
                    [
                        discord.utils.get(ctx.guild.roles, id=role)
                        for role in (
                            settings.get("game_security", {}).get("role") or [0]
                        )
                    ],
                ),
            ],
        )

        logging_view = GameLoggingConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "Message Logging~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings.get("game_logging", {})
                            .get("message", {})
                            .get("enabled", None)
                            is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
                (
                    "STS Logging >w<",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings.get("game_logging", {})
                            .get("sts", {})
                            .get("enabled", None)
                            is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
                (
                    "Pwiowity Logging owo~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings.get("game_logging", {})
                            .get("priority", {})
                            .get("enabled", None)
                            is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
            ],
        )

        antiping_view = AntipingConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "Anti-Ping uwu~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings.get("antiping", {}).get("enabled", None) is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
                (
                    "Use Hiewawchy~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if settings.get("antiping", {}).get("use_hierarchy", None)
                            is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
                (
                    "Affected Rowes owo~",
                    [
                        discord.utils.get(ctx.guild.roles, id=role)
                        for role in (settings.get("antiping", {}).get("role") or [0])
                    ],
                ),
                (
                    "Bypass Rowes~",
                    [
                        discord.utils.get(ctx.guild.roles, id=role)
                        for role in (
                            settings.get("antiping", {}).get("bypass_role") or [0]
                        )
                    ],
                ),
            ],
        )

        erlc_view = ERLCIntegrationConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "Elevation Requiwed owo~",
                    [
                        ["CUSTOM_CONF~", {"_FIND_BY_LABEL": True}],
                        (
                            "Enabled >w<"
                            if (settings.get("ERLC~", {}) or {}).get(
                                "elevation_required", True
                            )
                            is True
                            else "Disabled owo~"
                        ),
                    ],
                ),
                (
                    "Playew Logs Channel owo~",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (
                                channel := (settings.get("ERLC~", {}) or {}).get(
                                    "player_logs"
                                )
                            )
                            else 0
                        )
                    ],
                ),
                (
                    "Kiww Logs Channel uwu~",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (
                                channel := (settings.get("ERLC~", {}) or {}).get(
                                    "kill_logs"
                                )
                            )
                            else 0
                        )
                    ],
                ),
            ],
        )

        erm_command_log_view = ERMCommandLog(
            bot,
            ctx.author.id,
            [
                (
                    "ERM Log Channel >w<",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (
                                channel := settings.get("staff_management", {}).get(
                                    "erm_log_channel"
                                )
                            )
                            else 0
                        )
                    ],
                )
            ],
        )

        priority_settings = await self.bot.priority_settings.db.find_one(
            {"guild_id": str(ctx.guild.id)}
        )

        priority_requests = PriorityRequestConfiguration(
            bot,
            ctx.author.id,
            [
                (
                    "Blacklisted Rowes uwu~",
                    [
                        discord.utils.get(ctx.guild.roles, id=int(role))
                        for role in (priority_settings or {}).get("blacklisted_roles")
                        or [0]
                    ],
                ),
                (
                    "Mentioned Rowes uwu~",
                    [
                        discord.utils.get(ctx.guild.roles, id=int(role))
                        for role in (priority_settings or {}).get("mentioned_roles")
                        or [0]
                    ],
                ),
                (
                    "Pwiowity Channel~",
                    [
                        (
                            discord.utils.get(ctx.guild.channels, id=channel)
                            if (
                                channel := ((priority_settings or {}).get("channel_id"))
                            )
                            else 0
                        )
                    ],
                ),
            ],
        )

        maple_county_configuration = MapleCountyConfiguration(
            bot,
            ctx.author.id,
            settings.get("MC owo~", {})
        )

        pages = []

        for index, view in enumerate(
            [
                basic_settings_view,
                loa_configuration_view,
                shift_management_view,
                ra_view,
                roblox_punishments,
                security_view,
                logging_view,
                antiping_view,
                erlc_view,
                erm_command_log_view,
                priority_requests,
                maple_county_configuration,
            ]
        ):
            corresponding_embeds = [
                discord.Embed(
                    title="Basic Settings >w<",
                    description=(
                        "**Staff Rowe:** A staff rowe is da rowe dat is going to be abwe to use most ERM commands. U'd assign dis rowe to da peopwe u want to be abwe to use ERM's cowe functionawities.\n\n"
                        "**Admin Rowe:** An admin rowe is da rowe dat can manage LOAs, RAs & odew peoples' shifts but it can nyot use sewvew manage and config.\n\n"
                        "**Management Rowe:** A management rowe is da rowes of ur sewvew management membews. These peopwe wiww be abwe to dewete punishments, modify peopwe's shift time, and accept LOA Requests.\n\n"
                        "**Pwefix:** Dis wiww be a pwefix u awe abwe to use instead of ouw slash command system. U can use dis pwefix to execute commands slightwy fastew and to take advantage of some extwa featuwes."
                    ),
                    color=blank_color,
                ),
                discord.Embed(
                    title="LOA Requests uwu~",
                    description=(
                        "**Enabled:** Dis setting enables ow disables da LOA Requests moduwe. When enabled, dis awwows ur staff membews to fiww out Leave of Absence requests fow ur management membews to appwove.\n\n"
                        "**LOA Rowe:** Dis rowe is given to those who awe on Leave of Absence, and is removed when they go off Leave of Absence.\n\n"
                        "**LOA Channel:** Dis channel wiww be whewe Leave of Absence requests wiww be logged, and whewe they wiww be accepted ow denied. Make suwe dis is a channel dat Management membews can see, so dat they can appwove LOA requests."
                    ),
                    color=blank_color,
                ),
                discord.Embed(
                    title="Shift Management~",
                    description=(
                        "**What is Shift Management?** Da Shift Management moduwe awwows fow staff membews to log how much time they wewe in-game, ow modewating, ow on as a staff membew. It awwows fow a compwehensive guide of who is da most active in ur staff team.\n\n"
                        "**Enabled:** When enabled, staff membews wiww be abwe to run `/duty` commands to manage theiw shift, see how much time they hab, as weww as see how much time odew peopwe hab. Management membews wiww be abwe to administwate peopwe's shifts, add time, remove time, and cleaw peopwe's shifts.\n\n"
                        "**Shift Channel:** Dis is whewe aww shift logs wiww go to. Dis channel wiww be used fow aww modifications to shifts, any pewson dat may be stawting ow ending theiw shift.\n\n"
                        "**On-Duty Rowe:** When someone is on shift, they wiww be given dis rowe. When da staff membew goes off shift, dis rowe wiww be removed fwom them."
                    ),
                    color=blank_color,
                ),
                discord.Embed(
                    title="RA Requests uwu~",
                    description=(
                        "**What awe RA Requests?** RA Requests, also cawwed Reduced Activity Requests, awe a fowm of Leave of Absence whewe da staff membew isn't requiwed to complete da fuww quota, but expects dat they wiww be abwe to complete it pawtiawwy.\n\n"
                        "**RA Rowe:** Dis rowe is given to those who awe on Reduced Activity, and is removed when they go off Reduced Activity.\n\n"
                    ),
                    color=blank_color,
                ),
                discord.Embed(
                    title="ROBLOX Punishments uwu~",
                    description=(
                        "**What is da ROBLOX Punishments moduwe?** Da ROBLOX Punishments moduwe awwows fow membews of ur Staff Team to log punishments against a ROBLOX playew using ERM! U can specify custom types of punishments, whewe they wiww go, as weww as manage and seawch individuaw punishments.\n\n"
                        "**Enabled:** Dis setting toggles da ROBLOX Punishments moduwe. When enabled, staff membews wiww be abwe to use `/punish`, and management membews wiww be abwe to additionawwy use `/punishment manage`.\n\n"
                        "**Punishments Channel:** Dis is whewe most punishments made wid da ROBLOX Punishments go. Any logged actions of a ROBLOX playew wiww go to dis channel."
                    ),
                    color=blank_color,
                ),
                discord.Embed(
                    title="Game Secuwity owo~",
                    description=(
                        "**What is da Game Secuwity moduwe?** As of right now, dis moduwe onwy applies to pwivate sewvews of Emewgency Response: Libewty County. Dis moduwe aims to pwotect and secuwe pwivate sewvews by detecting if a staff membew runs a potentiawwy abusive command, and notifying management of dis incident.\n\n"
                        "**Enabled:** Game Secuwity is a moduwe dat aims to pwotect pwivate sewvews fwom abuse of administwative pwiviweges. Dis onwy wowks fow pawticuwaw games and sewvews. U shouwd disabwe dis if u awen't a game listed above.\n\n"
                        "**Webhook Channel:** Dis channel is whewe da bot wiww read da webhooks fwom da game sewvew. Dis is nyot whewe awewts wiww be sent. Radew, dis is whewe da bot wiww detect any admin abuse.\n\n"
                        "**Alewt Channel:** Dis channel is whewe da bot wiww send da cowwesponding awewts fow abuse of administwative pwiviweges in ur pwivate sewvew. It is recommended fow dis nyot to be da same as ur Webhook Channel so dat u don't miss any unwesolved Secuwity Alewts.\n\n"
                        "**Mentionables:** These rowes wiww be mentioned when a secuwity awewt is sent by ERM. Aww of these rowes wiww be mentioned in da message, and they shouwd be abwe to deaw wid da situation at hand fow maximum staff efficiency."
                    ),
                    color=blank_color,
                ),
                discord.Embed(
                    title="Game Logging >w<",
                    color=blank_color,
                    description=(
                        "**What is Game Logging?** Game Logging is an ERM moduwe, pawticuwawwy taiwowed towawds pwivate sewvews of Emewgency Response: Libewty County, but can appwy to odew roweplay games in a simiwaw genwe. Game Logging awwows fow staff membews to log events of intewest, such as custom in-game messages, pwiowity timews, as weww as STS events. Dis awwows fow stweamlined management of staff efficiency.\n\n"
                        "### Message Logging\n\n"
                        "**Enabled:** Dis dictates whedew da in-game message section of da Game Logging moduwe is enabled. Dis pawt of da moduwe automaticawwy and awwows fow manuaw logs of in-game messages and 'hints' so dat management can effectivewy see if staff membews awe sending da cowwect amount of notifications.\n\n"
                        "**Message Logging Channel:** Dis channel wiww be whewe these message and notification logs wiww be sent to.\n\n"
                        "### STS Logging\n\n"
                        "**Enabled:** Dis dictates whedew da Shouldew-to-Shouldew event logging section of da Game Logging moduwe is enabled. When enabled, staff membews can log da duwation of theiw events, as weww as who hosted them and odew impowtant infowmation.\n\n"
                        "**STS Logging Channel:** Dis is whewe da event logs fow Shouldew-to-Shouldew events wiww appeaw. Management membews wiww be abwe to see aww rewevant infowmation of an STS hewe.\n\n"
                        "### Pwiowity Logging\n\n"
                        "**Enabled:** Dis section of da Game Logging moduwe, cowwespondingwy named da Pwiowity Logging pawt, awwows fow staff membews to log Pwiowity Timew events, theiw reason, duwation, as weww as any notabwe infowmation which may be necessawy fow management membews.\n\n"
                        "**Pwiowity Logging Channel:** Dis channel wiww be whewe pwiowity timew events and event notifications wiww be logged accowdingwy fow management membews to view."
                    ),
                ),
                discord.Embed(
                    title="Anti-Ping uwu~",
                    color=blank_color,
                    description=(
                        "**What is Anti-Ping?** Anti-ping is an ERM moduwe which speciawises in pweventing mention abuse of High Ranks widin a Discowd sewvew. ERM detects if an unaudowized individuaw mentions a High Ranking individuaw, and notifies them to discontinue any fuwdew attempts to viowate da sewvew's reguwations.\n\n"
                        "**Enabled:** Dis setting dictates whedew ERM wiww take action upon these usews, and intewvene when necessawy. When disabled, da Anti-Ping moduwe wiww nyot activate.\n\n"
                        "**Affected Rowes:** These rowes clawify da individuals who awe affected by Anti-Ping, and awe classed as impowtant individuals to ERM. An individuaw who pings someone wid these affected rowes, wiww activate Anti-Ping.\n\n"
                        "**Bypass Rowes:** An individuaw who howds one of these rowes wiww nyot be abwe to twiggew Anti-Ping filtews, and wiww be abwe to ping any individuaw widin da Affected Rowes list widout ERM intewvening.\n\n"
                        "**Use Hiewawchy:** Dis setting dictates whedew Anti-Ping wiww take into account rowe hiewawchy fow each of da affected rowes. Fow exampwe, if u set Modewation as an affected rowe, it wouwd also appwy fow aww rowes above Modewation, such as Administwation ow Management."
                    ),
                ),
                discord.Embed(
                    title="ER:LC Integwation owo~",
                    color=blank_color,
                    description=(
                        "**What is da ER:LC Integwation?** ER:LC Integwation awwows fow ERM to communicate wid da Powice Roweplay Community APIs, and ur Emewgency Response: Libewty County sewvew. In pawticuwaw, these configuwations awwow fow Join Logs, Leave Logs, and Kiww Logs to be logged.\n\n"
                        "**Elevation Requiwed:** Dis setting dictates whedew ewevated pewmissions awe requiwed to run commands such as `:admin` and `:unadmin`. In such case whewe dis is enabled, Co-Ownew pewmissions awe requiwed to run these commands to pwevent secuwity risk. If disabled, those wid da Management Rowes in ur sewvew can run these commands. **It is advised u keep dis enabled unless u hab a vawid reason to tuwn it off.** Contact ERM Suppowt if u awe unsuwe what dis setting does.\n\n"
                        "**Playew Logs Channel:** Dis channel is whewe Playew Join and Leave logs wiww be sent by ERM. ERM wiww check ur sewvew evewy 45 seconds to see if new membews hab joined ow left, and repowt of theiw time accowdingwy.\n\n"
                        "**Kiww Logs Channel:** Dis setting is whewe Kiww Logs wiww be sent by ERM. ERM wiww check ur sewvew evewy 45 seconds and constantwy contact ur ER:LC pwivate sewvew to know if thewe awe any new kiww logs. If thewe awe, to log them in da cowwesponding channel."
                    ),
                ),
                discord.Embed(
                    title="ERM Logging >w<",
                    color=blank_color,
                    description=(
                        "**ERM Log Channel:** Dis channel is whewe ERM wiww log aww administwative commands and configuwation changes made by Admin & Management Rowes. Dis is useful fow auditing puwposes, ensuwing twanspawency, and detecting any potentiaw abuse of administwative pwiviweges. Dis is a cwiticaw pawt of ERM and shouwd be enabled fow aww sewvews using ERM.\n\n"
                        "Aww commands such as Duty Admin, LOA Admin, RA Admin, Sewvew Manage, Config, etc., as weww as neawwy aww configuwation changes, wiww be logged in dis channel."
                    ),
                ),
                discord.Embed(
                    title="Pwiowity Requests~",
                    color=blank_color,
                    description=(
                        "**Blacklisted Rowes:** These awe da rowes which awe unabwe to use da ERM Pwiowity Request system. They wiww nyot be abwe to submit pwiowity requests if they hab any of these rowes.\n\n"
                        "**Mentioned Rowes:** When a pwiowity request is submitted, these rowes wiww be mentioned in da accompanying message advising staff in regawds to da pwiowity request.\n\n"
                        "**Pwiowity Channel:** Dis channel wiww be whewe pwiowity requests awe submitted, and whewe da message advising staff in regawds to da pwiowity request wiww be sent."
                    ),
                ),
                discord.Embed(
                    title="Mapwe County Integwation owo~",
                    color=blank_color,
                    description=(
                        "**What is da Mapwe County Integwation?**\nDa Mapwe County Integwation awwows fow ERM to communicate wid da Mapwe County APIs, and ur Mapwe County sewvew. In pawticuwaw, these configuwations awwow fow configuwation of vawious Mapwe County-specific suppowted featuwes and settings.\n\n"
                    )
                )
            ]
            embed = corresponding_embeds[index]
            page = CustomPage()
            page.embeds = [embed]
            page.identifier = embed.title
            page.view = view

            pages.append(page)

        paginator = SelectPagination(self.bot, ctx.author.id, pages)
        try:
            await ctx.send(embeds=pages[0].embeds, view=paginator.get_current_view())
        except discord.HTTPException:
            await ctx.send(
                embed=discord.Embed(
                    title="Cwiticaw Ewwow >w<",
                    description="Configuwation ewwow; 827 owo~",
                    color=BLANK_COLOR,
                )
            )

    @commands.hybrid_group(
        name="server",
        description="Dis is a namespace fow commands rewating to da Sewvew Management functionawity",
        extras={"category": "Configuwation~"},
    )
    async def server(self, ctx: commands.Context):
        pass

    @commands.guild_only()
    @server.command(
        name="manage",
        description="Manage ur sewvew's ERM data! >w<",
        extras={"category": "Configuwation~"},
    )
    @is_management()
    @require_settings()
    async def server_management(self, ctx: commands.Context):
        await log_command_usage(self.bot, ctx.guild, ctx.author, f"Server Manage")

        embeds = [
            discord.Embed(
                title="Intwoduction >w<",
                description=(
                    "Dis **Sewvew Management Panel** awwows individuals who hab access to it, to manage ur data regawding ERM on ur sewvew. Dis contains any of da data contained widin da 3 main moduwes, which awe Activity Notices, ROBLOX Punishments, and Shift Logging.\n\n"
                    "Using dis panel, u can cleaw cewtain pawts of data, ow ewase da data of a pawticuwaw moduwe in its entiwety. Fow some moduwes, u can also ewase its data by a pawticuwaw specification - such as removing aww punishments fwom a punishment type.\n\n"
                    "Membews wid **Management** pewmissions can access dis panel, and ewase ur sewvew's data, so ensuwe u onwy give dis access to peopwe who u twust. As wid pawticuwaw pawts of dis panel, some actions awe revewsibwe when contacting ERM Suppowt."
                ),
                color=BLANK_COLOR,
            ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon),
            discord.Embed(
                title="Activity Notices >w<",
                description=(
                    "Activity Notices awwow fow routine and robust staff management and administwation, wid da implementation of Leave of Absence requests and Reduced Activity requests. Staff membews can request fow one of these faciwities, and Management can appwove and deny on a case-by-case basis.\n\n"
                    "Using dis panel, u can pewfowm 3 actions. U can **Ewase Pending Requests** to remove aww ongoing Activity Notice requests. U can also **Ewase LOA Notices** and **Ewase RA Notices** to ewase theiw cowwespondent activity notices. **These wiww nyot automaticawwy remove da LOA ow RA rowes, as these actions onwy ewase these notices fwom ouw database.**"
                ),
                color=BLANK_COLOR,
            ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon),
            discord.Embed(
                title="ROBLOX Punishments uwu~",
                description=(
                    "ROBLOX Punishments awwow fow staff membews to log theiw punishments on da ROBLOX platfowm using ERM. ERM awwows a robust expewience fow a staff membew utiwising dis moduwe, as commands awe easy to leawn and execute, as weww as to effectivewy be implemented into a staff membew's wowkflow.\n\n"
                    "Using dis panel, u can **Ewase Aww Punishments**, as weww as **Ewase Punishments By Type** and **Ewase Punishments By Usewname**."
                ),
                color=BLANK_COLOR,
            ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon),
            discord.Embed(
                title="Shift Logging owo~",
                description=(
                    'Shift Logging awwow fow an easy expewience fow staff membews looking to log theiw active shift time using ERM. Staff membews can run simpwe commands to go "on-duty", as weww as go on bweak to signify unavaiwabiwity. Once they awe ready, they can go "off-duty" to signify dat they awe nyo longew avaiwabwe fow any administwative action.\n\n'
                    "Using dis panel, u can **Ewase Aww Shifts**, as weww as utiwise **Ewase Past Shifts** and **Ewase Active Shifts**. U can also **Ewase Shifts By Type**."
                ),
                color=BLANK_COLOR,
            ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon),
        ]
        views = [
            discord.ui.View(),
            ActivityNoticeManagement(self.bot, ctx.author.id),
            PunishmentManagement(self.bot, ctx.author.id),
            ShiftLoggingManagement(self.bot, ctx.author.id),
        ]

        paginator = SelectPagination(
            self.bot,
            ctx.author.id,
            [
                CustomPage(embeds=[embed], identifier=embed.title, view=view)
                for embed, view in zip(embeds, views)
            ],
        )

        await ctx.send(embed=embeds[0], view=paginator.get_current_view())


async def setup(bot):
    await bot.add_cog(Configuration(bot))
