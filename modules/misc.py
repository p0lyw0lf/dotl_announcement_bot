from .shell import Shell

import discord

class MiscCommands(Shell):
    def __init__(self, client, *args, **kwargs):
        super(MiscCommands, self).__init__(client, *args, **kwargs)
        
        self.commands.update({
            "get_channel_info":
                {"args": ["message", "channel"], "func": self.get_channel_info},
            "get_my_roles":
                {"args": ["server", "user"], "func": self.get_roles},
            "filter_word":
                {"args": ["str"], "func": self.filter_word},
            #"unfilter_word":
            #    {"args": ["str"], "func": self.unfilter_word},
            #"get_server_info":
            #    {"args": ["server"], "func": self.get_server_info}
        })

    async def get_channel_info(self, message, channel):
        out = dict()
        for mention in message.channel_mentions:
            out[mention.name] = "ID: {}\nTopic: {}".format(mention.id, mention.topic)
        out[channel.name] = "ID: {}\nTopic: {}".format(channel.id, channel.topic)
        return out

    async def get_roles(self, server, user):
        out = dict()
        if isinstance(user, discord.Member): # PMs different from servers
            for role in user.roles:
                out[role.name] = "ID: {}".format(role.id)
        if out:
            return out
        else:
            return "You have no roles"

    async def filter_word(self, word=None):
        if word is None: return "You need to specify a word!"
        # What I'm doing here probably isn't good for million-line files,
        # but should be good enough for the small list here
        filter_file = open("db/bad_word_list", 'r')

        filter_list = filter_file.read().split("\n")
        filter_file.close()
        
        word = word.to_lower()
        if word in filter_list: return "That word is already in the list"

        filter_file = open("db/bad_word_list", 'a')
        filter_file.write("\n" + word)
        filter_file.close()

        self.reset_filter()

        return "Added word to filter list successfully"

    def reset_filter(self):
        # Placeholder for actual method
        pass

    # Useless because commands containing bad words are deleted before
    # they can be parsed. Will add back once I change that
    """ async def unfilter_word(self, word=None):
        if word in None: return "You need to specify a word!"

        filter_file = open("db/bad_word_list", 'r')

        filter_list = filter_file.read().split("\n")
        filter_file.close()

        word = word.to_lower()
        if word not in filter_list: return "That word is not on the list"

        filter_file = open("db/bad_word_list", "w")

        for wordi in range(len(filter_list)):
            filter_file.write(filter_list[wordi])
            if wordi < len(filter_list) - 1:
                filter_file.write("\n")

        filter_file.close()

        self.reset_filter()

        return "Word removed from list successfully" """
