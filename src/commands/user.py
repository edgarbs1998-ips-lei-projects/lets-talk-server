from datetime import datetime
import commands
import enums
import persistence
import globals

help_regular = {
    "help": "[HELP] Print the client available commands and their usage."
            "\nUsage: client help",
    "password": "[PASSWORD] Change your accounts password."
                "\nUsage: client password <password>",
    "private": "[PRIVATE] Send a private message to a specified user."
               "\nUsage: client private <user> <message>"
}

help_super_moderator = {
    "kick": "[KICK] Kick the specified user from the server."
            "\nUsage: client kick <user>",
    "ban": "[BAN] Ban the specified user from the server."
           "\nIf hours are not specified the ban is permanent."
           "\nUsage: client ban <user> [hours]",
    "unban": "[UNBAN] Unban the specified user from the server."
             "\nUsage: client unban <user>",
    "promote": "[PROMOTE] Promote the specified user to super moderator."
               "\nUsage: client promote <user>",
    "demote": "[DEMOTE] Demote the specified user from super moderator."
              "\nUsage: client demote <user>",
}


# Regular commands
def user_help(client, args, rmx):
    commands.common_help(client, "Client Commands", help_regular)
    commands.common_help(client, "Client Commands [Super Moderator]", help_super_moderator)

    return True


def user_password(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_regular["password"])
        return True

    password = args.split(" ", 1)[0].strip()
    if len(password) < 6:
        client.send_message(enums.MessageType.ERROR,
                            "Your password must be at least 6 characters long!"
                            "\nPlease, try again with a different password.")
        return True

    persistence.users.update_client_password(client.get_username(), password)
    client.send_message(enums.MessageType.INFO,
                        "You have changed your account password!")

    return True


def user_private(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_regular["private"])
        return True

    private_args = args.split(" ", 1)
    client_name = private_args[0].strip()
    if len(private_args) <= 1:
        client.send_message(enums.MessageType.HELP, help_regular["private"])
        return True
    message = private_args[1].strip()

    if client_name in globals.client_list.keys():
        globals.channel_list[client_name].send_message(enums.MessageType.PRIVATE,
                                                       "%f %s %s"
                                                       % (datetime.timestamp(rmx), client.get_username(), message))
        client.send_message(enums.MessageType.INFO,
                            "Your ptivate message to @%s has been sent!"
                            % client_name)
    else:
        client.send_message(enums.MessageType.WARNING,
                            "The specified client is not connected to the server!")

    return True


# Super moderator commands
def user_kick(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_super_moderator["kick"])
        return True

    if client.get_level() < enums.ClientLevel.SUPER_MODERATOR:
        client.send_message(enums.MessageType.ERROR,
                            "You are not allowed to use this command!")
        return True

    client_name = args.split(" ", 1)[0].strip()
    if client_name not in globals.client_list:
        client.send_message(enums.MessageType.ERROR,
                            "The specified client is not connected to the server!")
        return True

    globals.client_list[client_name].send_message(enums.ClientAction.KICK,
                                                  "You have been kicked from the server")

    client.send_message(enums.MessageType.INFO,
                        "You have kicked @%s from the server!"
                        % client_name)

    return True


def user_ban(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_super_moderator["ban"])
        return True

    if client.get_level() < enums.ClientLevel.SUPER_MODERATOR:
        client.send_message(enums.MessageType.ERROR,
                            "You are not allowed to use this command!")
        return True

    ban_args = args.split(" ", 1)
    client_name = ban_args[0].strip()
    if client_name not in globals.client_list:
        client.send_message(enums.MessageType.ERROR,
                            "The specified client is not connected to the server!")
        return True

    if len(ban_args) > 1:
        ban_hours = ban_args[1].strip()
        ban_seconds = ban_hours * 60 * 60
        ban_duration = datetime.timestamp(datetime.now()) + ban_seconds
    else:
        ban_hours = 0
        ban_duration = None

    persistence.users.ban_client(client.get_username(), ban_duration)

    ban_client = globals.client_list[client_name]
    if ban_duration is None:
        ban_client.send_message(enums.ClientAction.KICK,
                                "You have been permanently banned from the server!")
        client.send_message(enums.MessageType.INFO,
                            "You have permanently baned @%s from the server!"
                            % client_name)
    else:
        ban_client.send_message(enums.ClientAction.KICK,
                                "You have been banned from the server for %d hours!"
                                % ban_hours)
        client.send_message(enums.MessageType.INFO,
                            "You have baned @%s from the server for %d hours!"
                            % (client_name, ban_hours))

    return True


def user_unban(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_super_moderator["unban"])
        return True

    if client.get_level() < enums.ClientLevel.SUPER_MODERATOR:
        client.send_message(enums.MessageType.ERROR,
                            "You are not allowed to use this command!")
        return True

    client_name = args.split(" ", 1)[0].strip()
    if not persistence.users.is_banned(client_name):
        client.send_message(enums.MessageType.ERROR,
                            "The specified user is not banned from the server!")
        return True

    persistence.users.unban_client(client_name)

    client.send_message(enums.MessageType.INFO,
                        "You have unbanned @%s from the server!"
                        % client_name)

    return True


def user_promote(client, args, rmx):
    if args is None or len(args) == 0:
        if args is None or len(args) == 0:
            client.send_message(enums.MessageType.HELP, help_super_moderator["promote"])
            return True

        if client.get_level() < enums.ClientLevel.SUPER_MODERATOR:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        client_name = args.split(" ", 1)[0].strip()

        persistence.users.promote_client(client_name)
        if client_name is globals.client_list.keys():
            promote_client = globals.client_list[client_name]
            promote_client.set_level(client_name, enums.ClientLevel.SUPER_MODERATOR)
            promote_client.sen_message(enums.MessageType.INFO,
                                       "You have been promoted to server super moderator!")

        client.send_message(enums.MessageType.INFO,
                            "You have promoted @%s to server super moderator!"
                            % client_name)

        return True


def user_demote(client, args, rmx):
    if args is None or len(args) == 0:
        if args is None or len(args) == 0:
            client.send_message(enums.MessageType.HELP, help_super_moderator["demote"])
            return True

        if client.get_level() < enums.ClientLevel.SUPER_MODERATOR:
            client.send_message(enums.MessageType.ERROR,
                                "You are not allowed to use this command!")
            return True

        client_name = args.split(" ", 1)[0].strip()

        persistence.users.demote_client(client_name)
        if client_name is globals.client_list.keys():
            demote_client = globals.client_list[client_name]
            demote_client.set_level(client_name, enums.ClientLevel.REGULAR)
            demote_client.sen_message(enums.MessageType.INFO,
                                      "You have been demoted from server super moderator!")

        client.send_message(enums.MessageType.INFO,
                            "You have demoted @%s from server super moderator!"
                            % client_name)

        return True


switcher = {
    # # Regular commands
    "help": user_help,
    "password": user_password,
    "private": user_private,

    # Moderator commands
    "kick": user_kick,
    "ban": user_ban,
    "unban": user_unban,
    "promote": user_promote,
    "demote": user_demote
}


def user(client, command, args, rmx):
    if args is None or len(args) == 0:
        return user_help(client, args, rmx)

    command_args = args.split(" ", 1)
    command = command_args[0]
    if len(command_args) > 1:
        args = command_args[1].strip()
    else:
        args = None

    # Get the function from switcher dictionary
    func = switcher.get(command, user_help)
    # Execute the function
    return func(client, args, rmx)
