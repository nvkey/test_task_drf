from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from catalog.models import Album, AlbumTrack, Track


def remove_track_from_album(album: Album, data: dict) -> Response:
    order = data["order"]
    if not AlbumTrack.objects.filter(album=album, order=order).exists():
        return Response("Нет такого номера трэка", status=status.HTTP_404_NOT_FOUND)
    album_track_order = get_object_or_404(AlbumTrack, album=album, order=order)
    if AlbumTrack.objects.filter(track=album_track_order.track).count() == 1:
        track = get_object_or_404(Track, id=album_track_order.track.id)
        track.delete()
        return Response("Трэк удален", status=status.HTTP_204_NO_CONTENT)
    album_track_order.delete()
    return Response("Трэк удален из альбома", status=status.HTTP_204_NO_CONTENT)
