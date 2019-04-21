import time
from datetime import datetime
from classes.channel import Channel
import commands
import persistence
import enums
import globals

help_regular = {
    "help": "[HELP] Print the channel available commands and their usage."
            "\nUsage: /channel help",
    "set": "[SET] Set the client active channel."
           "\nUsage: /channel set <channel>",
    "list": "[LIST] List all server channels."
            "\nUsage: /channel list",
    "join": "[JOIN] Join the specified channel if exists and set it as the active channel."
            "\nUsage: /channel join <channel>",
    "leave": "[LEAVE] Leave the specified channel."
             "\nIf no channel is specified, use the active one."
             "\nUsage: /channel leave [channel]",
    "create": "[CREATE] Create a new channel, join it and set it as the active channel."
              "\nUsage: /channel create <name>"
}

help_moderator = {
    "motd": "[MOTD] Set channel message of the day."
            "\nUsage: /channel motd <motd>",
    "destroy": "[DESTROY] Destroy the channel and kick all the clients."
               "\nUsage: /channel destroy",
    "kick": "[KICK] Kick the specified user from the channel."
            "\nUsage: /channel kick <user>",
    "ban": "[BAN] Ban the specified user from the channel."
           "\nIf hours are not specified the ban is permanent."
           "\nUsage: /channel ban <user> [hours]",
    "unban": "[UNBAN] Unban the specified user from the channel."
             "\nUsage: /channel unban <user>",
    "promote": "[PROMOTE] Promote the specified user to channel moderator."
               "\nUsage: /channel promote <user>",
    "demote": "[DEMOTE] Demote the specified user from channel moderator."
              "\nUsage: /channel demote <user>"
}


# Regular commands
def channel_help(client, args, rmx):
    commands.common_help(client, "Channel Commands", help_regular)
    commands.common_help(client, "Channel Commands [Channel Moderator]", help_moderator)

    return True


def channel_join(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_regular["join"])
        return True

    channel_name = args.split(" ", 1)[0].strip()
    if channel_name in globals.channel_list:
        if globals.channel_list[channel_name].is_client(client.get_username()):
            client.send_message(enums.MessageType.ERROR,
                                "You have already joined #%s channel."
                                % channel_name)
            return True

        client_banned = globals.channel_list[channel_name].is_banned(client.get_username())
        if client_banned > 0:
            client.send_message(enums.MessageType.WARNING,
                                "You are banned from the specified channel for %d more hours!"
                                % client_banned)
            return True
        elif client_banned:
            client.send_message(enums.MessageType.WARNING,
                                "You are permanently banned from the specified channel!")
            return True

        globals.channel_list[channel_name].add_client(client.get_username())
        client.send_channels()
        time.sleep(0.2)
        client.set_channel(channel_name)
        client.send_message(enums.MessageType.INFO,
                            "You have joined the #%s channel."
                            "\nThe #%s channel is now your active channel!"
                            % (channel_name, channel_name))

        globals.channel_list[channel_name].send_message(enums.MessageType.INFO,
                                                        "Client @%s has joined the #%s channel!"
                                                        % (client.get_username(), channel_name))

        # Display MOTD message to the user if set
        motd = globals.channel_list[channel_name].get_motd()
        if motd is not None and len(motd) > 0:
            client.send_message(enums.MessageType.MOTD,
                                "%s %s" % (channel_name, motd))
    else:
        client.send_message(enums.MessageType.WARNING,
                            "The specified channel does not exist!"
                            "\nCheck 'channel help' for more info.")

    return True


def channel_set(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_regular["set"])
        return True

    channel_name = args.split(" ", 1)[0].strip()
    if channel_name in globals.channel_list:
        if client.get_channel() == channel_name:
            client.send_message(enums.MessageType.ERROR,
                                "The specified channel is already your active channel!")
            return True

        client.set_channel(channel_name)
    else:
        client.send_message(enums.MessageType.WARNING,
                            "The specified channel does not exist!"
                            "\nCheck '/channel help' for more info.")

    return True


def channel_list(client, args, rmx):
    channels = ""
    for channel_name in globals.channel_list.keys():
        channels += channel_name + " "
    client.send_message(enums.MessageType.INFO,
                        "The following channels are available to join: %s" % channels)

    return True


def channel_leave(client, args, rmx):
    if args is None or len(args) == 0:
        channel_name = client.get_channel()
    else:
        channel_name = args.split(" ", 1)[0].strip()

    if channel_name in globals.channel_list:
        if not globals.channel_list[channel_name].is_client(client.get_username()):
            client.send_message(enums.MessageType.ERROR,
                                "You cannot leave #%s channel because you have not joined it."
                                % channel_name)
            return True

        if channel_name == "general":
            client.send_message(enums.MessageType.ERROR,
                                "You can not leave #general channel!")
            return True

        globals.channel_list[channel_name].remove_client(client.get_username())
        client.send_channels()
        time.sleep(0.2)
        client.send_message(enums.MessageType.INFO,
                            "You have left the #%s channel."
                            % channel_name)

        globals.channel_list[channel_name].send_message(enums.MessageType.INFO,
                                                        "Client @%s has left the #%s channel!"
                                                        % (client.get_username(), channel_name))

        if channel_name == client.get_channel():
            client.set_channel("general")
            client.send_message(enums.MessageType.INFO,
                                "The #general channel has been set as your active channel!")

        client.send_channels()
    else:
        client.send_message(enums.MessageType.WARNING,
                            "The specified channel does not exist! Check '/channel help' for more info.")

    return True


def channel_create(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_regular["create"])
        return True

    channel_name = args.split(" ", 1)[0].strip()
    if channel_name in globals.channel_list:
        client.send_message(enums.MessageType.WARNING,
                            "The specified channel name already exist!"
                            "\nPlease, specify another channel name.")
    else:
        globals.channel_list[channel_name] = Channel(channel_name)
        globals.channel_list[channel_name].add_client(client.get_username())
        globals.channel_list[channel_name].promote_client(client.get_username())

        persistence.channels.create_channel(channel_name)
        persistence.channels.add_channel_moderator(channel_name, client.get_username())

        client.send_channels()
        client.set_channel(channel_name)
        client.send_message(enums.MessageType.INFO,
                            "You have created the #%s channel."
                            "\nThe #%s channel is now your active channel!"
                            % (channel_name, channel_name))

    return True


# Moderator commands
def channel_motd(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_moderator["motd"])
        return True

    channel_name = client.get_channel()
    if channel_name in globals.channel_list:
        if not globals.channel_list[channel_name].is_moderator(client.get_username())\
                and client.get_level().value < enums.ClientLevel.SUPER_MODERATOR.value:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        motd = args.strip()
        globals.channel_list[channel_name].set_motd(motd)

        persistence.channels.channel_set_motd(channel_name, motd)

        client.send_message(enums.MessageType.INFO,
                            "You have set channel motd to: %s"
                            % motd)
    else:
        client.set_channel("general")
        client.send_message(enums.MessageType.ERROR,
                            "Your current active channel is not available."
                            "\nYour active channel has been set to #general!")

    return True


def channel_destroy(client, args, rmx):
    channel_name = client.get_channel()
    if channel_name in globals.channel_list:
        if not globals.channel_list[channel_name].is_moderator(client.get_username())\
                and client.get_level().value < enums.ClientLevel.SUPER_MODERATOR.value:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        if channel_name == "general":
            client.send_message(enums.MessageType.ERROR,
                                "You can not destroy #general channel!")
            return True

        print(globals.channel_list[channel_name].get_clients())  # TODO Fix this shit
        for channel_client_username in globals.channel_list[channel_name].get_clients():
            globals.channel_list[channel_name].remove_client(channel_client_username)
            if channel_client_username in globals.client_list:
                channel_client = globals.client_list[channel_client_username]
                channel_client.send_channels()
                channel_client.send_message(enums.MessageType.INFO,
                                            "You have left channel #%s because it has been destroyed!"
                                            % channel_name)
                if channel_client.get_channel() == channel_name:
                    channel_client.set_channel("general")
                    channel_client.send_message(enums.MessageType.INFO,
                                               "Your active channel has been destroyed!"
                                               "\nYour active channel has been set to #general.")
        del globals.channel_list[channel_name]
        persistence.channels.destroy_channel(channel_name)
    else:
        client.set_channel("general")
        client.send_message(enums.MessageType.ERROR,
                            "Your current active channel is not available."
                            "\nYour active channel has been set to #general!")

    return True


def channel_kick(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_moderator["kick"])
        return True

    channel_name = client.get_channel()
    if channel_name in globals.channel_list:
        if not globals.channel_list[channel_name].is_moderator(client.get_username())\
                and client.get_level().value < enums.ClientLevel.SUPER_MODERATOR.value:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        if channel_name == "general":
            client.send_message(enums.MessageType.ERROR,
                                "You can not kick users from #general channel!\n"
                                "Kick from server instead.")
            return True

        client_name = args.split(" ", 1)[0].strip()
        if not globals.channel_list[channel_name].is_client(client_name):
            client.send_message(enums.MessageType.ERROR,
                                "The specified user is not in the channel!")
            return True

        globals.channel_list[channel_name].remove_client(client_name)
        kick_client = globals.client_list[client_name]
        kick_client.send_message(enums.MessageType.WARNING,
                                 "You have been kicked from #%s channel!"
                                 % channel_name)

        globals.channel_list[channel_name].send_message(enums.MessageType.INFO,
                                                        "Client @%s has been kicked from the #%s channel!"
                                                        % (client.get_username(), channel_name))

        if kick_client.get_channel() == channel_name:
            kick_client.set_channel("general")
            kick_client.send_message(enums.MessageType.INFO,
                                     "The #general channel has been set as your active channel!")
        kick_client.send_channels()

        client.send_message(enums.MessageType.INFO,
                            "You have kicked @%s from the channel!"
                            % client_name)
    else:
        client.set_channel("general")
        client.send_message(enums.MessageType.ERROR,
                            "Your current active channel is not available."
                            "\nYour active channel has been set to #general!")

    return True


def channel_ban(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_moderator["ban"])
        return True

    channel_name = client.get_channel()
    if channel_name in globals.channel_list:
        if not globals.channel_list[channel_name].is_moderator(client.get_username())\
                and client.get_level().value < enums.ClientLevel.SUPER_MODERATOR.value:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        if channel_name == "general":
            client.send_message(enums.MessageType.ERROR,
                                "You can not ban users from #general channel!"
                                "\nBan from server instead.")
            return True

        ban_args = args.split(" ", 1)
        client_name = ban_args[0].strip()
        if len(ban_args) > 1:
            ban_hours = float(ban_args[1].strip())
            if ban_hours < 1:
                client.send_message(enums.MessageType.WARNING,
                                    "The minimum ban duration is 1 hour!")
                return True
            ban_seconds = ban_hours * 60 * 60
            ban_duration = datetime.timestamp(datetime.now()) + ban_seconds
        else:
            ban_hours = 0
            ban_duration = None

        globals.channel_list[channel_name].add_banned(client_name, ban_duration)
        globals.channel_list[channel_name].remove_client(client_name)
        persistence.channels.channel_ban(channel_name, client_name, ban_duration)
        ban_client = globals.client_list[client_name]
        if client_name in globals.client_list:
            if ban_duration is None:
                ban_client.send_message(enums.MessageType.WARNING,
                                        "You have been permanently banned from the #%s channel!"
                                        % channel_name)
            else:
                ban_client.send_message(enums.MessageType.WARNING,
                                        "You have been banned from the #%s channel for %d hours!"
                                        % (channel_name, ban_hours))

        globals.channel_list[channel_name].send_message(enums.MessageType.INFO,
                                                        "Client @%s has been banned from the #%s channel!"
                                                        % (client_name, channel_name))

        if ban_client.get_channel() == channel_name:
            ban_client.set_channel("general")
            ban_client.send_message(enums.MessageType.INFO,
                                    "The #general channel has been set as your active channel!")
        ban_client.send_channels()

        client.send_message(enums.MessageType.INFO,
                            "You have banned @%s from the channel!"
                            % client_name)
    else:
        client.set_channel("general")
        client.send_message(enums.MessageType.ERROR,
                            "Your current active channel is not available."
                            "\nYour active channel has been set to #general!")

    return True


def channel_unban(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_moderator["unban"])
        return True

    channel_name = client.get_channel()
    if channel_name in globals.channel_list:
        if not globals.channel_list[channel_name].is_moderator(client.get_username())\
                and client.get_level().value < enums.ClientLevel.SUPER_MODERATOR.value:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        client_name = args.split(" ", 1)[0].strip()
        if not globals.channel_list[channel_name].is_banned(client_name):
            client.send_message(enums.MessageType.ERROR,
                                "The specified user is not banned from the channel!")
            return True

        globals.channel_list[channel_name].remove_banned(client_name)
        persistence.channels.channel_unban(channel_name, client_name)

        if client_name in globals.client_list:
            globals.client_list[client_name].send_message(enums.MessageType.INFO,
                                                          "You have been unbanned from #%s channel!"
                                                          % channel_name)

        client.send_message(enums.MessageType.INFO,
                            "You have unbanned @%s from the channel!"
                            % client_name)
    else:
        client.set_channel("general")
        client.send_message(enums.MessageType.ERROR,
                            "Your current active channel is not available."
                            "\nYour active channel has been set to #general!")

    return True


def channel_promote(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_moderator["promote"])
        return True

    channel_name = client.get_channel()
    if channel_name in globals.channel_list:
        if not globals.channel_list[channel_name].is_moderator(client.get_username())\
                and client.get_level().value < enums.ClientLevel.SUPER_MODERATOR.value:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        client_name = args.split(" ", 1)[0].strip()
        if not globals.channel_list[channel_name].is_client(client_name):
            client.send_message(enums.MessageType.ERROR,
                                "The specified user is not in the channel!")
            return True

        globals.channel_list[channel_name].promote_client(client_name)
        persistence.channels.add_channel_moderator(channel_name, client_name)

        if client_name in globals.client_list:
            globals.client_list[client_name].send_message(enums.MessageType.INFO,
                                                          "You have been promoted to channel moderator on #%s channel!"
                                                          % channel_name)

        client.send_message(enums.MessageType.INFO,
                            "You have promoted @%s to channel moderator!"
                            % client_name)
    else:
        client.set_channel("general")
        client.send_message(enums.MessageType.ERROR,
                            "Your current active channel is not available."
                            "\nYour active channel has been set to #general!")

    return True


def channel_demote(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_moderator["demote"])
        return True

    channel_name = client.get_channel()
    if channel_name in globals.channel_list:
        if not globals.channel_list[channel_name].is_moderator(client.get_username())\
                and client.get_level().value < enums.ClientLevel.SUPER_MODERATOR.value:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        client_name = args.split(" ", 1)[0].strip()
        if not globals.channel_list[channel_name].is_client(client_name):
            client.send_message(enums.MessageType.ERROR,
                                "The specified user is not in the channel!")
            return True

        globals.channel_list[channel_name].demote_client(client_name)
        persistence.channels.remove_channel_moderator(channel_name, client_name)

        if client_name in globals.client_list:
            globals.client_list[client_name].send_message(enums.MessageType.INFO,
                                                          "You have been demoted from channel moderator on #%s channel!"
                                                          % channel_name)

        client.send_message(enums.MessageType.INFO, "You have demoted @%s from channel moderator!"
                            % client_name)
    else:
        client.set_channel("general")
        client.send_message(enums.MessageType.ERROR,
                            "Your current active channel is not available."
                            "\nYour active channel has been set to #general!")

    return True


switcher = {
    # Regular commands
    "help": channel_help,
    "set": channel_set,
    "list": channel_list,
    "join": channel_join,
    "leave": channel_leave,
    "create": channel_create,

    # Moderator commands
    "motd": channel_motd,
    "destroy": channel_destroy,
    "kick": channel_kick,
    "ban": channel_ban,
    "unban": channel_unban,
    "promote": channel_promote,
    "demote": channel_demote
}


def channel(client, command, args, rmx):
    if args is None or len(args) == 0:
        return channel_help(client, args, rmx)

    command_args = args.split(" ", 1)
    command = command_args[0]
    if len(command_args) > 1:
        args = command_args[1].strip()
    else:
        args = None

    # Get the function from switcher dictionary
    func = switcher.get(command, channel_help)
    # Execute the function
    return func(client, args, rmx)
