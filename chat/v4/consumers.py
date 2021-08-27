from fullfii.lib.authSupport import authenticate_jwt
import traceback
import uuid
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
import json
from channels.layers import get_channel_layer
from django.utils import timezone
from fullfii.lib.inappropriate_checker import (
    InappropriateMessageChecker,
    InappropriateType,
)
from main.v4.consumers import JWTAsyncWebsocketConsumer
from chat.models import RoomV4, MessageV4
from chat.v4.serializers import MessageSerializer, RoomSerializer
from fullfii.lib.firebase import send_fcm


class ChatConsumer(JWTAsyncWebsocketConsumer):
    groups = ["broadcast"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = (
            self.scope["url_route"]["kwargs"]["room_id"]
            if "room_id" in self.scope["url_route"]["kwargs"]
            else ""
        )
        self.inappropriate_checker = None
        self.inappropriate_words_csv_path = (
            "fullfii/lib/inappropriate_checker/inappropriate_words.csv"
        )

    @classmethod
    def get_group_name(cls, _id):
        return "room_{}".format(str(_id))

    async def receive_auth(self, received_data):
        """
        received_data: {'type': 'auth', 'token': token}

        return {
            'type': 'auth',
            'room_id': room_id,
            'not_stored_messages': [],
            'is_already_ended': False,
        }
        """

        self.group_name = self.get_group_name(self.room_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        me = await authenticate_jwt(received_data["token"], is_async=True)
        if me is None:
            # 401 Unauthorized
            await self.disconnect(4001)
            print("401 Unauthorized")
            return
        self.me_id = me.id

        auth_response_data = {
            "type": "auth",
            "room_id": str(self.room_id),
            "room": None,
            "not_stored_messages": [],
            "is_already_ended": False,
        }

        room = await self.get_room()
        if room:
            # Messages that you haven't stored yet include in auth send.
            not_stored_messages_data = await self.get_not_stored_messages_data(me, room)
            if not_stored_messages_data:
                auth_response_data["not_stored_messages"] = not_stored_messages_data

            # If the talk has already ended, notice. (通常、アプリがquit間にトークの開始・終了が行われた時)
            is_already_ended = room.is_end
            if is_already_ended:
                auth_response_data["is_already_ended"] = is_already_ended

            auth_response_data["room"] = await self.get_room_data(room, me)

            # 不適切チェッカー
            self.inappropriate_checker = await self.create_inappropriate_checker(
                me, room
            )

        elif room == 0:
            # マッチング直後にchat wsコネクションを試みたとき(マッチング時にアプリを開いていた時)
            # roomをcreateした直後にself.get_room()した場合、roomがdoesNotExist判定になる(↓参考)
            # https://github.com/django/channels/issues/1110
            pass
            # self.is_speaker = received_data['is_speaker'] if 'is_speaker' in received_data else True
        else:
            await self.close()
            print("room error.")
            return

        await self.send(text_data=json.dumps(auth_response_data))
        return True

    async def _receive(self, received_data):
        received_type = received_data["type"]

        if received_type == "chat_message":
            if "message_id" in received_data and "text" in received_data:
                message_id = received_data["message_id"]
                text = received_data["text"]
                time = timezone.datetime.now()

                me = await self.get_user(self.me_id)

                # 不適切チェック
                if self.inappropriate_checker is not None:
                    result = await self.check_inappropriate_word(text, message_id)
                    # タブーだった場合, 凍結処理
                    if result == InappropriateType.TABOO:
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type": "chat_taboo_message",
                                    "room_id": str(self.room_id),
                                    "message_id": message_id,
                                }
                            )
                        )
                        await self.ban_me(me)
                        return

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat_message",
                        "message_id": message_id,
                        "text": text,
                        "sender_id": str(me.id),
                        "time": time.strftime("%Y/%m/%d %H:%M:%S"),
                    },
                )
                await self.create_message(message_id, text, time, me)

                room = await self.get_room()
                if room:
                    # send fcm(SEND_MESSAGE)
                    receiver_list = await self.get_receiver_list(sender=me, room=room)
                    for receiver in receiver_list:
                        await send_fcm(
                            receiver,
                            {
                                "type": "SEND_MESSAGE_V4",
                                "sender": me,
                                "text": text,
                            },
                        )
            else:
                # chat_message送信失敗
                pass

        elif received_type == "store":
            if "message_id" in received_data:
                message_id = received_data["message_id"]

                me = await self.get_user(self.me_id)
                await self.turn_on_message_stored(me, message_id=message_id)
            else:
                # store 失敗
                pass

        elif received_type == "store_by_room":
            me = await self.get_user(self.me_id)
            await self.turn_on_message_stored(me, room_id=self.room_id)

        # フロントで既読処理が走った際に送信される
        elif received_type == "read":
            me = await self.get_user(self.me_id)
            await self.turn_on_read_all_messages(me=me, room_id=self.room_id)

    async def chat_message(self, event):
        try:
            message_id = event["message_id"]
            text = event["text"]
            sender_id = event["sender_id"]
            time = event["time"]

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "chat_message",
                        "room_id": str(self.room_id),
                        # serializerを参考に ↓
                        "message": {
                            "id": message_id,
                            "text": text,
                            "sender_id": sender_id,
                            "time": time,
                        },
                    }
                )
            )
        except Exception as e:
            traceback.print_exc()

    async def end_talk(self, event):
        try:
            data = {"type": "end_talk"}
            room = await self.get_room()
            me = await self.get_user(self.me_id)
            room_data = await self.get_room_data(room, me)
            appended_data = {"room": room_data}
            data.update(appended_data)
            await self.send(text_data=json.dumps(data))
        except Exception as e:
            traceback.print_exc()

    @database_sync_to_async
    def get_room(self):
        rooms = RoomV4.objects.filter(id=self.room_id)
        if rooms.count() == 1:
            return rooms.first()
        elif rooms.count() == 0:
            return 0
        else:
            return

    @database_sync_to_async
    def ban_me(self, me):
        me.is_ban = True
        me.save()

    @database_sync_to_async
    def create_inappropriate_checker(self, me, room):
        return InappropriateMessageChecker.create(
            self.inappropriate_words_csv_path,
            sender=me,
            room=room,
        )

    @database_sync_to_async
    def check_inappropriate_word(self, text, message_id):
        return self.inappropriate_checker.check(text, message_id, shouldSendSlack=True)

    @database_sync_to_async
    def get_room_data(self, room, me):
        return RoomSerializer(room, context={"me": me}).data

    @database_sync_to_async
    def get_receiver_list(self, sender, room):
        receiver_list = []

        # owner
        if sender.id != room.owner.id:
            receiver_list.append(room.owner)

        # participants
        for participant in room.participants.all():
            if sender.id != participant.id:
                receiver_list.append(participant)

        return receiver_list

    @database_sync_to_async
    def create_message(self, message_id, text, time, me):
        try:
            room = RoomV4.objects.get(id=self.room_id)
            MessageV4.objects.create(
                id=message_id,
                room=room,
                sender=me,
                text=text,
                time=time,
            )
        except Exception as e:
            traceback.print_exc()

    @database_sync_to_async
    def turn_on_read_all_messages(self, me, room_id):
        """
        message.read_participants更新
        """
        try:
            messages = MessageV4.objects.filter(room__id=room_id).exclude(
                read_participants=me.id
            )
            for message in messages:
                message.read_participants.add(me)
        except:
            traceback.print_exc()

    @database_sync_to_async
    def turn_on_message_stored(self, me, message_id=None, room_id=None):
        """
        message.stored_on_participants更新
        引数message_idを指定した場合、message単位で更新
        引数room_idを指定した場合、room単位で更新
        """
        try:
            if message_id:  # for one message
                message = MessageV4.objects.get(id=message_id)
                message.stored_on_participants.add(me)

            elif room_id:  # for all messages in the room
                messages = MessageV4.objects.filter(room__id=room_id).exclude(
                    stored_on_participants=me.id
                )
                for message in messages:
                    message.stored_on_participants.add(me)
        except Exception as e:
            traceback.print_exc()

    @database_sync_to_async
    def get_not_stored_messages_data(self, me, room):
        try:
            messages = (
                MessageV4.objects.filter(room=room)
                .exclude(stored_on_participants=me.id)
                .order_by("time")
            )
            return MessageSerializer(messages, many=True).data
        except Exception as e:
            traceback.print_exc()

    @classmethod
    def send_end_talk(cls, room_id):
        group_name = cls.get_group_name(room_id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "end_talk",
            },
        )

    @classmethod
    def send_leave_message(cls, room_id, text, sender):
        message_id = uuid.uuid4()
        time = timezone.datetime.now()

        try:
            room = RoomV4.objects.get(id=room_id)
            MessageV4.objects.create(
                id=message_id,
                room=room,
                sender=sender,
                text=text,
                time=time,
                is_leave_message=True,
            )
            group_name = cls.get_group_name(room_id)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "chat_message",
                    "message_id": str(message_id),
                    "text": text,
                    "sender_id": str(sender.id),
                    "time": time.strftime("%Y/%m/%d %H:%M:%S"),
                },
            )
        except Exception as e:
            traceback.print_exc()
