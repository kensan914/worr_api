import os


def clean_text(text):
    text = text.replace("\n", "")
    text = text.replace(" ", "")
    text = text.replace("\t", "")
    return text


def calc_file_num(dir_path):
    return sum(
        os.path.isfile(os.path.join(dir_path, name)) for name in os.listdir(dir_path)
    )


def check_is_maintaining(BASE_DIR):
    """
    メンテナンス状況の取得
    :return: true(メンテナンス中) false(メンテナンスしていない)
    """
    f = open("{}/config/maintenance_mode_state.txt".format(BASE_DIR))
    mode_state = clean_text(f.read())
    f.close()
    return mode_state == "1"
