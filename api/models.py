from django.db import models


class Match(models.Model):
    match_id = models.CharField(max_length=15)

    summary_json = models.JSONField(default=dict)

    summoner = models.CharField(max_length=50)

    def __str__(self):
        return self.match_id
