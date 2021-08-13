def calc_exp(me, target_user):
    """
    得られる経験値を計算
    """
    exp = 0
    default_exp = 2

    # 通常
    exp += default_exp

    # ブロックされていたら経験値0
    if me in target_user.blocked_accounts.all():
        exp = 0
        return exp

    # また話したいリスト追加で経験値2倍
    if me in target_user.favorite_users.all():
        exp *= 2

    return exp


def do_when_leveled_up(level, me):
    """
    レベルアップ時に1度だけ実行される処理.
    """
    if level == 2:
        # Lv.2になった時の処理
        me.limit_participate = 2
        me.save()
    elif level == 3:
        pass


def level_up(current_total_exp, earned_exp, me):
    """
    過去獲得した総経験値と今回の獲得経験値を受け取り, レベルアップ処理を行う.
    return { result_level_up: "STABLE" | "LEVELED_UP", current_level: int }
    """
    if current_total_exp < 0 or type(current_total_exp) != int:
        raise ValueError("current_total_expは0以上の整数である必要があります")
    if earned_exp < 0 or type(earned_exp) != int:
        raise ValueError("earned_expは0以上の整数である必要があります")

    (
        current_level,
        required_exp_next_level,
        exp_in_current_level,
    ) = get_current_level_info(current_total_exp)

    # 次のレベルまであと〇〇経験値
    exp_to_go_until_next_level = required_exp_next_level - exp_in_current_level
    if earned_exp >= exp_to_go_until_next_level:
        # レベルアップした
        (
            current_level__after_leveled_up,
            required_exp_next_level__after_leveled_up,
            exp_in_current_level__after_leveled_up,
        ) = get_current_level_info(current_total_exp + earned_exp)

        # レベルアップ時処理. ex) Lv.1 => Lv.3になった時, 2, 3を実行.
        for _level in range(current_level + 1, current_level__after_leveled_up + 1):
            do_when_leveled_up(_level, me)
        return {
            "result_level_up": "LEVELED_UP",
            "current_level": current_level__after_leveled_up,
        }
    else:
        return {"result_level_up": "STABLE", "current_level": current_level}


def get_current_level_info(total_exp):
    """
    総経験値から
    1. 現在のレベル (current_level)
    2. 次レベルまでの総必要経験値 (required_exp_next_level)
    3. 現在のレベルになってからの取得経験値 (exp_in_current_level)
    を返す.
    経験値計算手法はポケモンの100万タイプを採用 (https://wiki.xn--rckteqa2e.com/wiki/%E7%B5%8C%E9%A8%93%E5%80%A4%E3%82%BF%E3%82%A4%E3%83%97#100.E4.B8.87.E3.82.BF.E3.82.A4.E3.83.97)

    ex) get_current_level_info(5) => (2, 8, 4)
    """
    current_level = 1  # 現在のレベル
    required_exp_next_level = 0  # 次レベルまでの総必要経験値
    exp_in_current_level = 0  # 現在のレベルになってからの取得経験値

    if total_exp < 0 or type(total_exp) != int:
        raise ValueError("total_expは0以上の整数である必要があります")

    _total_required_exp = 0
    while total_exp >= _total_required_exp:
        required_exp_next_level = (current_level + 1) ** 3
        _total_required_exp += required_exp_next_level
        if total_exp < _total_required_exp:
            _prev_total_required_exp = (
                _total_required_exp - required_exp_next_level
            )  # 1つ前の_total_required_exp
            exp_in_current_level = total_exp - _prev_total_required_exp
            break
        else:
            current_level += 1
            continue

    return current_level, required_exp_next_level, exp_in_current_level
