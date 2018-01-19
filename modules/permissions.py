from doclite import InMemDatabase
from .shell import Shell

import discord

class Permissions(Shell):
    def __init__(self, client, *args, **kwargs):
        super().__init__(client, *args, **kwargs)
        self.permdb = InMemDatabase('perms', 'default')
        self.databases.append(self.permdb)
        self.commands.update({
            "restrict_command":
                {"args": ["server", "str", "yes?"], "func": self.restrict_command},
            "admin_role":
                {"args": ["server", "int"], "func": self.set_admin_role},
        })

    async def restrict_command(self, server, command=None, restrict=True):
        if command is None: return "You need to specify a command."
        if command not in self.commands:
            return "`{}` is not a valid command".format(command)

        if server is not None:
            if restrict:
                self.permdb[server.id, 'restricted', command.lower()] = 'yes'
                return "Restricted use of `{}` to admins only.".format(command)
            else:
                self.permdb[server.id, 'restricted', command.lower()] = 'no'
                return "Allowed use of `{}` for everyone.".format(command)
        else:
            return "It dosen't make sense to restrict commands in PMs!"

        

    async def set_admin_role(self, server, admin_role_id=None):
        if admin_role_id is None: return "You need to specify a role id."

        self.permdb[server.id, 'admin_role'] = str(admin_role_id)

        return "Set role {} as the admin role".format(admin_role_id)

    def can_run_command(self, user, server, command):
        if server is None: return True
        admin_role_id = self.permdb[server.id, 'admin_role']
        # Are we not in a place with admin restrictions?
        if not admin_role_id or \
           not isinstance(user, discord.Member): return True
        # Is the user an admin?
        if admin_role_id in {role.id for role in user.roles}: return True
        # If the command restricted?
        if not self.is_no(self.permdb[server.id, 'restricted', command.lower()]):
            return False
        return True
