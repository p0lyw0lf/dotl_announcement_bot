import datetime
import logging as log
from doclite import JsonDatabase
from .shell import Shell
from .permissions import Permissions

import discord
from discord import Forbidden, HTTPException


class RoleManager(Permissions):
    def __init__(self, client, *args, **kwargs):
        super(RoleManager, self).__init__(client, *args, **kwargs)
        self.warnings = JsonDatabase("db/warnings.json")
        self.databases.append(self.warnings)
        self.commands.update({
            "probation": {
                "args": ["server", "mention", "str"],
                "func": self.probation_user,
            },
            "warn": {
                "args": ["server", "mention", "str"],
                "func": self.warn_user,
            },
            "unwarn": {
                "args": ["server", "mention", "str"],
                "func": self.unwarn_user,
            },
            "warninfo": {
                "args": ["server", "user", "mention", "str"],
                "func": self.warning_info,
            },
            
            "member_role": {
                "args": ["server", "int"], 
                "func": self.set_member_role
            },
            "muted_role": {
                "args": ["server", "int"],
                "func": self.set_muted_role
            },
        })
        
        
    async def check_roles(self, serverid, member_timelimit, unmuted_timelimit):
        if self.permdb[serverid, 'member_role'] is None or \
            self.permdb[serverid, 'muted_role'] is None:
            log.warn("You must set the member and role ids on {} before auto-roleing can work!"
                .format(serverid))
            return
        
        curtime = datetime.datetime.utcnow()
        
        server = self.client.get_server(serverid)
        if server.large:
            await self.client.request_offline_members(server)
            
        member_role = discord.utils.get(server.roles, id=self.permdb[serverid, 'member_role'])
        muted_role = discord.utils.get(server.roles, id=self.permdb[serverid, 'muted_role'])
        
        # removing this func for now
        #if previous_roleid is None:
        #    previous_role = server.default_role
        #else:
        #    previous_role = discord.utils.get(server.roles, id=previous_roleid)
        previous_role = server.default_role
        
        for member in server.members:
            # Promote members to the Buds role, but only if they're not on probation
            warnings = self.get_warnings(member.id, False)
            if warnings["probation"]:
                probation_start = datetime.datetime.strptime(warnings["since"], "%Y-%m-%dT%H:%M:%S.%f")
                if probation_start + member_timelimit < curtime:
                    # Probation is up, add them back to Bud status
                    log.warn("removing probation")
                    await self.client.add_roles(member, member_role)
                    del warnings["since"]
                    warnings["probation"] = False
                    log.info(str(member))
                    self.warnings[member.id] = warnings
                
                if probation_start + unmuted_timelimit < curtime:
                    # Unmute them
                    await self.client.remove_roles(member, muted_role)
                
            elif member.joined_at + member_timelimit < curtime:
                if previous_role in member.roles and member_role not in member.roles:    
                    log.debug(str(member)+": "+str(member.joined_at)+" | "+str(curtime)+" | "+str(member.joined_at+member_timelimit))
                    try:
                        await self.client.add_roles(member, member_role)
                        log.info("[SUCCESS] Changing role of "+str(member)+" succeeded")
                    except (Forbidden, HTTPException) as e:
                        log.info("[FAILURE] Changing role of "+str(member)+" failed")

    async def warn_user(self, server, userid=None, username=None):
        """
        Warn a user and record that they've been warned.

        :param server: the server the command was used in
        :param userid: (str) the id of the user to warn
        :param username: (str) the name of the user to warn
        """
        try:
            member = self.get_server_user(server, userid, username, "You didn't specify a member to warn")
            
            # increment the warning count
            warnings = self.get_warnings(member.id)
            warnings["warnings"] += 1

            # send a PM to the user that they've been warned
            member_pm = ("You have been issued a warning. You have {} warnings. Play nice or else."
                    .format(warnings["warnings"]))
            await self.client.send_message(member, member_pm)

            # report back to the caller how many warnings this person has
            response = ("User {} has been warned and now has {} warnings."
                    .format(self.user_format(member), warnings["warnings"]))
            return response

        except Exception as e:
            return str(e)

    async def unwarn_user(self, server, userid=None, username=None):
        """
        Decreases the number of warnings a user has received.

        :param server: the server the command was used in
        :param userid: (str) the id of the user to unwarn
        :param username: (str) the name of the user to unwarn
        """
        try:
            member = self.get_server_user(server, userid, username, "You didn't specify a user to unwarn")
            # decrement the warning count
            warnings = self.get_warnings(member.id)
            warnings["warnings"] = max(0, warnings["warnings"]-1)

            # report back to the caller how many warnings this person has
            response = "User {} has {} warnings.".format(self.user_format(member), warnings["warnings"])
            return response

        except Exception as e:
            return str(e)

    async def warning_info(self, server, caller, userid=None, username=None):
        """
        Report to the caller how many warnings user "username" has received and if they're on probation.
        If the user is on probation, tell the caller when they were put on probation.

        :param server: the server the command was used in
        :param caller: the user who ran the command
        :param userid: (str) the id of the user to check info on
        :param username: (str) the name of the user to check info on
        """
        try:
            if userid is None and username is None:
                member = caller
            else:
                member = self.get_server_user(server, userid, username, "You didn't specify a user to check")
            # Determine how many warnings the user has and if they're on probation
            warnings = self.get_warnings(member.id, False)
            if warnings["warnings"] == 0:
                response = "User {} has no warnings.".format(self.user_format(member))
                return response

            # report back to the caller how many warnings this person has
            else:
                response = "User {} has {} warnings.".format(self.user_format(member), warnings["warnings"])
                if warnings["probation"]:
                    # Parse the "since" field and convert to a nice, readable time
                    formatted_time = (datetime.datetime.strptime(warnings["since"], "%Y-%m-%dT%H:%M:%S.%f")
                            .strftime("%I:%M %p on %b %d, %Y"))
                    response += " They have been on probation since {}.".format(formatted_time)
                return response

        except Exception as e:
            return str(e)

    async def probation_user(self, server, userid=None, username=None):
        """
        Put user "username" on probation.
        This removes their "Buds" role and prevents them from posting for 24 hours.

        :param server: the server the command was used in
        :param caller: (Member) the user who called the command
        :param userid: (str) the id of the user to probate
        :param username: (str) the name of the user to probate
        """
        try:
            
            member = self.get_server_user(server, userid, username, "You didn't specify a member to put on probation")

            # Add them to the list of users on probation.
            # Do this BEFORE removing their bud role in case check_roles runs between when
            # we remove their role and when we put them on probation.
            warnings = self.get_warnings(member.id)
            if warnings["warnings"] == 0: warnings["warnings"] = 1
            warnings["probation"] = True
            warnings["since"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
            self.warnings[member.id] = warnings

            # Remove the user's "Buds" role.
            buds_role = discord.utils.get(server.roles, id=self.permdb[server.id, 'member_role'])
            await self.client.remove_roles(member, buds_role)

            # Prevent them from posting for 24 hours.
            muted_role = discord.utils.get(server.roles, id=self.permdb[server.id, 'muted_role'])
            await self.client.add_roles(member, muted_role)

            # Notify the caller that the user has been put on probation
            response = "User {} is now on probation.".format(self.user_format(member))
            return response

        except Exception as e:
            return str(e)
            
    async def set_member_role(self, server, member_role_id=None):
        if member_role_id is None: return "You need to specify a role id."

        self.permdb[server.id, 'member_role'] = str(member_role_id)

        return "Set role {} as the member role".format(member_role_id)
        
    async def set_muted_role(self, server, muted_role_id=None):
        if muted_role_id is None: return "You need to specify a role id."

        self.permdb[server.id, 'muted_role'] = str(muted_role_id)

        return "Set role {} as the muted role".format(muted_role_id)


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

    def get_server_user(self, server, userid, username, messageIfNone):
        log.debug(str(userid) + " " + str(username))
        if server is None:
            raise Exception("This command doesn't work in a PM")
        member = None
        if userid is not None:
            member = server.get_member(userid)
        elif username is not None:
            member = server.get_member_named(username)
            if member is None:
                # in case you want to input raw ID instead of username
                member = server.get_member(username)
        if member is None:
            raise Exception(messageIfNone)
        return member
