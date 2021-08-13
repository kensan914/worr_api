from account.models import Account
from fullfii.lib.exp_calculator import calc_exp, level_up


class AccountEx(Account):
    class Meta:
        proxy = True

    @classmethod
    def increment_num_of_talk(cls, me, room):
        """
        トーク完了後に実行.
        オーナーであればnum_of_ownerを, 参加者であればnum_of_participatedをインクリメント.
        """
        if me.id == room.owner.id:
            me.num_of_owner += 1
            me.save()
            return
        elif me.id in room.participants.all().values_list("id", flat=True):
            me.num_of_participated += 1
            me.save()
            return

    @classmethod
    def give_exp(cls, me, room):
        """
        トーク完了後に実行.
        経験値を計算し, 付与する. レベルアップ状況を返す.
        """
        if me.level >= 2:  # HACK: Beta版でレベル上限が2
            return {"result_level_up": "STABLE", "current_level": me.level}, me

        if me.id == room.owner.id:
            target_user = room.participants.first()  # HACK:
        else:
            target_user = room.owner

        exp_this_time = calc_exp(me, target_user)
        result = level_up(me.exp, exp_this_time, me)

        me.exp += exp_this_time
        me.level = result["current_level"]
        me.save()

        return result, me
