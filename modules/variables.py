from doclite import Database
from .shell import Shell


class VariableCommands(Shell):
    def __init__(self, client, *args, **kwargs):
        super().__init__(client, *args, **kwargs)
        self.db = Database('db', 'global')
        self.commands.update({
            "set":
                {"args": ["user", "*str", "str"], "func": self.set_user_data},
            "get":
                {"args": ["user", "*str"], "func": self.get_user_data}
        })
                         

    async def set_user_data(self, user, variable, value):
        print(variable, value)
        if variable[0] == self.db.global_keyword:
            if user.id in self.admins:
                self.db[tuple(variable)] = value
            else:
                return "You can't set globals!"
        else:
            self.db[tuple([user.id] + variable)] = value
        return f"{variable} set to {value}"

    async def get_user_data(self, user, variable):
        print(variable)
        if variable[0] == self.db.global_keyword:
            value = self.db[tuple(variable)]
        else:
            value = self.db[tuple([user.id] + variable)]

        if not value:
            value = 'None'

        return f"{' '.join(variable)} is currently set to {value}"
