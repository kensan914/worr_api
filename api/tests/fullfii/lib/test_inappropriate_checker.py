from django.test import TestCase

from account.tests.factories import AccountFactory
from chat.tests.factories import RoomV4Factory
from fullfii.lib.inappropriate_checker import (
    InappropriateMessageChecker,
    InappropriateType,
)


class TestInappropriateChecker(TestCase):
    def setUp(self):
        account_factory = AccountFactory.create()
        room_v4_factory = RoomV4Factory.create()
        self.inappropriate_checker = InappropriateMessageChecker.create(
            "fullfii/lib/inappropriate_checker/test_inappropriate_words.csv",
            sender=account_factory,
            room=room_v4_factory,
        )

    def test_create(self):
        self.assertEquals(
            type(self.inappropriate_checker), InappropriateMessageChecker, msg="型チェック"
        )
        self.assertEquals(
            self.inappropriate_checker.taboo_word_list,
            ["えんじにあ", "社員", "police"],
            msg="tabooチェック",
        )
        self.assertEquals(
            self.inappropriate_checker.warning_word_list,
            ["がーどまん", "銀行員", "firefighter"],
            msg="warningチェック",
        )

    def test_create_error(self):
        with self.assertRaises(KeyError):
            account_factory = AccountFactory.create()
            room_v4_factory = RoomV4Factory.create()
            InappropriateMessageChecker.create(
                "fullfii/lib/inappropriate_checker/test_keyerror_inappropriate_words.csv",
                sender=account_factory,
                room=room_v4_factory,
            )

    def test_check(self):
        taboo_message1 = "私はエンじﾆｱです。"
        taboo_message2 = "私はpoliceです。"
        warning_message1 = "私は銀行員です。"
        warning_message2 = "私はｆiｒeFiｇｈＴerです。"
        safe_message1 = "私はフリーターです。"
        safe_message2 = "私はポリスです。"

        self.assertEquals(
            self.inappropriate_checker.check(taboo_message1),
            InappropriateType.TABOO,
            msg="タブーチェック1",
        )
        self.assertEquals(
            self.inappropriate_checker.check(taboo_message2),
            InappropriateType.TABOO,
            msg="タブーチェック2",
        )
        self.assertEquals(
            self.inappropriate_checker.check(warning_message1),
            InappropriateType.WARNING,
            msg="警告チェック1",
        )
        self.assertEquals(
            self.inappropriate_checker.check(warning_message2),
            InappropriateType.WARNING,
            msg="警告チェック2",
        )
        self.assertEquals(
            self.inappropriate_checker.check(safe_message1),
            InappropriateType.SAFE,
            msg="安全チェック1",
        )
        self.assertEquals(
            self.inappropriate_checker.check(safe_message2),
            InappropriateType.SAFE,
            msg="安全チェック2",
        )
