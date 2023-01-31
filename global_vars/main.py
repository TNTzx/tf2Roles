"""Contains the globals used across the program."""


from __future__ import annotations


import disnake
from disnake.ext import commands



class NoGlobalsError(Exception):
    """The exception raised when the globals aren't initialized yet."""
    def __init__(self):
        super().__init__("The global variables aren't initialized yet.")


class Globals():
    """Class that constructs the global object responsible for storing all global variables."""
    _main_instance: Globals | None = None

    def __init__(self):
        self.intents = disnake.Intents.default()
        self.intents.guilds = True
        self.intents.presences = True
        self.intents.members = True

        self.masterRoles = [
            (298698700719521795, 298698201270059009),  # Rhythm Maestro -> Sushi Maestro
            (409552655623389185, 409551428814635008),  # Rhythm Master -> Sushi Master
            (966299552112062494, 409551428814635008),  # Rhythm Completionist -> Sushi Master
            (819428632447287296, 973061504180035644),  # Café Champion -> Café Addict
            (973061504180035644, 517143533853868074),  # Café Addict -> Café Regular
            (517143533853868074, 517143450391543818),  # Cafe Regular -> Cafe Visitor
            (538496816845553704, 966298129362202624),  # Fiery Aficionado -> Fiery Adept
            (966298455205097542, 538496816845553704),  # Lantern Voyager -> Fiery Aficionado
            (966298455205097542, 966298334757257216),  # Lantern Voyager -> Fiery Virtuoso
            (966298455205097542, 973065025709277214),  # Lantern Voyager -> Galactic Nobility
            (966298455205097542, 973064417493266452),  # Lantern Voyager -> Universal Royalty
            (973066531082764298, 973066015447613460),  # Prompt Pioneer -> Prompt Participator
            (973066015447613460, 973063466678112286),  # Prompt Participator -> Prompt Peruser
            (983061892002086994, 983060833141674014),  # Stellar Sovereign -> Orbital Overseer
            (983062281699098624, 983060833141674014),  # Neo Overlord -> Orbital Overseer
            (983062659882680401, 983060833141674014),  # Cosmos Conqueror -> Orbital Overseer
            (983062659882680401, 983061892002086994),  # Cosmos Conqueror -> Stellar Sovereign
            (331630636299452446, 978000113786028164)   # Winner -> Compo Finalist
        ]

        self.default_role = 831865797545951232

        self.activity = disnake.Game(name="ADOFAI: Neo Cosmos DLC Available Now!")

        self.bot = commands.InteractionBot(
            intents = self.intents,
            allowed_mentions = disnake.AllowedMentions(
                everyone = False,
                users = True,
                roles = False,
                replied_user = True
            ),
            activity = self.activity
        )

        # self.guilds = [770428394918641694, 296802696243970049]


        type(self)._main_instance = self


    @classmethod
    def get_globals(cls):
        """Gets the object that stores all global variables."""
        if cls._main_instance is None:
            raise NoGlobalsError()
        return cls._main_instance


    def get_guild_ids(self):
        """Gets all guilds joined by the bot."""
        return [guild.id for guild in self.bot.guilds]
