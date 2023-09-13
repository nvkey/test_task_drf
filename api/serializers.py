from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from catalog.models import Album, AlbumTrack, Artist, Track


class AlbumTrackSerializer(serializers.ModelSerializer):
    """Просмотр треков в альбоме."""

    track = serializers.StringRelatedField()

    class Meta:
        model = AlbumTrack
        fields = ("id", "order", "track")


class AlbumReadSerializer(serializers.ModelSerializer):
    """Просмотр альбома."""

    album_tracks = serializers.StringRelatedField(many=True)

    class Meta:
        model = Album
        fields = ("id", "name", "artist", "year", "album_tracks")


class AlbumWriteSerializer(serializers.ModelSerializer):
    """Запись альбома."""

    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=Album.objects.all())],
    )

    class Meta:
        model = Album
        fields = ("name", "artist", "year")

    def validate_year(self, value: int) -> int:
        year = timezone.now().year
        if not (year - 300 < value <= year):
            raise serializers.ValidationError(f"{value} is not a correcrt year!")
        return value

    def to_representation(self, instance):
        return AlbumReadSerializer(instance, context=self.context).data


class ArtistReadSerializer(serializers.ModelSerializer):
    """Просмотр исполнителя."""

    albums = AlbumReadSerializer(read_only=True, many=True)

    class Meta:
        model = Artist
        fields = ("id", "name", "albums")


class ArtistWriteSerializer(serializers.ModelSerializer):
    """Запись исполнителя."""

    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=Artist.objects.all())],
    )

    class Meta:
        model = Artist
        fields = ("name",)

    def to_representation(self, instance):
        return ArtistReadSerializer(instance, context=self.context).data


class TrackAlbumOrderSerializer(serializers.ModelSerializer):
    """Нумерация и альбомы трэка."""

    album = serializers.SlugRelatedField(queryset=AlbumTrack.objects.all(), slug_field="name")

    class Meta:
        model = AlbumTrack
        fields = ("order", "album")


class TrackReadSerializer(serializers.ModelSerializer):
    """Просмотр трэка."""

    track_albums = TrackAlbumOrderSerializer(read_only=True, many=True)

    class Meta:
        model = Track
        fields = ("id", "name", "track_albums")


class TrackAlbumOrderWriteSerializer(serializers.ModelSerializer):
    """Запись трека, нумерации и альбома."""

    name = serializers.CharField(max_length=100, source="track")
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all())
    order = serializers.IntegerField(min_value=1, max_value=999)

    class Meta:
        model = AlbumTrack
        fields = ("name", "order", "album")

    def validate(self, data):
        name = data["track"]
        album = data["album"]
        order = data["order"]
        if AlbumTrack.objects.filter(order=order, album=album).exists():
            raise serializers.ValidationError("Номер уже занят в этом альбоме")
        if not Track.objects.filter(name=name).exists():
            return data
        track = Track.objects.get(name=name)
        if AlbumTrack.objects.filter(track=track, album=album).exists():
            raise serializers.ValidationError("Трек уже есть в альбоме")
        if AlbumTrack.objects.filter(track=track, order=order).exists():
            raise serializers.ValidationError("Номер уже существует в другом альбоме")
        return data

    def create(self, validated_data):
        name = validated_data.pop("track")
        album = validated_data.pop("album")
        order = validated_data.pop("order")
        track, status = Track.objects.get_or_create(name=name)
        return AlbumTrack.objects.create(track=track, album=album, order=order)

    def to_representation(self, instance):
        return TrackAlbumOrderReadSerializer(instance, context=self.context).data


class TrackAlbumOrderReadSerializer(serializers.ModelSerializer):
    """Чтение трека, нумерации и альбома."""

    track_id = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all())
    name = serializers.StringRelatedField(source="track")
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all())

    class Meta:
        model = AlbumTrack
        fields = ("id", "track_id", "name", "order", "album")


class AlbumTrackDeleteSerializer(serializers.Serializer):
    order = serializers.IntegerField(min_value=1)
