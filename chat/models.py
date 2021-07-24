import uuid
from django.db import models
from django.utils import timezone
from stdimage.models import StdImageField
from random import choice


class RoomV4(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "ルーム"
        ordering = ["-created_at"]

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.owner})"
        else:
            return f"無名ルーム ({self.owner})"

    def get_upload_to(instance, filename):
        media_dir_1 = str(instance.id)
        return "room_images/{0}/{1}".format(media_dir_1, filename)

    def get_default_image():
        if DefaultRoomImage.objects.all().exists():
            pks = DefaultRoomImage.objects.values_list("pk", flat=True)
            random_pk = choice(pks)
            return random_pk
        else:
            return

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(verbose_name="ルーム名", max_length=60, blank=True, default="")
    image = StdImageField(
        verbose_name="ルーム画像",
        upload_to=get_upload_to,
        blank=True,
        null=True,
        variations={
            "large": (600, 600, True),
            "thumbnail": (100, 100, True),
            "medium": (250, 250, True),
        },
    )
    default_image = models.ForeignKey(
        "chat.DefaultRoomImage",
        verbose_name="デフォルトルーム画像",
        on_delete=models.PROTECT,
        null=True,
        default=get_default_image,
    )
    owner = models.ForeignKey(
        "account.Account", verbose_name="作成者", on_delete=models.CASCADE
    )
    participants = models.ManyToManyField(
        "account.Account",
        verbose_name="参加者",
        blank=True,
        symmetrical=False,
        related_name="room_participants",
    )
    left_members = models.ManyToManyField(
        "account.Account",
        verbose_name="退室したメンバー(作成者含む)",
        blank=True,
        symmetrical=False,
        related_name="room_left_members",
    )
    closed_members = models.ManyToManyField(
        "account.Account",
        verbose_name="クローズ(フロントから完全削除)したメンバー(作成者含む)",
        blank=True,
        symmetrical=False,
        related_name="room_closed_members",
    )
    max_num_participants = models.IntegerField(verbose_name="可能参加者数", default=1)
    is_exclude_different_gender = models.BooleanField(
        verbose_name="異性を禁止", default=False
    )
    is_private = models.BooleanField(verbose_name="プライベートルーム", default=False)
    created_at = models.DateTimeField(verbose_name="作成時間", default=timezone.now)
    is_end = models.BooleanField(verbose_name="終了状態", default=False)  # 1人でも退室したらTrue
    is_active = models.BooleanField(
        verbose_name="アクティブ状態", default=True
    )  # 全員クローズしたらFalse


class MessageV4(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "メッセージ"
        ordering = ["-time"]

    def __str__(self):
        return "{}({})".format(str(self.room), self.time)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    room = models.ForeignKey(
        RoomV4, verbose_name="チャットルーム", related_name="message", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        "account.Account", verbose_name="投稿者", on_delete=models.PROTECT
    )
    stored_on_participants = models.ManyToManyField(
        "account.Account",
        verbose_name="保存済み参加者",
        blank=True,
        symmetrical=False,
        related_name="message_stored_on_participants",
    )
    read_participants = models.ManyToManyField(
        "account.Account",
        verbose_name="既読済み参加者",
        blank=True,
        symmetrical=False,
        related_name="message_read_participants",
    )
    text = models.TextField(verbose_name="メッセージ内容", max_length=1000, blank=True)
    time = models.DateTimeField(verbose_name="投稿時間", default=timezone.now)
    is_leave_message = models.BooleanField(verbose_name="退室メッセージ", default=False)


class DefaultRoomImage(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "デフォルトルーム画像"
        ordering = ["file_name"]

    def __str__(self):
        return f"{self.file_name}"

    def get_upload_to(self, filename):
        media_dir_1 = str(self.id)
        return "default_room_images/{0}/{1}".format(media_dir_1, filename)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    file_name = models.CharField(
        verbose_name="ファイル名", max_length=100, blank=True, default=""
    )
    image = StdImageField(
        verbose_name="ルーム画像",
        upload_to=get_upload_to,
        blank=True,
        null=True,
        variations={
            "large": (600, 600, True),
            "thumbnail": (100, 100, True),
            "medium": (250, 250, True),
        },
    )


class TalkStatus(models.TextChoices):
    """not used"""

    TALKING = "talking", "会話中"
    WAITING = "waiting", "待機中"
    STOPPING = "stopping", "停止中"
    FINISHING = "finishing", "終了中"
    APPROVING = "approving", "承認中"


class TalkTicket(models.Model):
    """not used"""

    class Meta:
        verbose_name = verbose_name_plural = "旧トークチケット"
        unique_together = ("owner", "worry")

    def __str__(self):
        alert_msg = "【削除】 " if not self.is_active else ""
        return "{}{}-{}-{}".format(
            alert_msg, self.owner.username, self.worry.label, self.status
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner = models.ForeignKey(
        "account.Account", verbose_name="所持者", on_delete=models.CASCADE
    )
    worry = models.ForeignKey(
        "account.GenreOfWorries", verbose_name="悩み", on_delete=models.CASCADE
    )
    topic = models.CharField(verbose_name="話題", max_length=250, blank=True)
    is_speaker = models.BooleanField(verbose_name="話し手希望", default=True)
    status = models.CharField(
        verbose_name="状態",
        max_length=100,
        choices=TalkStatus.choices,
        default=TalkStatus.STOPPING,
    )
    wait_start_time = models.DateTimeField(verbose_name="待機開始時間", default=timezone.now)

    can_talk_heterosexual = models.BooleanField(verbose_name="異性との相談を許可", default=True)
    can_talk_different_job = models.BooleanField(
        verbose_name="異職業との相談を許可", default=True
    )
    is_active = models.BooleanField(verbose_name="アクティブ状態", default=True)


class TalkingRoom(models.Model):
    """not used"""

    class Meta:
        verbose_name = verbose_name_plural = "旧ルーム"
        ordering = ["-started_at"]

    def __str__(self):
        alert_msg = "【終了】 " if self.is_end else ""
        return "{}{} - {}({})".format(
            alert_msg,
            self.speaker_ticket.owner.username,
            self.listener_ticket.owner.username,
            self.speaker_ticket.worry.label,
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    speaker_ticket = models.ForeignKey(
        "chat.TalkTicket",
        verbose_name="話し手talkTicket",
        on_delete=models.CASCADE,
        related_name="speaker_ticket_talking_room",
        null=True,
    )
    listener_ticket = models.ForeignKey(
        "chat.TalkTicket",
        verbose_name="聞き手talkTicket",
        on_delete=models.CASCADE,
        related_name="listener_ticket_talking_room",
        null=True,
    )
    started_at = models.DateTimeField(verbose_name="トーク開始時間", default=timezone.now)
    is_alert = models.BooleanField(verbose_name="アラート済み", default=False)
    is_end = models.BooleanField(verbose_name="トーク終了状況", default=False)
    ended_at = models.DateTimeField(verbose_name="トーク終了時間", null=True)
    is_time_out = models.BooleanField(verbose_name="トーク終了理由(time out)", default=False)


class MessageV2(models.Model):
    """not used"""

    class Meta:
        verbose_name = verbose_name_plural = "旧メッセージ"
        ordering = ["-time"]

    def __str__(self):
        return "{}({})".format(str(self.room), self.time)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    room = models.ForeignKey(
        TalkingRoom,
        verbose_name="チャットルーム",
        related_name="message",
        on_delete=models.CASCADE,
    )
    content = models.TextField(verbose_name="メッセージ内容", max_length=1000, blank=True)
    time = models.DateTimeField(verbose_name="投稿時間", default=timezone.now)
    user = models.ForeignKey(
        "account.Account", verbose_name="投稿者", on_delete=models.CASCADE
    )
    is_stored_on_speaker = models.BooleanField(verbose_name="話し手側の保存状況", default=False)
    is_stored_on_listener = models.BooleanField(verbose_name="聞き手側の保存状況", default=False)
    is_read_speaker = models.BooleanField(verbose_name="話し手側の既読状況", default=False)
    is_read_listener = models.BooleanField(verbose_name="聞き手側の既読状況", default=False)


class Room(models.Model):
    """not used. only use v1"""

    def __str__(self):
        return "{} - {}".format(self.request_user.username, self.response_user.username)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    request_user = models.ForeignKey(
        "account.Account",
        verbose_name="リクエストユーザ",
        on_delete=models.CASCADE,
        related_name="request_room",
    )
    response_user = models.ForeignKey(
        "account.Account",
        verbose_name="レスポンスユーザ",
        on_delete=models.CASCADE,
        related_name="response_room",
    )
    created_at = models.DateTimeField(verbose_name="作成時間", default=timezone.now)
    is_start = models.BooleanField(verbose_name="トーク開始状況", default=False)
    started_at = models.DateTimeField(verbose_name="トーク開始時間", null=True)
    is_alert = models.BooleanField(verbose_name="アラート済み", default=False)
    is_end = models.BooleanField(verbose_name="トーク終了状況", default=False)
    ended_at = models.DateTimeField(verbose_name="トーク終了時間", null=True)
    is_time_out = models.BooleanField(verbose_name="トーク終了理由(time out)", default=False)
    is_end_request = models.BooleanField(verbose_name="リクエストユーザ側のend状況", default=False)
    is_end_response = models.BooleanField(verbose_name="レスポンスユーザ側のend状況", default=False)
    is_closed_request = models.BooleanField(
        verbose_name="リクエストユーザ側のclose状況", default=False
    )
    is_closed_response = models.BooleanField(
        verbose_name="レスポンスユーザ側のclose状況", default=False
    )
    is_worried_request_user = models.BooleanField(
        verbose_name="リクエストユーザが相談者である", default=True
    )


class Message(models.Model):
    """not used. only use v1"""

    def __str__(self):
        return "{}({})".format(str(self.room), self.time)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    room = models.ForeignKey(
        Room, verbose_name="チャットルーム", related_name="message", on_delete=models.CASCADE
    )
    content = models.TextField(verbose_name="メッセージ内容", max_length=1000, blank=True)
    time = models.DateTimeField(verbose_name="投稿時間", default=timezone.now)
    user = models.ForeignKey(
        "account.Account", verbose_name="投稿者", on_delete=models.CASCADE
    )
    is_stored_on_request = models.BooleanField(
        verbose_name="リクエストユーザ側の保存状況", default=False
    )
    is_stored_on_response = models.BooleanField(
        verbose_name="レスポンスユーザ側の保存状況", default=False
    )


class Worry(models.Model):
    """not used. only use v1"""

    class Meta:
        ordering = ["-time"]

    def __str__(self):
        return "{}".format(self.message)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    time = models.DateTimeField(verbose_name="投稿時間", default=timezone.now)
    message = models.TextField(verbose_name="メッセージ内容", max_length=280, blank=True)
    user = models.ForeignKey(
        "account.Account", verbose_name="投稿者", on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)
