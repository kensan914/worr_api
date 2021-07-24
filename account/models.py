import uuid
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import _user_has_perm
from django.db import models
from django.utils import timezone
from stdimage.models import StdImageField


def get_default_status():
    pass


class AccountManager(BaseUserManager):
    use_in_migration = True

    def _create_user(self, **fields):
        # if not 'id' in fields:
        #     raise ValueError('The given id must be set')
        if not "password" in fields:
            raise ValueError("The given password must be set")
        # fields['email'] = self.normalize_email(fields['email'])
        user = self.model(**fields)
        user.set_password(fields["password"])
        user.save(using=self._db)
        return user

    def create_user(self, **fields):
        fields.setdefault("is_staff", False)
        fields.setdefault("is_superuser", False)
        return self._create_user(**fields)

    def create_superuser(self, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff==True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser==True.")

        return self._create_user(password=password, **extra_fields)


class ParamsModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return "{}.{}".format(self.key, self.label)

    key = models.CharField(verbose_name="キー", max_length=30, unique=True, null=True)
    label = models.CharField(verbose_name="ラベル", max_length=30, null=True)


class Feature(ParamsModel):
    pass


class GenreOfWorries(ParamsModel):
    class Meta:
        verbose_name = verbose_name_plural = "悩みジャンル"

    value = models.CharField(verbose_name="バリュー", max_length=30, null=True)


class ScaleOfWorries(ParamsModel):
    pass


class Status(models.TextChoices):
    TALKING = "talking", "会話中"
    ONLINE = "online", "オンライン"
    OFFLINE = "offline", "オフライン"


class StatusColor(models.TextChoices):
    TALKING = "talking", "gold"
    ONLINE = "online", "mediumseagreen"
    OFFLINE = "offline", "indianred"


class Plan(models.TextChoices):
    """
    ex) Plan(user.plan).name: 'NORMAL', Plan(user.plan).value: 'com.fullfii.fullfii.normal_plan', Plan(user.plan).label: 'ノーマル'
    """

    NORMAL = "com.fullfii.fullfii.normal_plan", "ノーマル"
    FREE = "com.fullfii.fullfii.free_plan", "未加入"


class Gender(models.TextChoices):
    MALE = "male", "男性"
    FEMALE = "female", "女性"
    NOTSET = "notset", "未設定"
    # SECRET = 'secret', '内緒'


class Job(models.TextChoices):
    HS_STUDENT = "hs-student", "高校生"
    COLLEGE_STUDENT = "college-student", "大学生"
    HOUSEWIFE = "housewife", "主婦／主夫"
    WORKER = "worker", "会社員"
    FREETER = "freeter", "フリーター"
    OTHER = "other", "その他"
    SECRET = "secret", "内緒"


class IntroStep(models.Model):
    key = models.CharField(verbose_name="キー", max_length=30)

    def __str__(self):
        return str(self.key)


class Account(AbstractBaseUser):
    class Meta:
        verbose_name = verbose_name_plural = "アカウント"
        ordering = ["-date_joined"]

    def __str__(self):
        if self.username:
            return str(self.username)
        else:
            return "名無し"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(verbose_name="ユーザネーム", max_length=15, blank=True)
    gender = models.CharField(
        verbose_name="性別", max_length=100, choices=Gender.choices, default=Gender.NOTSET
    )
    is_secret_gender = models.BooleanField(verbose_name="性別内緒", default=False)
    job = models.CharField(
        verbose_name="職業", max_length=100, choices=Job.choices, default=Job.SECRET
    )
    introduction = models.CharField(verbose_name="自己紹介", max_length=250, blank=True)
    device_token = models.CharField(
        verbose_name="デバイストークン", max_length=200, null=True, blank=True
    )
    num_of_owner = models.IntegerField(verbose_name="オーナーとしての会話回数", default=0)
    num_of_participated = models.IntegerField(verbose_name="参加者としての会話回数", default=0)
    is_private_profile = models.BooleanField(verbose_name="プロフィール非公開", default=True)
    is_active = models.BooleanField(verbose_name="アクティブ状態", default=True)
    is_ban = models.BooleanField(
        verbose_name="凍結状態 (凍結/凍結解除する際はここをTrue/Falseに)", default=False
    )

    hidden_rooms = models.ManyToManyField(
        "chat.RoomV4",
        verbose_name="非表示ルーム",
        blank=True,
        symmetrical=False,
        related_name="hide_rooms",
    )
    blocked_rooms = models.ManyToManyField(
        "chat.RoomV4",
        verbose_name="ブロックルーム",
        blank=True,
        symmetrical=False,
        related_name="block_rooms",
    )
    blocked_accounts = models.ManyToManyField(
        "self",
        verbose_name="ブロックアカウント",
        blank=True,
        symmetrical=False,
        related_name="block_me_accounts",
    )
    favorite_users = models.ManyToManyField(
        "self",
        verbose_name="また話したいユーザ",
        blank=True,
        symmetrical=False,
        related_name="favorite_me_accounts",
        through="FavoriteUserRelationship",
    )

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    loggedin_at = models.DateTimeField(verbose_name="最終ログイン", default=timezone.now)
    date_joined = models.DateTimeField(verbose_name="登録日", default=timezone.now)

    ### not used ###
    num_of_thunks = models.IntegerField(verbose_name="(not used)ありがとう", default=0)
    genre_of_worries = models.ManyToManyField(
        GenreOfWorries, verbose_name="(not used)悩み", blank=True
    )
    talked_accounts = models.ManyToManyField(
        "self",
        verbose_name="(not used)トーク済みアカウント",
        blank=True,
        symmetrical=False,
        related_name="talked_me_accounts",
    )
    plan = models.CharField(
        verbose_name="(not used)プラン",
        max_length=100,
        choices=Plan.choices,
        default=Plan.FREE,
    )
    email = models.EmailField(
        verbose_name="(not used)メールアドレス", max_length=255, null=True, unique=True
    )
    features = models.ManyToManyField(Feature, verbose_name="(not used)特徴", blank=True)
    scale_of_worries = models.ManyToManyField(
        ScaleOfWorries, verbose_name="(not used)話せる悩みの大きさ", blank=True
    )
    birthday = models.DateField(verbose_name="(not used)生年月日", null=True, blank=True)
    status = models.CharField(
        verbose_name="(not used)ステータス",
        max_length=100,
        choices=Status.choices,
        default=Status.OFFLINE,
    )
    is_online = models.BooleanField(verbose_name="(not used)オンライン状況", default=False)
    intro_step = models.ManyToManyField(
        IntroStep, verbose_name="(not used)イントロステップ", blank=True
    )
    can_talk_heterosexual = models.BooleanField(
        verbose_name="(not used)異性との相談を許可", default=False
    )
    ### not used ###

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def user_has_perm(user, perm, obj):
        return _user_has_perm(user, perm, obj)

    def has_perm(self, perm, obj=None):
        return _user_has_perm(self, perm, obj=obj)

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_short_name(self):
        return self.username

    objects = AccountManager()


def get_upload_to(instance, filename):
    pass
    media_dir_1 = str(instance.user.id)
    return "profile_images/{0}/{1}".format(media_dir_1, filename)


class ProfileImage(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "プロフィ―ル画像"
        ordering = ("-upload_date",)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = StdImageField(
        verbose_name="画像",
        upload_to=get_upload_to,
        variations={
            "large": (600, 400),
            "thumbnail": (100, 100, True),
            "medium": (250, 250),
        },
    )
    upload_date = models.DateTimeField(verbose_name="アップロード日", default=timezone.now)
    user = models.OneToOneField(
        Account,
        verbose_name="ユーザ",
        on_delete=models.CASCADE,
        unique=True,
        related_name="image",
    )

    def __str__(self):
        return str(self.user)


class FavoriteUserRelationship(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "また話したいユーザ中間テーブル"
        ordering = ("-created_at",)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        "Account",
        verbose_name="また話したいと思った人",
        on_delete=models.CASCADE,
        related_name="owner_favorite_user_relationship",
    )
    favorite_account = models.ForeignKey(
        "Account",
        verbose_name="また話したいと思われた人",
        on_delete=models.CASCADE,
        related_name="favorite_account_favorite_user_relationship",
    )
    created_at = models.DateTimeField(verbose_name="登録日", default=timezone.now)

    def __str__(self):
        return str(self.owner.username)


class IapStatus(models.TextChoices):
    SUBSCRIPTION = "subscription", "購読中"
    FAILURE = "failure", "自動更新失敗中"
    EXPIRED = "expired", "期限切れ"


class Iap(models.Model):
    original_transaction_id = models.CharField(
        verbose_name="オリジナルトランザクションID", max_length=255, unique=True, default=""
    )
    transaction_id = models.CharField(
        verbose_name="最新トランザクションID", max_length=255, unique=True, default=""
    )
    user = models.ForeignKey(
        Account, verbose_name="対象ユーザ", on_delete=models.CASCADE, related_name="iap"
    )
    receipt = models.TextField(verbose_name="レシート", default="")
    expires_date = models.DateTimeField(verbose_name="有効期限日時")
    status = models.CharField(
        verbose_name="ステータス",
        max_length=100,
        choices=IapStatus.choices,
        default=IapStatus.SUBSCRIPTION,
    )

    def __str__(self):
        return str(self.user)
