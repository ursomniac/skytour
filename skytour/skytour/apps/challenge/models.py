from django.db import models
from .vocabs import *

class ChallengeList(models.Model):
    title = models.CharField(
        max_length = 100,
    )
    slug = models.SlugField()

    class Meta:
        verbose_name = 'Challenge List'
        verbose_name_plural = 'Challenge Lists'

class ObservingChallenge(models.Model):
    title = models.CharField (
        max_length = 60,
        null = True, blank = True
    )
    id_in_list = models.CharField (
        max_length = 10
    )
    suited_for = models.CharField (
        max_length = 20,
        choices = CHALLENGE_CLASSES
    )

class ObservingChallengeSuccess(models.Model):
    challenge = models.ForeignKey(ObservingChallenge, on_delete=models.CASCADE)
    status = models.IntegerField (
        choices = CHALLENGE_STATUSES
    )
