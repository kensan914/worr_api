from django.contrib import admin

from fullfii.lib.constants import gene_messages_admin_url
from .models import *
from django.utils.html import format_html


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "label",
        "order",
    )


@admin.register(RoomV4)
class RoomV4Admin(admin.ModelAdmin):
    list_display = (
        "name",
        "format_to_admin_messages",
        "format_image",
        "format_default_image",
        "owner",
        "format_participants",
        "format_left_members",
        "format_closed_members",
        "is_speaker",
        "is_exclude_different_gender",
        "is_private",
        "created_at",
        "format_is_talking",
        "is_active",
    )
    list_display_links = ("name",)
    search_fields = ("owner__username",)
    date_hierarchy = "created_at"
    list_filter = (
        "is_end",
        "is_active",
    )
    raw_id_fields = ("owner", "participants", "left_members", "closed_members")

    def format_to_admin_messages(self, obj):
        if obj.participants.all().exists():
            messages = MessageV4.objects.filter(room=obj)
            return format_html(
                '<a href={} target="_blank">メッセージ一覧（{}）</a>',
                gene_messages_admin_url(obj.id),
                messages.count(),
            )
        else:
            return format_html(
                "<p>まだ参加者がいません</p>",
            )

    format_to_admin_messages.short_description = "メッセージ一覧リンク"

    def format_participants(self, obj):
        participants_usernames = [
            str(participant) for participant in obj.participants.all()
        ]
        return "・".join(participants_usernames)

    format_participants.short_description = "参加者"
    format_participants.admin_order_field = "participants"

    def format_left_members(self, obj):
        left_members_usernames = [
            str(left_member) for left_member in obj.left_members.all()
        ]
        return "・".join(left_members_usernames)

    format_left_members.short_description = "退室したメンバー(作成者含む)"
    format_left_members.admin_order_field = "left_members"

    def format_closed_members(self, obj):
        closed_members_usernames = [
            str(closed_member) for closed_member in obj.closed_members.all()
        ]
        return "・".join(closed_members_usernames)

    format_closed_members.short_description = "クローズ(フロントから完全削除)したメンバー(作成者含む)"
    format_closed_members.admin_order_field = "closed_members"

    def format_image(self, obj):
        if obj.image:
            return format_html(
                '<a href={} target="_blank"><img src="{}" width="100" style="border-radius: 8px" /></a>',
                obj.image.url,
                obj.image.large.url,
            )

    format_image.short_description = "ルーム画像"
    format_image.empty_value_display = "No image"

    def format_default_image(self, obj):
        if obj.default_image:
            return format_html(
                '<a href={} target="_blank"><img src="{}" width="100" style="border-radius: 8px" /></a>',
                obj.default_image.image.url,
                obj.default_image.image.large.url,
            )

    format_default_image.short_description = "デフォルトルーム画像"
    format_default_image.empty_value_display = "No image"

    def format_is_talking(self, obj):
        return not obj.is_end

    format_is_talking.boolean = True
    format_is_talking.short_description = "会話中"
    format_is_talking.empty_value_display = "未設定"


@admin.register(MessageV4)
class MessageV4Admin(admin.ModelAdmin):
    list_display = (
        "text",
        "sender",
        "format_room",
        "time",
        "format_stored_on_participants",
        "format_read_participants",
    )
    list_display_links = ("text",)
    raw_id_fields = (
        "room",
        "sender",
        "stored_on_participants",
        "read_participants",
    )
    search_fields = ("sender__username",)
    date_hierarchy = "time"
    list_filter = ("is_leave_message",)

    def format_room(self, obj):
        max_room_name_length = 15
        room_name_label = obj.room.name
        if len(obj.room.name) > max_room_name_length:
            room_name_label = f"{obj.room.name[:max_room_name_length]}..."
        elif len(obj.room.name) <= 0:
            room_name_label = "無名ルーム"

        return f"{room_name_label} ({obj.room.owner})"

    format_room.short_description = "チャットルーム"
    format_room.admin_order_field = "room"

    def format_stored_on_participants(self, obj):
        participants_usernames = [
            str(participant) for participant in obj.stored_on_participants.all()
        ]
        return "・".join(participants_usernames)

    format_stored_on_participants.short_description = "保存済み参加者"
    format_stored_on_participants.admin_order_field = "stored_on_participants"

    def format_read_participants(self, obj):
        participants_usernames = [
            str(participant) for participant in obj.read_participants.all()
        ]
        return "・".join(participants_usernames)

    format_read_participants.short_description = "既読済み参加者"
    format_read_participants.admin_order_field = "read_participants"


@admin.register(DefaultRoomImage)
class DefaultRoomImageAdmin(admin.ModelAdmin):
    list_display = (
        "format_image",
        "file_name",
    )
    list_display_links = ("format_image",)

    def format_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" style="border-radius: 8px" />', obj.image.url
            )

    format_image.short_description = "デフォルトルーム画像"
    format_image.empty_value_display = "No image"


@admin.register(TalkTicket)
class TalkTicketAdmin(admin.ModelAdmin):
    list_display = (
        "format_to_detail",
        "owner",
        "worry",
        "format_status",
        "wait_start_time",
        "is_speaker",
        "can_talk_heterosexual",
        "can_talk_different_job",
        "is_active",
    )
    list_display_links = ("format_to_detail",)
    search_fields = ("owner__username",)
    date_hierarchy = "wait_start_time"
    list_filter = (
        "worry",
        "is_speaker",
        "status",
        "can_talk_heterosexual",
        "can_talk_different_job",
        "is_active",
    )
    # filter_horizontal = ('genre_of_worries',
    #                      'blocked_accounts', 'talked_accounts')
    raw_id_fields = ("owner",)

    def format_to_detail(self, obj):
        return "詳細"

    format_to_detail.short_description = "詳細"

    def format_status(self, obj):
        if obj.status:
            backgroundColor = "white"
            talk_status = TalkStatus(obj.status)
            if talk_status.name == "TALKING":
                backgroundColor = "palegreen"
            elif talk_status.name == "WAITING":
                backgroundColor = "lightskyblue"
            elif talk_status.name == "STOPPING":
                backgroundColor = "salmon"
            elif talk_status.name == "FINISHING":
                backgroundColor = "gold"
            elif talk_status.name == "APPROVING":
                backgroundColor = "mediumorchid"

            return format_html(
                '<div style="background-color: {}; text-align: center; border-radius: 8px; padding-left: 2px; padding-right: 2px;">{}</div>',
                backgroundColor,
                talk_status.label,
            )
        else:
            return "No status"

    format_status.short_description = "状態"
    format_status.admin_order_field = "status"


@admin.register(TalkingRoom)
class TalkingRoomAdmin(admin.ModelAdmin):
    list_display = (
        "format_to_detail",
        "format_speaker_ticket",
        "format_listener_ticket",
        "started_at",
        "ended_at",
        "is_end",
        "is_alert",
        "is_time_out",
    )
    list_display_links = ("format_to_detail",)
    search_fields = (
        "speaker_ticket__owner__username",
        "listener_ticket__owner__username",
    )
    date_hierarchy = "started_at"
    list_filter = (
        "is_end",
        "is_alert",
        "is_time_out",
    )
    raw_id_fields = ("speaker_ticket", "listener_ticket")

    def format_to_detail(self, obj):
        return "詳細"

    format_to_detail.short_description = "詳細"

    def format_speaker_ticket(self, obj):
        if obj.speaker_ticket:
            return obj.speaker_ticket.owner.username
        else:
            return "No speaker"

    format_speaker_ticket.short_description = "話し手"
    format_speaker_ticket.admin_order_field = "speaker_ticket"

    def format_listener_ticket(self, obj):
        if obj.listener_ticket:
            return obj.listener_ticket.owner.username
        else:
            return "No listener"

    format_listener_ticket.short_description = "聞き手"
    format_listener_ticket.admin_order_field = "listener_ticket"


@admin.register(MessageV2)
class MessageV2Admin(admin.ModelAdmin):
    list_display = (
        "format_to_detail",
        "format_chat_composition",
        "time",
        "content",
        "is_stored_on_speaker",
        "is_stored_on_listener",
        "is_read_speaker",
        "is_read_listener",
    )
    list_display_links = ("format_to_detail",)
    raw_id_fields = ("room", "user")
    search_fields = (
        "room__speaker_ticket__owner__username",
        "room__listener_ticket__owner__username",
    )
    date_hierarchy = "time"

    def format_to_detail(self, obj):
        return "詳細"

    format_to_detail.short_description = "詳細"

    def format_chat_composition(self, obj):
        if obj.room and obj.user:
            if obj.room.speaker_ticket.owner.id == obj.user.id:
                return "{}(話し手) ⏩ {}(聞き手)".format(
                    obj.room.speaker_ticket.owner, obj.room.listener_ticket.owner
                )
            elif obj.room.listener_ticket.owner.id == obj.user.id:
                return "{}(聞き手) ⏩ {}(話し手)".format(
                    obj.room.listener_ticket.owner, obj.room.speaker_ticket.owner
                )
