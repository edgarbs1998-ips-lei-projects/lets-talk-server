import pickle
from datetime import datetime
import math
import enums
import uuid
import hashlib

# Create user accounts list (password, level, banned)
import settings

_users_list = {}


def users_save():
    global _users_list
    try:
        with open(settings.PERSISTENCE_PATH + 'users.pickle', 'wb') as handle:
            pickle.dump(_users_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print("[%s] Saved persisted users to file"
                  % datetime.now().strftime(settings.DATETIME_FORMAT))
    except IOError:
        _users_list = {}
        print("[%s] Failed to saved persisted users to file"
              % datetime.now().strftime(settings.DATETIME_FORMAT))


def users_load():
    global _users_list
    try:
        with open(settings.PERSISTENCE_PATH + 'users.pickle', 'rb') as handle:
            _users_list = pickle.load(handle)
            print("[%s] Loaded persisted users from file"
                  % datetime.now().strftime(settings.DATETIME_FORMAT))
    except IOError:
        _users_list = {}
        print("[%s] Failed to load persisted users from file"
              % datetime.now().strftime(settings.DATETIME_FORMAT))


def create_client(username, password):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    password_hash = hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    _users_list[username] = {
        "password": password_hash,
        "level": enums.ClientLevel.REGULAR,
        "banned": False
    }
    users_save()
    return True


def update_client_password(username, password):
    if username in _users_list:
        # uuid is used to generate a random number
        salt = uuid.uuid4().hex
        password_hash = hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

        _users_list[username]["password"] = password_hash
        users_save()
        return True
    return False


def promote_client(username):
    if username in _users_list:
        _users_list[username]["level"] = enums.ClientLevel.SUPER_MODERATOR
        users_save()
        return True
    return False


def demote_client(username):
    if username in _users_list:
        _users_list[username]["level"] = enums.ClientLevel.REGULAR
        users_save()
        return True
    return False


def get_level(username):
    if username in _users_list:
        return _users_list[username]["level"]
    return False


def ban_client(username, timestamp):
    if username in _users_list:
        _users_list[username]["banned"] = timestamp
        users_save()
        return True
    return False


def unban_client(username):
    if username in _users_list:
        _users_list[username]["banned"] = False
        users_save()
        return True
    return False


def is_banned(username):
    if username in _users_list:
        banned_timestamp = _users_list[username]["banned"]
        if banned_timestamp is None:
            return True
        else:
            diff = banned_timestamp - datetime.timestamp(datetime.now())
            if diff > 0:
                diff_hours = math.ceil(diff / 60 / 60)
                return diff_hours
            else:
                unban_client(username)
                return False
    return False


def client_exists(username):
    if username in _users_list:
        return True
    else:
        return False


def get_client(username, password):
    if username in _users_list:
        client_password, salt = _users_list[username]["password"].split(':')
        if client_password == hashlib.sha256(salt.encode() + password.encode()).hexdigest():
            return _users_list[username]
    return False
