import os
from config import settings

### URL ###
BASE_URL = "http://192.168.11.46:8080/" if settings.DEBUG else "https://fullfii.com/"

### static ###
USER_EMPTY_ICON_PATH = "static/images/user_empty_icon.png"

### slack webhooks ###
SLACK_WEBHOOKS_FULLFII_BOT_URL = settings.SLACK_WEBHOOKS_FULLFII_BOT_URL

### admin URL ###
def gene_account_admin_url(account_id):
    return os.path.join(BASE_URL, f"admin/account/account/{str(account_id)}/change/")


def gene_room_admin_url(room_id):
    return os.path.join(BASE_URL, f"admin/chat/roomv4/{str(room_id)}/change/")


### confluence ###
CONFLUENCE_URL_GUIDE_BAN = (
    "https://fullfii.atlassian.net/wiki/spaces/FULLFII/pages/238747656"
)
