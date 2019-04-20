from enum import Enum


class ClientAction(Enum):
    ACTIVE_CHANNEL = "active_channel "
    CHANNEL = "channel "
    KICK = "kick "
    EXIT = "exit "


class MessageType(Enum):
    INFO = "info "
    WARNING = "warning "
    ERROR = "error "
    MESSAGE = "message "
    HELP = "help "
    MOTD = "motd "
    BROADCAST = "broadcast "
    PRIVATE = "private "


class ClientLevel(Enum):
    REGULAR = 0
    SUPER_MODERATOR = 1
