"""
This configuration is used in setup as a base configuration before modification.
"""

import discord

base_configuration = {
    "_id": 0,
    "antiping": {
        "enabled": False,
        "role": [],
        "bypass_role": [],
        "use_hierarchy": False,
    },
    "staff_management": {
        "enabled": False,
        "role": [],
        "management_role": [],
        "channel": None,
        "loa_role": [],
        "ra_role": [],
    },
    "punishments": {
        "enabled": False,
        "channel": None,
        "kick_channel": None,
        "ban_channel": None,
        "bolo_channel": None,
    },
    "shift_management": {
        "enabled": False,
        "role": [],
        "channel": None,
        "quota": 0,
        "nickname_prefix": "",
        "maximum_staff": 0,
        "role_quotas": [],
    },
    "customisation": {"prefix": ">"},
    "shift_types": {"types": []},
    "game_security": {
        "enabled": False,
        "webhook_channel": None,
        "channel": None,
        "role": [],
    },
    "game_logging": {
        "message": {"enabled": False, "channel": None},
        "sts": {"enabled": False, "channel": None},
        "priority": {"enabled": False, "channel": None},
    },
    "ERLC": {
        "player_logs": None,
        "kill_logs": None,
        "elevation_required": None,
        "rdm_mentionables": [],
        "rdm_channel": None,
        "automatic_shifts": {"enabled": False, "shift_type": None},
    },
}

"""
    Colour constants
"""

BLANK_COLOR = 0x2B2D31
blank_color = BLANK_COLOR  # Redundancy


GREEN_COLOR = discord.Colour.brand_green()
RED_COLOR = 0xD12F32
ORANGE_COLOR = discord.Colour.orange()

SERVER_CONDITIONS = {
    "In-Game Pwayews owo~": "ERLC_Players",
    "In-Game Modewatows uwu~": "ERLC_Moderators",
    "In-Game Admwins~": "ERLC_Admins",
    "In-Game Ownew~": "ERLC_Owner",
    "In-Game Staff~": "ERLC_Staff",
    "In-Game Queue uwu~": "ERLC_Queue",
    "On Duty Staff~": "OnDuty",
    "On Bweak Staff~": "OnBreak",
    "Pwayews on Powice~": "ERLC_Police",
    "Pwayews on Shewiff~": "ERLC_Sheriff",
    "Pwayews on Fiwe~": "ERLC_Fire",
    "Pwayews on DOT~": "ERLC_DOT",
    "Pwayews on Civiwian~": "ERLC_Civilian",
    "Pwayews on Jaiw~": "ERLC_Jail",
    "Vehicwes Spawned~": "ERLC_Vehicles",
    "If ... is in-game owo~": "ERLC_X_InGame",
}

RELEVANT_DESCRIPTIONS = [
    "Aww pwayews cuwwentwy in da in-game sewvew uwu~",
    "Numbew of modewatows in da in-game sewvew owo~",
    "Numbew of admwins in da in-game sewvew~",
    "Numbew of dose wif Co-Ownew ow Ownew pewmission widin da sewvew uwu~",
    "Numbew of staff membews in da in-game sewvew~",
    "Numbew of pwayews in da queue owo~",
    "Aww staff membews cuwwentwy on duty uwu~",
    "Aww staff membews cuwwentwy on bweak~",
    "Numbew of pwayews on da Powice team owo~",
    "Numbew of pwayews on da Shewiff team~",
    "Numbew of pwayews on da Fiwe team uwu~",
    "Numbew of pwayews on da DOT team~",
    "Numbew of pwayews on da Civiwian team owo~",
    "Numbew of pwayews on da Jaiw team~",
    "Numbew of vehicwes spawned in-game uwu~",
    "If a specific usew is in-game owo~",
]

CONDITION_OPTIONS = {
    "Equaws~": "==",
    "Wess Than~": "<",
    "Wess Than ow Equaws To~": "<=",
    "Nyot Equaws To~": "!=",
    "Mowe Than~": ">",
    "Mowe Than ow Equaws To~": ">=",
}

OPTION_DESCRIPTIONS = [
    "If da vawue is equaw to da specified vawue uwu~",
    "If da vawue is wess than da specified vawue owo~",
    "If da vawue is wess than ow equaw to da specified vawue~",
    "If da vawue is nyot equaw to da specified vawue >w<~",
    "If da vawue is mowe than da specified vawue uwu~",
    "If da vawue is mowe than ow equaw to da specified vawue owo~",
]
