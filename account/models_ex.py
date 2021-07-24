from account.models import Account


class AccountEx(Account):
    class Meta:
        proxy = True

    @classmethod
    def increment_num_of_talk(cls, account, room):
        """
        トーク完了後に実行.
        オーナーであればnum_of_ownerを, 参加者であればnum_of_participatedをインクリメント.
        """
        if account.id == room.owner.id:
            account.num_of_owner += 1
            account.save()
            return
        elif account.id in room.participants.all().values_list("id", flat=True):
            account.num_of_participated += 1
            account.save()
            return
