from classes.client import Client
from datetime import datetime
import persistence
import commands
import socket
import threading
import enums
import globals
import settings


# Client listen function
def handle_client(connection, address):
    client = Client(connection, address)
    try:
        while True:
            client.send_message(enums.MessageType.INFO,
                                "Can you please indicate your username?")
            client_username = client.receive_message()
            if client_username == "/exit":
                commands.general_exit(client, None, None)
                client.get_connection().close()
                print("[%s] Client from IP address %s disconnected!"
                      % (datetime.now().strftime(settings.DATETIME_FORMAT), client.get_address()))
                return True

            if len(client_username) < 3:
                client.send_message(enums.MessageType.ERROR,
                                    "Your username must be at least 3 characters long!")
                continue

            # Check if client username is banned
            client_banned = persistence.users.is_banned(client_username)
            if client_banned > 0:
                client.send_message(enums.MessageType.ERROR,
                                    "Your username is banned from the server for %d more hours!"
                                    % client_banned)
                client.get_connection().close()
                print("[%s] Client with username %s is banned for %d more hours!"
                      % (datetime.now().strftime(settings.DATETIME_FORMAT), client_username, client_banned))
                return True
            elif client_banned:
                client.send_message(enums.MessageType.ERROR,
                                    "Your username is permanently banned from the server!")
                client.get_connection().close()
                print("[%s] Client with username %s is permanently banned!"
                      % (datetime.now().strftime(settings.DATETIME_FORMAT), client_username))
                return True

            if client_username in globals.client_list:
                client.send_message(enums.MessageType.ERROR,
                                    "The indicated username is already connected!")
            elif persistence.users.client_exists(client_username):
                client.send_message(enums.MessageType.INFO,
                                    "This username is registered, please indicate your password!")
                client_password = client.receive_message()
                if persistence.users.get_client(client_username, client_password):
                    client.set_logged(True)
                    client.set_level(persistence.users.get_level(client_username))
                    client.send_message(enums.MessageType.INFO,
                                        "You are now logged in!")
                    break
                else:
                    client.send_message(enums.MessageType.ERROR,
                                        "The typed password is wrong, please try again!")
            else:
                break

        client.set_username(client_username)
        globals.client_list[client.get_username()] = client
        client.send_message(enums.MessageType.INFO,
                            "You are now connected, %s!"
                            % client.get_username())
        for channel_client in globals.channel_list["general"].get_clients():
            if channel_client in globals.client_list:
                globals.client_list[channel_client].send_message(enums.MessageType.INFO,
                                                                 "Client @%s connected to the server!"
                                                                 % client.get_username())
        print("[%s] Client connected with username %s"
              % (datetime.now().strftime(settings.DATETIME_FORMAT), client.get_username()))

        # Join 'general' channel by default
        commands.channel_join(client, "general", None)

        if not client.is_logged():
            client.send_message(enums.MessageType.INFO,
                                "In order to use this chat you do need to register your username."
                                "\nFor that just type '/register <password>'.")

        while True:
            message = client.receive_message()
            rmx = datetime.now()

            print("[%s] Received from @%s on #%s: %s"
                  % (datetime.now().strftime(settings.DATETIME_FORMAT),
                     client.get_username(), client.get_channel(), message))
            if not commands.parse(client, message, rmx):
                break

        # Close client connection
        for channel in globals.channel_list.values():
            channel.remove_client(client.get_username())
            for channel_client in globals.channel_list["general"].get_clients():
                if channel_client in globals.client_list:
                    globals.client_list[channel_client].send_message(enums.MessageType.INFO,
                                                                     "Client @%s connected to the server!"
                                                                     % client.get_username())
        if client.get_username() in globals.client_list:
            globals.client_list.pop(client.get_username())
        client.get_connection().close()
        print("[%s] Client %s disconnected!"
              % (datetime.now().strftime(settings.DATETIME_FORMAT), client.get_username()))
    except socket.error as error:
        if client.get_username() is not None:
            for channel in globals.channel_list.values():
                channel.remove_client(client.get_username())
                for channel_client in globals.channel_list["general"].get_clients():
                    if channel_client in globals.client_list:
                        globals.client_list[channel_client].send_message(enums.MessageType.INFO,
                                                                         "Client @%s connected to the server!"
                                                                         % client.get_username())
            if client.get_username() in globals.client_list:
                globals.client_list.pop(client.get_username())
        client.get_connection().close()
        print("[%s] Client from IP address %s connection error! error: %s"
              % (datetime.now().strftime(settings.DATETIME_FORMAT), address, error))


# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((settings.SERVER_HOST, settings.SERVER_PORT))
server_socket.listen(5)
print("[%s] Server listening on host %s and port %s ..."
      % (datetime.now().strftime(settings.DATETIME_FORMAT), settings.SERVER_HOST, settings.SERVER_PORT))

# Load persisted data
persistence.channels.channels_load()
persistence.users.users_load()

while True:
    # Wait for client connections
    client_connection, client_address = server_socket.accept()

    # Start a new thread for the client
    threading.Thread(target=handle_client, args=(client_connection, client_address)).start()

# Close socket
server_socket.close()
