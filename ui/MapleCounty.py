from discord import Interaction
from discord.ext import commands
from utils.constants import blank_color
from utils.mc_api import ServerKey
from utils.utils import config_change_log
import discord

class CustomModal(discord.ui.Modal, title="Edit Weason uwu~"):
    def __init__(self, title, options, epher_args: dict = None):
        super().__init__(title=title)
        if epher_args is None:
            epher_args = {}
        self.saved_items = {}
        self.epher_args = epher_args
        self.interaction = None

        for name, option in options:
            self.add_item(option)
            self.saved_items[name] = option

    async def on_submit(self, interaction: discord.Interaction):
        for key, item in self.saved_items.items():
            setattr(self, key, item)
        self.interaction = interaction
        await interaction.response.defer(**self.epher_args)
        self.stop()

class MapleCountyConfiguration(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, settings: dict = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.settings = settings or {}

    @discord.ui.button(label="Automatic Discowd Checks uwu~", style=discord.ButtonStyle.secondary)
    async def automatic_discord_checks(self, interaction: Interaction, button: discord.ui.Button):
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            sett = {"_id": interaction.guild.id}
        
        view = MCDiscordCheckConfig(self.bot, interaction.user.id, sett)
        
        discord_checks = sett.get('MC', {}).get('discord_checks', {})
        enabled = discord_checks.get('enabled', False)
        channel_id = discord_checks.get('channel_id')
        
        embed = discord.Embed(
            title="Automatic Discowd Checks uwu~",
            description=(
                "> Dis moduwe awwows fow automatic checks on Discowd accounts of pwayews in ur Mapwe County sewvew owo~"
            ),
            color=blank_color,
        ).add_field(
            name="Awewt Channew~",
            value=f"> Pwayews dat awen't in da Discowd sewvew wiww be sent in dis channew uwu~",
            inline=False,
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True,
        )

class MCDiscordCheckConfig(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, settings: dict = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.settings = settings or {}
        
        # Add the select dropdown and channel select
        self.add_item(self.create_select())
        self.add_item(self.create_channel_select())
    
    def create_select(self):
        select = discord.ui.Select(
            placeholder="Enabwe/Disabwe Discowd Checks uwu~",
            options=[
                discord.SelectOption(
                    label="Enabwe Discowd Checks uwu~",
                    value="enable",
                    default=self.settings.get('MC', {}).get('discord_checks', {}).get('enabled', False)
                ),
                discord.SelectOption(
                    label="Disabwe Discowd Checks >w<~",
                    value="disable",
                    default=not self.settings.get('MC', {}).get('discord_checks', {}).get('enabled', False)
                ),
            ],
            row=0
        )
        select.callback = self.select_callback
        return select
    
    def create_channel_select(self):
        current_channel_id = self.settings.get('MC', {}).get('discord_checks', {}).get('channel_id')
        default_values = [discord.Object(id=current_channel_id)] if current_channel_id else None
        
        channel_select = discord.ui.ChannelSelect(
            placeholder="Sewect Awewt Channew uwu~",
            channel_types=[discord.ChannelType.text],
            max_values=1,
            default_values=default_values,
            row=1
        )
        channel_select.callback = self.channel_select_callback
        return channel_select
    
    async def select_callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "U awe nyot pewmitted to intewact wif dis dwopdown >w<~",
                ephemeral=True
            )
            return
            
        if interaction.data['values']:
            selected_value = interaction.data['values'][0]

            sett = await self.bot.settings.find_by_id(interaction.guild.id)
            if not sett:
                sett = {"_id": interaction.guild.id}

            if "MC" not in sett:
                sett["MC"] = {}
            if "discord_checks" not in sett["MC"]:
                sett["MC"]["discord_checks"] = {"enabled": False}
            
            if selected_value == "enable":
                sett["MC"]["discord_checks"]["enabled"] = True
                status = "enabled"
            elif selected_value == "disable":
                sett["MC"]["discord_checks"]["enabled"] = False
                status = "disabled"
            
            await self.bot.settings.upsert(sett)
            
            await config_change_log(
                self.bot, 
                interaction.guild, 
                interaction.user, 
                f"MC Discowd Checks hav been {status} uwu~"
            )
            
            await interaction.response.send_message(
                f"Discowd Checks hav been {status} uwu~",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message("Nyo option sewected >w<~", ephemeral=True)

    async def channel_select_callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "U awe nyot pewmitted to intewact wif dis dwopdown >w<~",
                ephemeral=True
            )
            return

        channel_select = None
        for component in self.children:
            if isinstance(component, discord.ui.ChannelSelect):
                channel_select = component
                break
        
        channel_id = channel_select.values[0].id if channel_select and channel_select.values else None

        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            sett = {"_id": interaction.guild.id}

        if "MC" not in sett:
            sett["MC"] = {}
        if "discord_checks" not in sett["MC"]:
            sett["MC"]["discord_checks"] = {"enabled": False}

        sett["MC"]["discord_checks"]["channel_id"] = channel_id

        await self.bot.settings.upsert(sett)

        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"MC Discowd Checks awewt channew set to <#{channel_id}> uwu~"
        )

        await interaction.response.send_message(
            f"Awewt channew set to <#{channel_id}> uwu~",
            ephemeral=True
        )