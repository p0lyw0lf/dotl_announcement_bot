from .shell import Shell
from doclite import Database
import json


class HelpCommands(Shell):
    def __init__(self, client):
        super().__init__(client)
        self.helpdb = Database('./help', './help')
        self.commands.update({
            "help":
                {"args": ["user", "channel", "*str"], "func": self.get_help}
        })

    async def get_help(self, user, channel, path=None):
        if path is None:
            path = ["main"]
        path[-1] += '.json'
        data = self.helpdb[tuple(path)]
        if data == '':
            return f"Sorry, help for {' '.join(path)} cannot be found"
        data = json.loads(data)
        to_return = "**" + data["title"] + "**\n\n" + data["content"]

        if channel.is_private:
            return to_return
        else:
            await self.client.send_message(user, to_return)
            return "A PM has been sent to you with help"
