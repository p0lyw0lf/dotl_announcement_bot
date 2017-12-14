from doclite import Database
from .shell import Shell
import discord

class Permissions(Shell):
    def __init__(self, client, *args, **kwargs):
        super().__init__(client, *args, **kwargs)
        self.permdb = Database('perms', 'perms')
        self.commands.update({
            "restrict_command":
                {"args": ["str", "yes?"], "func": self.restrict_command},
            "set_admin_role":
                {"args": ["server", "int"], "func": self.set_admin_role},
        })

    def can_run_command(self, user, server, command):
        pass
