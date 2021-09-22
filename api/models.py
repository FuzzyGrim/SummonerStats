from django.db import models


class Match(models.Model):
    match_id = models.CharField(max_length=15)

    REGION_BY_PLATFORM = (
        ("NA1", "AMERICAS"),
        ("BR1", "AMERICAS"),
        ("LA1", "AMERICAS"),
        ("LA2", "AMERICAS"),
        ("OC1", "AMERICAS"),
        ("EUN1", "EUROPE"),
        ("EUW1", "EUROPE"),
        ("TR1", "EUROPE"),
        ("RU", "EUROPE"),
        ("KR", "ASIA"),
        ("JP1", "ASIA"),
    )

    json_file = models.JSONField(default=list)

    region = models.CharField(max_length=4, choices=REGION_BY_PLATFORM)
    
    def __str__(self):
        return self.match_id