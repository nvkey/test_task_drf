from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlbumViewSet, ArtistViewSet, TrackViewSet

router = DefaultRouter()
router.register("artists", ArtistViewSet, basename="artists")
router.register("albums", AlbumViewSet, basename="albums")
router.register("tracks", TrackViewSet, basename="tracks")
urlpatterns = [
    path("v1/", include(router.urls)),
]
