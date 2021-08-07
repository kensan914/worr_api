from django.db import models
import uuid


class AccountDeleteSurvey(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "アカウント削除理由"
        ordering = ("-created_at",)

    def __str__(self):
        return "{}".format(self.respondent.username)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    respondent = models.ForeignKey(
        "account.Account", verbose_name="回答者", on_delete=models.CASCADE
    )
    reason = models.CharField(
        verbose_name="アカウント削除のきっかけとなる不満と感じた点を教えていただけませんか？", max_length=500
    )
    created_at = models.DateTimeField(verbose_name="回答日", auto_now_add=True)


class DissatisfactionSurvey(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "不満レビュー"
        ordering = ("-created_at",)

    def __str__(self):
        return "{}".format(self.respondent.username)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    respondent = models.ForeignKey(
        "account.Account", verbose_name="回答者", on_delete=models.CASCADE
    )
    contents = models.CharField(verbose_name="不満点を聞かせてください", max_length=500)
    created_at = models.DateTimeField(verbose_name="回答日", auto_now_add=True)
