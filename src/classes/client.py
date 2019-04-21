import time

import enums
import settings
import globals


class Client:
    def __init__(self, connection, address, level=enums.ClientLevel.REGULAR, logged=False):
        self.__connection = connection
        self.__address = address
        self.__username = None
        self.__channel = None
        self.__level = level
        self.__logged = logged

    def get_connection(self):
        return self.__connection

    def get_address(self):
        return self.__address

    def set_username(self, username):
        self.__username = username

    def get_username(self):
        return self.__username

    def set_channel(self, channel):
        self.send_message(enums.ClientAction.ACTIVE_CHANNEL, channel)  # Tell client to set new active channel
        self.__channel = channel

    def get_channel(self):
        return self.__channel

    def set_level(self, level):
        self.__level = level

    def get_level(self):
        return self.__level

    def set_logged(self, logged):
        self.__logged = logged

    def is_logged(self):
        return self.__logged

    def receive_message(self):
        return self.__connection.recv(settings.BUFSIZE).decode(settings.ENCODING)

    def send_message(self, message_type, message):
        self.__connection.send(("$" + message_type.value + message).encode(settings.ENCODING))

    def send_channels(self):
        channels = ""
        for channel in globals.channel_list.values():
            if channel.is_client(self.__username):
                channels += channel.get_name() + ";"
        channels = channels[:-1]
        self.send_message(enums.ClientAction.CHANNEL, channels)
