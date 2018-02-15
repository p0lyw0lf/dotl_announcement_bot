from .variables import VariableCommands
from utils import ent2list, list2ent

from urllib.parse import urlparse
from random import randint
import logging as log
import discord

class MemeCommands(VariableCommands):
    def __init__(self, client, *args, **kwargs):
        super(MemeCommands, self).__init__(client, *args, **kwargs)
        self.commands.update({
            "register_meme":
                {"args": ["server", "str"], "func": self.register_meme},
            "add_to":
                {"args": ["server", "str", "str"], "func": self.add_to_meme},
            "show_memes":
                {"args": ["server"], "func": self.show_all_memes},
            "show_from":
                {"args": ["server", "str"], "func": self.show_all_from_meme},
            "delete_meme":
                {"args": ["server", "str"], "func": self.delete_meme},
            "delete_from":
                {"args": ["server", "str", "int"], "func": self.delete_from_meme},
        })
        
    async def register_all_memes(self):
        for server in self.client.servers:
            all_memes = ent2list(self.db["memes_of", server.id])
            for meme in all_memes:
                await self.register_meme(server, meme, do_update_db=False)
        
    async def register_meme(self, server, meme=None, do_update_db=True):
        if meme is None or not meme:
            return "Lol u forgot 2 giv me a meme"
            
        if meme in self.commands:
            return "I already know how to \"{}\"!".format(meme)
            
        self.commands.update({
            meme:
                {"args": ["server", "int"], "func": self.show_meme(meme)},
        })
        
        if do_update_db:
            all_memes = ent2list(self.db["memes_of", server.id], exclude={meme})
            all_memes.append(meme)
            self.db["memes_of", server.id] = list2ent(all_memes)
            
        return "Haha yes now I can \"{}\" with all my fellow memesters".format(meme)
        
        
    def show_meme(self, meme):
    
        async def inner_meme(server, index=None):
        
            all_memes = ent2list(self.db["memes_of", server.id])
            if meme not in all_memes:
                return "\"{}\" is not a meme on this server".format(meme)
            
            all_links = ent2list(self.db["memes_in", server.id, meme])
            if len(all_links) == 0:
                return "I don't have any images for \"{}\"".format(meme)
                
            if index is None:
                index = randint(0, len(all_links)-1)
                
            embed = discord.Embed()
            embed.color = 0x0da000
            embed.set_image(url=all_links[index])
            
            return embed
            
        return inner_meme
        
    def validate_url(self, url):
        try:
            result = urlparse(url)
            return bool(result.scheme.startswith('http') and result.netloc and result.path)
        except:
            return False
    
    async def add_to_meme(self, server, meme=None, link=None):
        if meme is None or not meme:
            return "Lol u forgot 2 giv me a meme"
        
        if meme not in self.commands:
            return "I don't know how to do a \"{}\"".format(meme)
            
        if link is None or not link:
            return "There's a meme but no link???"
            
        if not self.validate_url(link):
            return "I don't think that's a valid link..."
            
        all_links = ent2list(self.db["memes_in", server.id, meme], exclude={link})
        all_links.append(link)
        self.db["memes_in", server.id, meme] = list2ent(all_links)
        
        return "Wow that's a cool \"{}\" meme".format(meme)
        
    async def show_all_memes(self, server):
        all_memes = ent2list(self.db["memes_of", server.id])
        
        if all_memes:
            meme_dict = dict()
            for meme in all_memes:
                meme_dict[meme] = "{} images".format(len(ent2list(self.db["memes_in", server.id, meme])))
            return meme_dict
            
        else:
            return "I don't know any memes! :("
    
    async def show_all_from_meme(self, server, meme=None):
        if meme is None or not meme:
            return "Lol u forgot 2 giv me a meme"
        
        if meme not in self.commands:
            return "I don't know how to do a \"{}\"".format(meme)
    
        all_links = ent2list(self.db["memes_in", server.id, meme])
        
        if all_links:
            link_dict = dict()
            for x in range(len(all_links)):
                link_dict[x+1] = all_links[x]
            return link_dict
        else:
            return "I know what \"{}\" is, but I don't have any links for it".format(meme)
        
    async def delete_meme(self, server, meme=None):
        if meme is None or not meme:
            return "Lol u forgot 2 giv me a meme"
        
        if meme not in self.commands:
            return "I don't know how to do a \"{}\"".format(meme)
            
        all_memes = ent2list(self.db["memes_of", server.id])
        
        if meme not in all_memes:
            return "\"{}\" is not a meme on this server".format(meme)
            
        del self.commands[meme]
        all_memes.remove(meme)
        self.db["memes_of", server.id] = list2ent(all_memes)
        self.db["memes_in", server.id, meme] = ""
        del self.db["memes_in", server.id, meme]
        
        return "I did do a delete of \"{}\"".format(meme)
    
    async def delete_from_meme(self, server, meme=None, index=None):
        if meme is None or not meme:
            return "Lol u forgot 2 giv me a meme"
        
        if meme not in self.commands:
            return "I don't know how to do a \"{}\"".format(meme)
            
        all_memes = ent2list(self.db["memes_of", server.id])
        
        if meme not in all_memes:
            return "\"{}\" is not a meme on this server".format(meme)
            
        if index is None:
            return "I need to know which link to remove"
            
        all_links = ent2list(self.db["memes_in", server.id, meme])
        
        if index > len(all_links):
            return "I only have {} links for that meme!".format(len(all_links))
            
        all_links = [all_links[x] for x in range(len(all_links)) if x+1 != index]
        self.db["memes_in", server.id, meme] = list2ent(all_links)
        
        return "Link {} removed from \"{}\" list!".format(index, meme)