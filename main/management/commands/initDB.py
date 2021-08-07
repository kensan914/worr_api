from django.core.management.base import BaseCommand
from fullfii import init_chat_tag, init_default_room_image


class Command(BaseCommand):
    help = "デフォルトルーム画像のinit"

    def handle(self, *args, **options):
        init_default_room_image()
        init_chat_tag()
