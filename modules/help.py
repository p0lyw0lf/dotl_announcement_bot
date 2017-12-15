from .shell import Shell
from doclite import Database
import json


class HelpCommands(Shell):
    def __init__(self, client, *args, **kwargs):
        super(HelpCommands, self).__init__(client, *args, **kwargs)
        self.helpdb = Database('help', 'help')
        self.commands.update({
            "help":
                {"args": ["user", "channel", "*str"], "func": self.get_help}
        })

    async def get_help(self, user, channel, path=None):
        if path is None:
            path = ["main"]
        path[-1] += '.txt'
        data = self.helpdb[tuple(path)]
        if data == '':
            return f"Sorry, help for {' '.join(path)} cannot be found"

        if channel.is_private:
            return data
        else:
            await self.client.send_message(user, data)
            return "A PM has been sent to you with help"
