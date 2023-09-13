import pytest

from .factories import AlbumTrackFactory


@pytest.mark.skip(reason="Одиночная проверка")
@pytest.mark.django_db(transaction=True)
class TestAlbumTrackFactory:
    def test_order_start_sequence(self):
        album_track = AlbumTrackFactory.create()
        expected = album_track.order
        assert expected == 1
