import datetime
import logging as log
from doclite import JsonDatabase
from .shell import Shell

import discord
from discord import Forbidden, HTTPException


class RoleManager(Shell):
    def __init__(self, client, *args, **kwargs):
        super(RoleManager, self).__init__(client, *args, **kwargs)
        self.warnings = JsonDatabase("db/warnings.json")
        self.databases.append(self.warnings)
        self.commands.update({
            "probation": {
                "args": ["server", "channel", "user", "str"],
                "func": self.probation_user,
            },
            "warn": {
                "args": ["server", "channel", "user", "str"],
                "func": self.warn_user,
            },
            "unwarn": {
                "args": ["server", "channel", "user", "str"],
                "func": self.unwarn_user,
            },
            "warninfo": {
                "args": ["server", "channel", "user", "str"],
                "func": self.warning_info,
            },
        })
        
    async def check_roles(self, serverid, roleid, timelimit, *_, previous_roleid=None):
        curtime = datetime.datetime.utcnow()
        
        server = self.client.get_server(serverid)
        if server.large:
            await self.client.request_offline_members(server)
        role = discord.utils.get(server.roles, id=roleid)
        
        if previous_roleid is None:
            previous_role = server.default_role
        else:
            previous_role = discord.utils.get(server.roles, id=previous_roleid)
            
        for member in server.members:
            # Promote members to the Buds role, but only if they're not on probation
            if member.joined_at + timelimit < curtime and not self.get_warnings(member.id, False)["probation"]:
                if previous_role in member.roles and role not in member.roles:    
                    log.debug(str(member)+": "+str(member.joined_at)+" | "+str(curtime)+" | "+str(member.joined_at+timelimit))
                    try:
                        await self.client.add_roles(member, role)
                        log.info("[SUCCESS] Changing role of "+str(member)+" succeeded")
                    except (Forbidden, HTTPException) as e:
                        log.info("[FAILURE] Changing role of "+str(member)+" failed")

    async def warn_user(self, server, channel, caller, username):
        """
        Warn a user and record that they've been warned.

        :param serverid: the ID of the server the command was used in
        :param caller: (Member) the user who called the command
        :param username: (str) the name of the user to warn
        """
        try:
            member = self.get_server_user(server, username, "You didn't specify a member to warn")
            
            # increment the warning count
            warnings = self.get_warnings(member.id)
            warnings["warnings"] += 1

            # send a PM to the user that they've been warned
            member_pm = ("You have been issued a warning. You have {} warnings. Play nice or else."
                    .format(warnings["warnings"]))
            self.client.send_message(member, member_pm)

            # report back to the caller how many warnings this person has
            response = ("User {} has been warned and now has {} warnings."
                    .format(self.user_format(member), warnings["warnings"]))
            self.send_message_simple(response, channel)

        except Exception as e:
            await self.send_simple_message(str(e), channel)

    async def unwarn_user(self, server, channel, caller, username):
        """
        Decreases the number of warnings a user has received.

        :param serverid: the ID of the server the command was used in
        :param caller: (Member) the user who called the command
        :param username: (str) the name of the user to unwarn
        """
        try:
            member = self.get_server_user(server, username, "You didn't specify a user to unwarn")
            # decrement the warning count
            warnings = self.get_warnings(member.id)
            warnings["warnings"] -= 1

            # report back to the caller how many warnings this person has
            response = "User {} has {} warnings.".format(self.user_format(member), warnings["warnings"])
            await self.send_simple_message(response, channel)

        except Exception as e:
            await self.send_simple_message(str(e), channel)

    async def warning_info(self, server, channel, caller, username):
        """
        Report to the caller how many warnings user "username" has received and if they're on probation.
        If the user is on probation, tell the caller when they were put on probation.

        :param serverid: the ID of the server the command was used in
        :param caller: (Member) the user who called the command
        :param username: (str) the name of the user to unwarn
        """
        try:
            member = self.get_server_user(server, username, "You didn't specify a user to check")
            # Determine how many warnings the user has and if they're on probation
            warnings = self.get_warnings(member.id, False)
            if warnings["warnings"] == 0:
                response = "User {} has no warnings.".format(self.user_format(member))
                await self.send_simple_message(response, channel)

            # report back to the caller how many warnings this person has
            else:
                response = "User {} has {} warnings.".format(self.user_format(member), warnings["warnings"])
                if warnings["probation"]:
                    # Parse the "since" field and convert to a nice, readable time
                    formatted_time = (datetime.datetime.fromisoformat(warnings["since"])
                            .strftime("%I:%M %p on %b %d, %Y"))
                    response += " They have been on probation since {}.".format(formatted_time)
                await self.send_simple_message(response, channel)

        except Exception as e:
            await self.send_simple_message(str(e), channel)

    async def probation_user(self, server, channel, caller, username):
        """
        Put user "username" on probation.
        This removes their "Buds" role and prevents them from posting for 24 hours.

        :param serverid: the ID of the server the command was used in
        :param caller: (Member) the user who called the command
        :param username: (str) the name of the user to unwarn
        """
        try:
            member = self.get_server_user(server, username, "You didn't specify a member to put on probation")

            # Add them to the list of users on probation.
            # Do this BEFORE removing their bud role in case check_roles runs between when
            # we remove their role and when we put them on probation.
            warnings = self.get_warnings(member.id)
            warnings["probation"] = True
            warnings["since"] = datetime.datetime.utcnow().isoformat()

            # Remove the user's "Buds" role.
            budsRole = [r for r in server.roles if r.name == "Buds"]
            await self.client.remove_roles(member, budsRole)

            # Prevent them from posting for 24 hours.
            mutedRole = [r for r in server.roles if r.name == "Muted"]
            await self.client.add_roles(member, mutedRole)

            # Notify the caller that the user has been put on probation
            response = "User {} is now on probation.".format(self.user_format(member))
            await self.send_simple_message(response, channel)

        except Exception as e:
            await self.send_simple_message(str(e), channel)


    def user_format(self, member):
        return "{}#{}".format(member.name, member.discriminator)

    def get_warnings(self, userid, createIfNotExist=True):
        if not self.warnings[userid]:
            # This is the default "warnings" entry
            obj = {
                "warnings": 0,
                "probation": False,
            }
            # Set it in the database if we need to create the entry
            if createIfNotExist:
                self.warnings[userid] = obj
            return obj
        else:
            return self.warnings[userid]

    async def get_server_user(self, server, username, messageIfNone):
        if server is None:
            raise Exception("This command doesn't work in a PM")
        member = server.get_member_named(username)
        if member is None:
            raise Exception(messageIfNone)
        return member
