from datetime import datetime
import commands
import enums
import globals
import settings


def common_help(client, title, help_messages):
    message = title
    for key in help_messages:
        message += "\n" + help_messages[key]
    client.send_message(enums.MessageType.HELP, message)


def client_message(client, message, rmx):
    if not client.is_logged():
        client.send_message(enums.MessageType.WARNING,
                            "In order to use this chat you do need to register your username."
                            "\nFor that just type '/register <password>'.")
        return True

    if client.get_channel() not in globals.channel_list:
        client.set_channel("general")
        client.send_message(enums.MessageType.ERROR,
                            "Your current active channel is not available."
                            "\nYour active channel has been set to #general!")
        return True

    message = message.strip()
    globals.channel_list[client.get_channel()].send_message(enums.MessageType.MESSAGE,
                                                            "%f %s %s %s"
                                                            % (datetime.timestamp(rmx), client.get_username(),
                                                               client.get_channel(), message))

    return True


def parse(client, message, rmx):
    message = message.strip()
    if message[0] == "/":
        command_args = message.split(" ", 1)
        command = command_args[0][1:]  # Remove the '/' character
        if len(command) == 0:
            return commands.general_help(client, None, rmx)

        if len(command_args) > 1:
            args = command_args[1].strip()
        else:
            args = None

        if not client.is_logged() and command != "register" and command != "exit":
            client.send_message(enums.MessageType.WARNING,
                                "In order to use this chat you do need to register your username."
                                "\nFor that just type '/register <password>'.")
            return True

        # Get the function from 'commands'. Default to general commands.
        func = getattr(commands, command, commands.general)
        # Call the function as we return it
        return func(client, command, args, rmx)
    elif len(message) > 0:
        return client_message(client, message, rmx)
    else:
        print("[%s] Commands parser ignored the message from @%s on #%s."
              % (datetime.now().strftime(settings.DATETIME_FORMAT), client.get_username(), client.get_channel()))
        return True
