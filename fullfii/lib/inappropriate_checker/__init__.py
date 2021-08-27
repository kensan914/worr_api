from enum import Enum
from fullfii.lib.csv_handlers import fetch_csv_as_dict
from fullfii.lib.jaconv import optimize_text


class InappropriateType(Enum):
    TABOO = "taboo"  # タブー
    WARNING = "warning"  # 警告
    SAFE = "safe"  # 安全


def search_some_words(message, word_list):
    for word in word_list:
        if word in message:
            return word
        else:
            continue
    return False


from fullfii.lib.slack import (
    InappropriateMessageAlertSlackSender,
    InappropriateRoomNameAlertSlackSender,
)


class InappropriateChecker:
    def __init__(self, _taboo_word_list, _warning_word_list):
        self.taboo_word_list = _taboo_word_list
        self.warning_word_list = _warning_word_list
        self.inappropriate_alert_slack_sender = None

    @classmethod
    def validate_inappropriate_words_csv(cls, inappropriate_words_csv_path):
        inappropriate_words_dict = fetch_csv_as_dict(inappropriate_words_csv_path)
        if not "taboo" in inappropriate_words_dict:
            raise KeyError("tabooキーが存在しません。inappropriate_words.csvを確認してください。")
        elif not "warning" in inappropriate_words_dict:
            raise KeyError("warningキーが存在しません。inappropriate_words.csvを確認してください。")
        return inappropriate_words_dict

    def check(self, message_text, message_id=None, shouldSendSlack=False):
        optimized_message = optimize_text(message_text)

        # タブー
        result_taboo = search_some_words(optimized_message, self.taboo_word_list)
        if result_taboo:
            # 不適切アラート
            if shouldSendSlack and self.inappropriate_alert_slack_sender is not None:
                self.inappropriate_alert_slack_sender.send_inappropriate_alert(
                    inappropriate_type=InappropriateType.TABOO,
                    message_text=message_text,
                    message_id=message_id,
                    inappropriate_word_text=result_taboo,
                )
            return InappropriateType.TABOO

        # 警告
        result_warning = search_some_words(optimized_message, self.warning_word_list)
        if result_warning:
            # 不適切アラート
            if shouldSendSlack and self.inappropriate_alert_slack_sender is not None:
                self.inappropriate_alert_slack_sender.send_inappropriate_alert(
                    inappropriate_type=InappropriateType.WARNING,
                    message_text=message_text,
                    message_id=message_id,
                    inappropriate_word_text=result_warning,
                )
            return InappropriateType.WARNING

        # 安全
        return InappropriateType.SAFE


class InappropriateMessageChecker(InappropriateChecker):
    def __init__(self, _taboo_word_list, _warning_word_list, _sender, _room):
        super().__init__(_taboo_word_list, _warning_word_list)
        self.inappropriate_alert_slack_sender = (
            InappropriateMessageAlertSlackSender.create(
                sender=_sender,
                room=_room,
            )
        )

    @classmethod
    def create(cls, inappropriate_words_csv_path, sender, room):
        inappropriate_words_dict = cls.validate_inappropriate_words_csv(
            inappropriate_words_csv_path
        )
        return InappropriateMessageChecker(
            _taboo_word_list=inappropriate_words_dict["taboo"],
            _warning_word_list=inappropriate_words_dict["warning"],
            _sender=sender,
            _room=room,
        )


class InappropriateRoomNameChecker(InappropriateChecker):
    def __init__(self, _taboo_word_list, _warning_word_list, _sender):
        super().__init__(_taboo_word_list, _warning_word_list)
        self.inappropriate_alert_slack_sender = (
            InappropriateRoomNameAlertSlackSender.create(
                sender=_sender,
            )
        )

    @classmethod
    def create(cls, inappropriate_words_csv_path, sender):
        inappropriate_words_dict = cls.validate_inappropriate_words_csv(
            inappropriate_words_csv_path
        )
        return InappropriateRoomNameChecker(
            _taboo_word_list=inappropriate_words_dict["taboo"],
            _warning_word_list=inappropriate_words_dict["warning"],
            _sender=sender,
        )
