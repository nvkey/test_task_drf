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
    UsesPatchMethod,
    UsesPostMethod,
    ViewSetTest,
)
from pytest_drf.util import pluralized, url_for
from pytest_lambda import lambda_fixture, static_fixture
from rest_framework import status

from catalog.models import Album, AlbumTrack, Artist

from .factories import AlbumFactory, AlbumWith2TracksFactory, ArtistFactory, TrackFactory
from .utils import set_field_obj


def express_album(album: Album) -> Dict[str, Any]:
    """Метод выражения класса Album"""
    return {
        "id": album.id,
        "name": album.name,
        "artist": album.artist.id,
        "year": album.year,
        "album_tracks": list(map(str, album.album_tracks.all())),
    }


express_albums = pluralized(express_album)


@pytest.mark.django_db(transaction=True)
class TestAlbumViewSet(ViewSetTest):
    list_url = lambda_fixture(lambda: url_for("albums-list"))

    detail_url = lambda_fixture(lambda album: url_for("albums-detail", album.pk))

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        albums = lambda_fixture(
            lambda: AlbumWith2TracksFactory.create_batch(size=5),
            autouse=True,
        )

        def test_it_returns_albums(self, albums, results):
            expected = express_albums(sorted(albums, key=lambda album: album.id))
            actual = results
            assert expected == actual

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        data = lambda_fixture(
            lambda: {
                "name": "Album",
                "artist": ArtistFactory.create().id,
                "year": 1998,
            }
        )

        initial_album_ids = precondition_fixture(
            lambda: set(Album.objects.values_list("id", flat=True)),
            async_=False,
        )

        def test_it_creates_new_album(self, initial_album_ids, json):
            """Тест что был добавлен только один новый идентификатор."""

            expected = initial_album_ids | {json["id"]}
            actual = set(Album.objects.values_list("id", flat=True))

            assert expected == actual

        def test_it_sets_expected_attrs(self, data, json):
            """Тест значения полей, которые мы отправили POST."""
            album = Album.objects.get(pk=json["id"])
            expected = set_field_obj(data, "artist", Artist)
            assert_model_attrs(album, expected)

        def test_it_returns_album(self, json):
            """Тест структуры ответа."""
            album = Album.objects.get(pk=json["id"])

            expected = express_album(album)
            actual = json
            assert expected == actual

    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        album = lambda_fixture(lambda: AlbumFactory.create())

        def test_it_returns_album(self, album, json):
            expected = express_album(album)
            actual = json
            assert expected == actual

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        album = lambda_fixture(lambda: AlbumFactory.create())
        data = static_fixture(
            {
                "name": "Album Update",
            }
        )

        def test_it_sets_expected_attrs(self, data, album):
            """Тест изменений в БД"""
            album.refresh_from_db()

            expected = data
            assert_model_attrs(album, expected)

        def test_it_returns_album(self, album, json):
            """Тест структуры ответа."""
            album.refresh_from_db()

            expected = express_album(album)
            actual = json
            assert expected == actual

    class TestDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        album = lambda_fixture(lambda: AlbumFactory.create())
        initial_album_ids = precondition_fixture(
            lambda album: set(Album.objects.values_list("id", flat=True)),
            async_=False,
        )

        def test_it_deletes_album(self, initial_album_ids, album):
            expected = initial_album_ids - {album.id}
            actual = set(Album.objects.values_list("id", flat=True))
            assert expected == actual

    class TestUnique(
        UsesPostMethod,
        UsesListEndpoint,
        Returns400,
    ):
        album = lambda_fixture(lambda: Album.create(name="RaiseAlbum"))
        data = static_fixture(
            {"name": "RaiseAlbum"},
        )
        initial_album_ids = precondition_fixture(
            lambda: set(Artist.objects.values_list("id", flat=True)),
            async_=False,
        )

        def test_it_not_creates_new_album(self, initial_album_ids):
            """Тест записи уникального имени"""
            actual = set(Artist.objects.values_list("id", flat=True))
            expected = initial_album_ids
            assert expected == actual


@pytest.mark.django_db(transaction=True)
class TestAlbumViewSetAction:
    def test_it_deletes_album_order(self, api_client):
        """Тест удаления записи по номеру"""
        album = AlbumFactory.create()
        track = TrackFactory.create()
        album_track = AlbumTrack.objects.create(track=track, album=album, order=88)
        initial_album_ids = set((AlbumTrack.objects.all().values_list("id", flat=True)))
        url = url_for("albums-detail", album.id) + "remove_track/"

        response = api_client.delete(url, {"order": album_track.order}, format="json")
        expected = initial_album_ids - {album_track.id}

        actual = set(AlbumTrack.objects.values_list("id", flat=True))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert expected == actual


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "year",
    [
        500,
        99999,
    ],
)
def test_it_not_creates_new_album_validate_year(api_client, year):
    """Тест записи неправильного года"""
    artist = ArtistFactory.create()
    url = reverse("albums-list")
    actual = set(Album.objects.values_list("id", flat=True))
    response = api_client.post(url, data={"name": AlbumFactory.build().name, "year": year, "artist": artist.id})
    expected = set(Album.objects.values_list("id", flat=True))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected == actual
