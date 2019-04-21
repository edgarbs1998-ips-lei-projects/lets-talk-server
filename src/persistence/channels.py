from datetime import datetime
from classes import Channel
import settings
import pickle
import globals

# Created channels list (moderators, banned)
_channels_list = {}


def channels_save():
    global _channels_list
    try:
        with open(settings.PERSISTENCE_PATH + 'channels.pickle', 'wb') as handle:
            pickle.dump(_channels_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print("[%s] Saved persisted channels to file"
                  % datetime.now().strftime(settings.DATETIME_FORMAT))
    except IOError:
        _channels_list = {}
        print("[%s] Failed to saved persisted channels to file"
              % datetime.now().strftime(settings.DATETIME_FORMAT))


def channels_load():
    global _channels_list
    try:
        with open(settings.PERSISTENCE_PATH + 'channels.pickle', 'rb') as handle:
            _channels_list = pickle.load(handle)

            for channel_name, channel_data in _channels_list.items():
                globals.channel_list[channel_name] = Channel(channel_name, channel_data["motd"],
                                                             channel_data["moderators"], channel_data["banned"])

            print("[%s] Loaded persisted channels from file"
                  % datetime.now().strftime(settings.DATETIME_FORMAT))
    except IOError:
        _channels_list = {}
        print("[%s] Failed to load persisted channels from file"
              % datetime.now().strftime(settings.DATETIME_FORMAT))


def create_channel(name):
    _channels_list[name] = {
        "moderators": [],
        "banned": {},
        "motd": None
    }
    channels_save()
    return True


def destroy_channel(name):
    if name in _channels_list:
        del _channels_list[name]
        channels_save()
        return True
    return False


def add_channel_moderator(name, username):
    if name in _channels_list:
        _channels_list[name]["moderators"].append(username)
        channels_save()
        return True
    return False


def remove_channel_moderator(name, username):
    if name in _channels_list:
        if username in _channels_list[name]["moderators"]:
            _channels_list[name]["moderators"].remove(username)
            channels_save()
            return True
    return False


def channel_ban(name, username, timestamp):
    if name in _channels_list:
        _channels_list[name]["banned"][username] = timestamp
    return False


def channel_unban(name, username):
    if name in _channels_list:
        if username in _channels_list[name]["banned"]:
            del _channels_list[name]["banned"][username]
            channels_save()
            return True
    return False


def channel_set_motd(name, motd):
    if name in _channels_list:
        if len(motd) > 0:
            _channels_list[name]["motd"] = motd
        else:
            _channels_list[name]["motd"] = None
        channels_save()
    return False
