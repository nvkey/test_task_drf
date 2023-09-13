from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.models import Album, Artist, Track

from .serializers import (
    AlbumReadSerializer,
    AlbumTrackDeleteSerializer,
    AlbumWriteSerializer,
    ArtistReadSerializer,
    ArtistWriteSerializer,
    TrackAlbumOrderWriteSerializer,
    TrackReadSerializer,
)
from .services import remove_track_from_album

WRITE_METHODS = ["PUT", "POST", "PATCH"]


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()

    def get_serializer_class(self):
        if self.request.method in WRITE_METHODS:
            return ArtistWriteSerializer
        return ArtistReadSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()

    def get_serializer_class(self):
        if self.request.method in WRITE_METHODS:
            return AlbumWriteSerializer
        return AlbumReadSerializer

    @action(detail=True, methods=["delete"])
    def remove_track(self, request, pk):
        album = get_object_or_404(Album, pk=pk)
        serializer = AlbumTrackDeleteSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            return remove_track_from_album(album, data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrackViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Трэки возможно только добавлять и удалять, без редактирования:)."""

    queryset = Track.objects.all()

    def get_serializer_class(self):
        if self.request.method in WRITE_METHODS:
            return TrackAlbumOrderWriteSerializer
        return TrackReadSerializer
