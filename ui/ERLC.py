from discord.ext import commands
from utils.constants import blank_color
from utils.utils import config_change_log
import discord

class callSignCheck(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, settings: dict = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.settings = settings or {}

        self.enabled_select = discord.ui.Select(
            placeholder="Sewect an option uwu~",
            options=[
                discord.SelectOption(label="Enabwed", value="enabled"),
                discord.SelectOption(label="Disabwed", value="disabled"),
            ]
        )
        self.enabled_select.callback = self.enabled_callback
        self.add_item(self.enabled_select)

        self.add_whitelist_button = discord.ui.Button(
            label="Add Whitewist uwu~",
            style=discord.ButtonStyle.green,
            custom_id="add_whitelist"
        )
        self.add_whitelist_button.callback = self.add_whitelist_callback
        self.add_item(self.add_whitelist_button)

        self.delete_whitelist_button = discord.ui.Button(
            label="Dewete Whitewist >w<~",
            style=discord.ButtonStyle.red,
            custom_id="delete_whitelist"
        )
        self.delete_whitelist_button.callback = self.delete_whitelist_callback
        self.add_item(self.delete_whitelist_button)

    async def enabled_callback(self, interaction: discord.Interaction):
        selected_value = self.enabled_select.values[0]
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            sett = {}
        
        sett['ERLC']['callsign_check'] = {
            'enabled': selected_value == 'enabled'
        }
        await self.bot.settings.update_by_id(sett)

        embed = discord.Embed(
            title="Caww Sign Check Status Updated uwu~",
            description=f"Caww Sign Check is now **{selected_value.capitalize()}** hehe~",
            color=blank_color
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def add_whitelist_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Dis is an add whitewist UI uwu~",
            description="DUMMY",
            color=blank_color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def delete_whitelist_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Dis is a dewete whitewist UI >w<~",
            description="DUMMY",
            color=blank_color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)