from .shell import Shell
from doclite import InMemDatabase
from discord import ChannelType


class HelpCommands(Shell):
    def __init__(self, client, *args, **kwargs):
        super(HelpCommands, self).__init__(client, *args, **kwargs)
        self.helpdb = InMemDatabase('help', 'help')
        self.databases.append(self.helpdb)
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
            return "Sorry, help for {} cannot be found".format(' '.join(path))

        if channel.type == ChannelType.private:
            return data
        else:
            await user.send(data)
            return "A PM has been sent to you with help"
