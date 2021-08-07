import os
from django.core.files.images import ImageFile
from chat.models import DefaultRoomImage, Tag
import glob
import csv


def init_default_room_image():
    files = glob.glob("fullfii/db/images/default_room_images/*")
    for file_path in files:
        file_name = os.path.basename(file_path)
        if DefaultRoomImage.objects.filter(file_name=file_name).exists():
            continue
        default_room_image = DefaultRoomImage(file_name=file_name)
        image = ImageFile(open(file_path, "rb"))
        default_room_image.image.save(file_name, image)
        default_room_image.save()
        print(f"デフォルトルーム画像「{file_name}」が登録されました。")


def init_chat_tag():
    tag_key_list = [
        "key",
        "label",
        "order",
    ]

    fin = open("static/corpus/tagList.csv", "rt", encoding="utf-8")
    tag_csv_list = csv.DictReader(
        fin,
        delimiter=",",
        doublequote=True,
        lineterminator="\r\n",
        quotechar='"',
        skipinitialspace=True,
    )

    for tag_csv in tag_csv_list:
        tag_csv = format_dict_csv(tag_csv, tag_key_list)
        tags = Tag.objects.filter(key=tag_csv["key"])
        if not tags.exists():
            Tag.objects.create(
                key=tag_csv["key"],
                label=tag_csv["label"],
                order=float(tag_csv["order"]),
            )
            print(f'「{tag_csv["label"]}」is registered!')
        else:
            target_tag = tags.first()
            for key, val in tag_csv.items():
                if key == "order":
                    if target_tag.order != float(val):
                        print(f"「{target_tag.label}」の{key}を{float(val)}に変更しました。")
                        target_tag.order = float(val)
                # https://oshiete.goo.ne.jp/qa/8952513.html
                elif target_tag.__dict__[key] != val:
                    print(f"「{target_tag.label}」の{key}を{val}に変更しました。")
                    target_tag.__dict__[key] = val
                target_tag.save()
    fin.close()


def format_dict_csv(dict_csv, key_list):
    keys_with_int_as_value = []
    keys_with_float_as_value = ["order"]

    new_dict_csv = {}
    for key in key_list:
        if key in dict_csv:
            val = dict_csv[key]

            # actually format value
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False

            if key in keys_with_int_as_value:
                val = int(val)

            if key in keys_with_float_as_value:
                val = float(val)

            new_dict_csv[key] = val
        else:
            raise Exception("There is an unexpected key({}) in csv.".format(key))

    return new_dict_csv
