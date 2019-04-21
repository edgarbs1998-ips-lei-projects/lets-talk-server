from datetime import datetime
import commands
import persistence
import globals
import enums

help_regular = {
    "help": "[HELP] Print the available commands and their usage."
            "\nUsage: /help",
    "register": "[REGISTER] Register your current username."
                "\nUsage: /register <password>",
    "user": "[USER] Commands related to user management."
            "\nUsage: user <action> [arguments]"
            "\nHelp: /user help",
    "channel": "[CHANNEL] Commands related to channel usage and management."
               "\nUsage: channel <action> [arguments]"
               "\nHelp: /channel help",
    "exit": "[EXIT] Disconnects you from the chat."
            "\nUsage: /exit",
}

help_super_moderator = {
    "broadcast": "[BROADCAST] Send a message to all connected clients."
                 "\nUsage: /broadcast <message>",
}


def general_help(client, args, rmx):
    commands.common_help(client, "General Commands", help_regular)

    if client.get_level().value == enums.ClientLevel.SUPER_MODERATOR.value:
        commands.common_help(client, "General Commands [Super Moderator]", help_super_moderator)

    return True


def general_register(client, args, rmx):
    if client.is_logged():
        client.send_message(enums.MessageType.WARNING, "You are already registered!")
        return True

    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_regular["register"])
        return True

    password = args.split(" ", 1)[0].strip()
    if len(password) < 6:
        client.send_message(enums.MessageType.ERROR, "Your password must be at least 6 characters long!"
                                                     "\nPlease, try to register again using '/register <password>'.")
        return True

    persistence.users.create_client(client.get_username(), password)
    client.set_logged(True)
    client.send_message(enums.MessageType.INFO, "Your account has been registered."
                                                "\nYou are now logged in!")

    return True


def general_broadcast(client, args, rmx):
    if args is None or len(args) == 0:
        client.send_message(enums.MessageType.HELP, help_super_moderator["broadcast"])
        return True

    if client.get_level().value < enums.ClientLevel.SUPER_MODERATOR.value:
        client.send_message(enums.MessageType.ERROR,
                            "You are not allowed to use this command!")
        return True

    for broadcast_client in globals.client_list.values():
        broadcast_client.send_message(enums.MessageType.BROADCAST,
                                      "%f %s %s"
                                      % (datetime.timestamp(rmx), client.get_username(), args))

    return True


def general_exit(client, args, rmx):
    client.send_message(enums.ClientAction.EXIT,
                        "Goodbye %s!"
                        % client.get_username())
    return False


switcher = {
    "help": general_help,
    "register": general_register,
    "broadcast": general_broadcast,
    "exit": general_exit
}


def general(client, command, args, rmx):
    # Get the function from switcher dictionary. Default to command_help
    func = switcher.get(command, general_help)
    # Execute the function
    return func(client, args, rmx)
