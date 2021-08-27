import os
from config import settings

### URL ###
BASE_URL = "http://192.168.11.46:8080/" if settings.DEBUG else "https://fullfii.com/"

### static ###
USER_EMPTY_ICON_PATH = "static/images/user_empty_icon.png"

### slack webhooks ###
SLACK_WEBHOOKS_URL_MSG_WARNING = settings.SLACK_WEBHOOKS_URL_MSG_WARNING
SLACK_WEBHOOKS_URL_MSG_TABOO = settings.SLACK_WEBHOOKS_URL_MSG_TABOO
SLACK_WEBHOOKS_URL_ROOM_WARNING = settings.SLACK_WEBHOOKS_URL_ROOM_WARNING
SLACK_WEBHOOKS_URL_ROOM_TABOO = settings.SLACK_WEBHOOKS_URL_ROOM_TABOO

### admin URL ###
def gene_account_admin_url(account_id):
    return os.path.join(BASE_URL, f"admin/account/account/{str(account_id)}/change/")


def gene_room_admin_url(room_id):
    return os.path.join(BASE_URL, f"admin/chat/roomv4/{str(room_id)}/change/")


def gene_messages_admin_url(room_id, message_id=None):
    return os.path.join(BASE_URL, f"admin/rooms/{str(room_id)}/messages/") + (
        f"#{message_id}" if message_id is not None else ""
    )


### confluence ###
CONFLUENCE_URL_GUIDE_BAN = (
    "https://fullfii.atlassian.net/wiki/spaces/FULLFII/pages/238747656"
)
