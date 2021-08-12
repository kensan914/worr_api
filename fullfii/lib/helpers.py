from config import settings
from fullfii.lib.utils import check_is_maintaining


def gene_maintenance_message():
    return "実施中" if check_is_maintaining(settings.BASE_DIR) else ""


def convert_querystring_to_list(q_str):
    """
    ex) ',1,2,   3' ===> [1, 2, 3]
    数値に変換できるものは数値に変換し, それ以外は文字列. 空白を除去.
    引数が''(空文字)やundefinedの場合Noneを返す.
    リストの要素が空であるときその要素は削除(',a' => ['a']☚本来['', 'a'])
    """

    split_kw = ","
    if not q_str:
        return []

    not_blank_q_str = q_str.replace(" ", "")
    q_list = not_blank_q_str.split(split_kw)

    def not_empty(str):
        return bool(str)

    not_empty_q_list = list(filter(not_empty, q_list))

    def convert_from_str_to_int(str):
        return int(str) if str.isdecimal() else str

    converted_q_list = list(map(convert_from_str_to_int, not_empty_q_list))

    return converted_q_list
