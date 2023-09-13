import pytest
from django.db import IntegrityError

from .factories import AlbumFactory, ArtistFactory, TrackWithAlbumFactory


@pytest.mark.django_db(transaction=True)
class TestArtistModel:
    def test_raise_unique_name(self):
        artist = ArtistFactory.create()
        with pytest.raises(IntegrityError):
            assert ArtistFactory.create(name=artist.name)


@pytest.mark.django_db(transaction=True)
class TestAlbumtModel:
    def test_raise_unique_name(self):
        album = AlbumFactory.create()
        with pytest.raises(IntegrityError):
            assert AlbumFactory.create(name=album.name)


@pytest.mark.django_db(transaction=True)
class TestTracktModel:
    def test_model_have_correct_object_name(self):
        track = TrackWithAlbumFactory.create()
        expected = track.name
        assert expected == str(track)
