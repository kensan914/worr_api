import json
from abc import abstractmethod
import requests

from account.v4.serializers import UserSerializer
from fullfii.lib.constants import (
    SLACK_WEBHOOKS_FULLFII_BOT_URL,
    gene_account_admin_url,
    gene_room_admin_url,
    CONFLUENCE_URL_GUIDE_BAN,
    gene_messages_admin_url,
)
from fullfii.lib.inappropriate_checker import InappropriateType


class SlackSender:
    def __init__(self):
        self.settings = self.generate_settings()

    def update_settings(self):
        self.settings = self.generate_settings()

    def send(self):
        if not SLACK_WEBHOOKS_FULLFII_BOT_URL:
            print("slack webhooks URLが未設定です")
            return False
        if self.settings is None:
            print("settingsが未設定です")
            return False

        requests.post(
            SLACK_WEBHOOKS_FULLFII_BOT_URL,
            data=json.dumps(self.settings),
        )

    @abstractmethod
    def generate_settings(self):
        return None


class InappropriateAlertSlackSender(SlackSender):
    """不適切アラート"""

    def __init__(
        self,
        _sender,
        _room,
    ):
        self.sender = _sender
        self.room = _room
        self.inappropriate_type = InappropriateType.TABOO
        self.message_text = ""
        self.message_id = None
        self.inappropriate_word_text = ""
        super().__init__()

    def generate_settings(self):
        # "タブー" or "警告"
        inappropriate_type_label = {
            InappropriateType.TABOO: "タブー",
            InappropriateType.WARNING: "警告",
        }
        inappropriate_type_icon = {
            InappropriateType.TABOO: ":no_entry_sign:",
            InappropriateType.WARNING: ":warning:",
        }
        main_text = f"{inappropriate_type_icon[self.inappropriate_type]} *【{inappropriate_type_label[self.inappropriate_type]}】不適切アラート* {inappropriate_type_icon[self.inappropriate_type]}"
        pretext = {
            InappropriateType.TABOO: f" *{self.sender}* さんが以下のタブーメッセージを発言したため、自動凍結処理を行いました。メッセージが安全と判断された場合は、速やかに凍結解除を行ってください。",
            InappropriateType.WARNING: f" *{self.sender}* さんが以下の警告メッセージを発言しました。内容を確認し、凍結の検討・判断をしてください。",
        }
        fallback = {
            InappropriateType.TABOO: f"{self.sender}さんがタブーメッセージを発言したため、自動凍結処理を行いました。",
            InappropriateType.WARNING: f"{self.sender}さんが以下の警告メッセージを発言しました。内容を確認し、凍結の検討・判断をしてください。",
        }
        attachment_color = {
            InappropriateType.TABOO: "#d9534f",
            InappropriateType.WARNING: "#f0ad4e",
        }
        guide_attachment_field = {
            InappropriateType.TABOO: {
                "title": "【凍結解除手順】",
                "value": f"<{gene_account_admin_url(self.sender.id)}|アカウントページ>へアクセスし, 以下を実行\n1. :white_large_square:「凍結状態」のチェックを外す\n2. :ok_hand:「保存」をクリック\n詳しいガイドは<{CONFLUENCE_URL_GUIDE_BAN}|こちら>から",
            },
            InappropriateType.WARNING: {
                "title": "【凍結手順】",
                "value": f"<{gene_account_admin_url(self.sender.id)}|アカウントページ>へアクセスし, 以下を実行\n1. :ballot_box_with_check:「凍結状態」にチェックを入れる\n2. :ok_hand:「保存」をクリック\n詳しいガイドは<{CONFLUENCE_URL_GUIDE_BAN}|こちら>から",
            },
        }
        sender_serializer_data = UserSerializer(self.sender)
        return {
            "username": f"【{inappropriate_type_label[self.inappropriate_type]}】不適切アラート",
            "icon_emoji": inappropriate_type_icon[self.inappropriate_type],
            "text": main_text,
            "attachments": [
                {
                    "pretext": pretext[self.inappropriate_type],
                    "fallback": fallback[self.inappropriate_type],
                    "color": attachment_color[self.inappropriate_type],
                    "author_name": f"{self.sender}",
                    "author_link": f"{gene_account_admin_url(self.sender.id)}",
                    "author_icon": sender_serializer_data.data["image"],
                    "title": "",
                    "title_link": "",
                    "text": "",
                    "image_url": "",
                    "fields": [
                        {"title": "【メッセージ内容】", "value": f"{self.message_text}"},
                        {
                            "title": f"【{inappropriate_type_label[self.inappropriate_type]}ワード】",
                            "value": f"{self.inappropriate_word_text}",
                        },
                        {
                            "title": "【メッセージ一覧】",
                            "value": f"<{gene_messages_admin_url(self.room.id, self.message_id)}|{self.room}>",
                        },
                        guide_attachment_field[self.inappropriate_type],
                    ],
                    "thumb_url": "",
                    "footer": "",
                    "footer_icon": "",
                    "mrkdwn_in": ["text"],
                }
            ],
        }

    @classmethod
    def create(
        cls,
        sender,
        room,
    ):

        if not sender:
            raise ValueError("送信者は必須パラメータです")

        if not room:
            raise ValueError("ルームは必須パラメータです")

        return InappropriateAlertSlackSender(
            sender,
            room,
        )

    def send_inappropriate_alert(
        self,
        inappropriate_type,
        message_text,
        message_id,
        inappropriate_word_text,
    ):
        if (
            inappropriate_type != InappropriateType.TABOO
            and inappropriate_type != InappropriateType.WARNING
        ):
            raise ValueError("安全なメッセージをアラートする必要はありません")

        if not message_text:
            raise ValueError("メッセージは必須パラメータです")

        if not inappropriate_word_text:
            raise ValueError("不適切ワードは必須パラメータです")

        self.inappropriate_type = inappropriate_type
        self.message_text = message_text
        self.message_id = message_id
        self.inappropriate_word_text = inappropriate_word_text
        self.update_settings()

        self.send()
