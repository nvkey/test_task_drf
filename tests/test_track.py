from typing import Any, Dict

import pytest
from django.urls import reverse
from pytest_assert_utils import assert_model_attrs
from pytest_common_subject import precondition_fixture
from pytest_drf import (
    Returns200,
    Returns201,
    Returns204,
    Returns400,
    UsesDeleteMethod,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPostMethod,
    ViewSetTest,
)
from pytest_drf.util import pluralized, url_for
from pytest_lambda import lambda_fixture
from rest_framework import status

from catalog.models import AlbumTrack, Track

from .factories import AlbumFactory, TrackWith2AlbumFactory


def express_track(track: Track) -> Dict[str, Any]:
    """Метод выражения класса Track"""
    print(track)
    print(type(track))
    return {
        "id": track.id,
        "name": track.name,
        "track_albums": list(
            ({"order": AlbumTrack.objects.get(album=album, track=track).order, "album": album.name})
            for album in track.albums.all()
        ),
    }


express_tracks = pluralized(express_track)


@pytest.mark.django_db(transaction=True)
class TestTrackViewSet(ViewSetTest):
    list_url = lambda_fixture(lambda: url_for("tracks-list"))

    detail_url = lambda_fixture(lambda track: url_for("tracks-detail", track.pk))

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        tracks = lambda_fixture(
            lambda: TrackWith2AlbumFactory.create_batch(size=1),
            autouse=True,
        )

        def test_it_returns_tracks(self, tracks, results):
            expected = express_tracks(sorted(tracks, key=lambda track: track.id))
            actual = results
            assert expected == actual

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        data = lambda_fixture(
            lambda: {
                "name": "New Track",
                "order": 1,
                "album": AlbumFactory.create().id,
            }
        )

        initial_track_ids = precondition_fixture(
            lambda: set(Track.objects.values_list("id", flat=True)),
            async_=False,
        )

        def test_it_creates_new_track(self, initial_track_ids, json):
            """Тест что был добавлен только один новый идентификатор."""
            expected = initial_track_ids | {json["track_id"]}
            actual = set(Track.objects.values_list("id", flat=True))
            assert expected == actual

        def test_it_sets_expected_attrs(self, data, json):
            """Тест значения полей, которые мы отправили POST."""
            track = Track.objects.get(pk=json["track_id"])
            data.pop("order")
            data.pop("album")
            expected = data
            assert_model_attrs(track, expected)

    class TestRaiseCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns400,
    ):
        data = lambda_fixture(
            lambda: {
                "name": "New Track",
                "order": 0,
                "album": AlbumFactory.create().id,
            }
        )

        initial_track_ids = precondition_fixture(
            lambda: set(Track.objects.values_list("id", flat=True)),
            async_=False,
        )

        def test_it_not_creates_new_track(self, initial_track_ids, json):
            """Тест что не был добавлен трэк при записи 0 номера."""
            expected = initial_track_ids
            actual = set(Track.objects.values_list("id", flat=True))
            assert expected == actual

    class TestDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        track = lambda_fixture(lambda: TrackWith2AlbumFactory.create())
        initial_track_ids = precondition_fixture(
            lambda track: set(Track.objects.values_list("id", flat=True)),
            async_=False,
        )

        def test_it_deletes_track(self, initial_track_ids, track):
            expected = initial_track_ids - {track.id}
            actual = set(Track.objects.values_list("id", flat=True))
            assert expected == actual


@pytest.fixture
def track_with_2_albums():
    return TrackWith2AlbumFactory.create()


@pytest.mark.django_db(transaction=True)
def test_it_not_creates_repeat_track_name_album(api_client, track_with_2_albums):
    """Тест валидации повторяющегося трека в альбоме"""
    actual = set(AlbumTrack.objects.values_list("id", flat=True))
    url = reverse("tracks-list")
    album_id = track_with_2_albums.albums.all()[0].id
    response = api_client.post(url, data={"name": track_with_2_albums.name, "order": 999, "album": album_id})
    expected = set(AlbumTrack.objects.values_list("id", flat=True))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected == actual


@pytest.mark.django_db(transaction=True)
def test_it_not_creates_repeat_track_order(api_client, track_with_2_albums):
    """Тест валидации повторяющегося номера трека в альбоме"""
    actual = set(AlbumTrack.objects.values_list("id", flat=True))
    url = reverse("tracks-list")
    album_id = track_with_2_albums.albums.all()[0].id
    track_order_in_album = AlbumTrack.objects.get(track=track_with_2_albums, album=album_id).order
    response = api_client.post(url, data={"name": "NewName", "order": track_order_in_album, "album": album_id})
    expected = set(AlbumTrack.objects.values_list("id", flat=True))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected == actual


@pytest.mark.django_db(transaction=True)
def test_it_not_creates_repeat_track_order_other_album(api_client, track_with_2_albums):
    """Тест валидации повторяющегося номера трека в другом альбоме"""
    actual = set(AlbumTrack.objects.values_list("id", flat=True))
    url = reverse("tracks-list")
    album_id = track_with_2_albums.albums.all()[0].id
    track_order_in_album = AlbumTrack.objects.get(track=track_with_2_albums, album=album_id).order
    new_album = AlbumFactory.create()
    response = api_client.post(
        url, data={"name": track_with_2_albums.name, "order": track_order_in_album, "album": new_album.id}
    )
    expected = set(AlbumTrack.objects.values_list("id", flat=True))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected == actual
