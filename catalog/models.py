from django.db import models


class Artist(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название исполнителя",
        unique=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"

    def __str__(self) -> str:
        return str(self.name)


class Album(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название альбома",
        unique=True,
    )
    artist = models.ForeignKey(
        Artist,
        verbose_name="Исполнитель",
        on_delete=models.CASCADE,
        related_name="albums",
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Дата выпуска альбома",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"

    def __str__(self) -> str:
        return f"{self.name} {self.year}"


class Track(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название песни",
        unique=True,
    )

    albums = models.ManyToManyField(
        Album,
        related_name="tracks",
        through="AlbumTrack",
        through_fields=("track", "album"),
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Песня"
        verbose_name_plural = "Песни"

    def __str__(self) -> str:
        return str(self.name)


class AlbumTrack(models.Model):
    track = models.ForeignKey(Track, related_name="track_albums", on_delete=models.CASCADE)
    album = models.ForeignKey(Album, related_name="album_tracks", on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(
        verbose_name="Порядковый номер в альбоме",
    )

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["track", "order"],
                name="unique_track_order",
            ),
            models.UniqueConstraint(
                fields=["track", "album"],
                name="unique_track_album",
            ),
            models.UniqueConstraint(
                fields=["order", "album"],
                name="unique_order_album",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.order} {self.track}"
