from datetime import datetime
import math
import globals


class Channel:
    def __init__(self, name, motd=None, moderators=None, banned=None):
        if banned is None:
            banned = {}
        if moderators is None:
            moderators = []
        self.__name = name
        self.__motd = motd
        self.__clients = []
        self.__moderators = moderators
        self.__banned = banned

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_motd(self, motd):
        if len(motd) > 0:
            self.__motd = motd
        else:
            self.__motd = None

    def get_motd(self):
        return self.__motd

    def add_client(self, username):
        self.__clients.append(username)

    def remove_client(self, username):
        if username in self.__clients:
            self.__clients.remove(username)
            return True
        return False

    def is_client(self, username):
        if username in self.__clients:
            return True
        return False

    def get_clients(self):
        return self.__clients

    def promote_client(self, username):
        if username in self.__clients:
            self.__moderators.append(username)
            return True
        return False

    def demote_client(self, username):
        if username in self.__moderators:
            self.__moderators.remove(username)
            return True
        return False

    def is_moderator(self, username):
        if username in self.__moderators:
            return True
        return False

    def add_banned(self, username, timestamp):
        if username in self.__clients:
            del self.__clients[username]
        self.__banned[username] = timestamp

    def remove_banned(self, username):
        if username in self.__banned:
            del self.__banned[username]
            return True
        return False

    def is_banned(self, username):
        if username in self.__banned:
            banned_timestamp = self.__banned[username]
            if banned_timestamp is None:
                return True
            else:
                diff = banned_timestamp - datetime.timestamp(datetime.now())
                if diff > 0:
                    diff_hours = math.ceil(diff / 60 / 60)
                    return diff_hours
                else:
                    self.remove_banned(username)
                    return False
        return False

    def send_message(self, message_type, message):
        for username in self.__clients:
            if username in globals.client_list:
                globals.client_list[username].send_message(message_type, message)
            else:
                del self.__clients[username]
