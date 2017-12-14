from .variablecommands import VariableCommands

class MiscCommands(VariableCommands):
    def __init__(self, client, *args, **kwargs):
        super().__init__(client, *args, **kwargs)
        self.commands.update({
            "get_channel":
                {"args": ["message", "channel"], "func": self.get_channel},
            "get_roles":
                {"args": ["server", "user"], "func": self.get_roles},
            "filter_word":
                {"args": ["str"], "func": self.filter_word},
            "get_server_info":
                {"args": ["server"], "func": self.get_server_info}
        })
