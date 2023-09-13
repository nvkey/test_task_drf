from typing import Any, Dict

import pytest
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

from catalog.models import Artist

from .factories import ArtistFactory


def express_artist(artist: Artist) -> Dict[str, Any]:
    """Метод выражения класса Artist"""
    return {
        "id": artist.id,
        "name": artist.name,
        "albums": [],
    }


express_artists = pluralized(express_artist)


@pytest.mark.django_db(transaction=True)
class TestArtistViewSet(ViewSetTest):
    list_url = lambda_fixture(lambda: url_for("artists-list"))

    detail_url = lambda_fixture(lambda artist: url_for("artists-detail", artist.pk))

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        artists = lambda_fixture(
            lambda: ArtistFactory.create_batch(size=10),
            autouse=True,
        )

        def test_it_returns_artists(self, artists, results):
            expected = express_artists(sorted(artists, key=lambda artist: artist.id))
            actual = results

            assert expected == actual

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        data = static_fixture({"name": "Nikita"})

        initial_artist_ids = precondition_fixture(
            lambda: set(Artist.objects.values_list("id", flat=True)),
            async_=False,
        )

        def test_it_creates_new_artist(self, initial_artist_ids, json):
            """Тест что был добавлен только один новый идентификатор."""
            expected = initial_artist_ids | {json["id"]}
            actual = set(Artist.objects.values_list("id", flat=True))
            assert expected == actual

        def test_it_sets_expected_attrs(self, data, json):
            """Тест значения полей, которые мы отправили POST."""
            artist = Artist.objects.get(pk=json["id"])

            expected = data
            assert_model_attrs(artist, expected)

        def test_it_returns_artist(self, json):
            """Тест структуры ответа."""
            artist = Artist.objects.get(pk=json["id"])

            expected = express_artist(artist)
            actual = json | {"albums": []}
            assert expected == actual

    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        artist = lambda_fixture(lambda: ArtistFactory.create())

        def test_it_returns_artist(self, artist, json):
            expected = express_artist(artist)
            actual = json
            assert expected == actual

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        artist = lambda_fixture(lambda: ArtistFactory.create())
        data = static_fixture(
            {
                "name": "Kolesnikov",
            }
        )

        def test_it_sets_expected_attrs(self, data, artist):
            """Тест изменений в БД"""
            artist.refresh_from_db()

            expected = data
            assert_model_attrs(artist, expected)

        def test_it_returns_artist(self, artist, json):
            """Тест структуры ответа."""
            artist.refresh_from_db()

            expected = express_artist(artist)
            actual = json
            assert expected == actual

    class TestDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        artist = lambda_fixture(lambda: ArtistFactory.create())
        initial_artist_ids = precondition_fixture(
            lambda artist: set(Artist.objects.values_list("id", flat=True)),
            async_=False,
        )

        def test_it_deletes_artist(self, initial_artist_ids, artist):
            expected = initial_artist_ids - {artist.id}
            actual = set(Artist.objects.values_list("id", flat=True))
            assert expected == actual

    class TestUnique(
        UsesPostMethod,
        UsesListEndpoint,
        Returns400,
    ):
        data = static_fixture({"name": "RaiseArtist"})
        initial_artist_ids = precondition_fixture(
            lambda: set(
                list(Artist.objects.all().values_list("id", flat=True)) + [ArtistFactory.create(name="RaiseArtist").id]
            ),
            async_=False,
        )

        def test_it_not_creates_new_artist(self, initial_artist_ids):
            """Тест записи уникального имени"""
            actual = set(Artist.objects.values_list("id", flat=True))
            expected = initial_artist_ids
            assert expected == actual
