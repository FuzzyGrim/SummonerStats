from django.db import models


class Match(models.Model):

    match_id = models.CharField(max_length=15)
    match_json = models.JSONField(default=dict)
    summoner = models.CharField(max_length=50)
    summoner_json = models.JSONField(default=dict)

    class Meta:
        ordering = ["-match_id"]

    def __str__(self):
        return self.match_id


class Summoner(models.Model):

    summoner = models.CharField(max_length=50)
    matches = models.IntegerField(default=0)
    minutes = models.IntegerField(default=0)
    champions = models.JSONField(default=dict)
    roles = models.JSONField(default=dict)
    stats = models.JSONField(default=dict)

    class Meta:
        ordering = ["-matches"]

    def __str__(self):
        return self.summoner
