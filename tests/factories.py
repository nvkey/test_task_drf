import factory
from faker import Faker

from catalog.models import Album, AlbumTrack, Artist, Track

fake = Faker()


class ArtistFactory(factory.django.DjangoModelFactory):
    """Artist фабрика"""

    class Meta:
        model = Artist

    name = factory.Sequence(lambda n: fake.unique.name())


class AlbumFactory(factory.django.DjangoModelFactory):
    """Album фабрика"""

    class Meta:
        model = Album

    name = factory.LazyAttribute(lambda x: fake.unique.name())
    year = factory.LazyAttribute(lambda x: int(fake.year()))
    artist = factory.SubFactory(ArtistFactory)


class TrackFactory(factory.django.DjangoModelFactory):
    """Track фабрика"""

    class Meta:
        model = Track

    name = factory.LazyAttribute(lambda x: fake.unique.name())


class AlbumTrackFactory(factory.django.DjangoModelFactory):
    """Track фабрика"""

    class Meta:
        model = AlbumTrack

    track = factory.SubFactory(TrackFactory)
    album = factory.SubFactory(AlbumFactory)
    order = factory.Sequence(lambda n: n + 1)


class TrackWithAlbumFactory(TrackFactory):
    """Track и 1 Album фабрика"""

    class Meta:
        skip_postgeneration_save = True

    album_release = factory.RelatedFactory(
        AlbumTrackFactory,
        factory_related_name="track",
    )


class TrackWith2AlbumFactory(TrackFactory):
    """Track и 2 Album фабрика"""

    class Meta:
        skip_postgeneration_save = True

    album_release1 = factory.RelatedFactory(
        AlbumTrackFactory,
        factory_related_name="track",
        album__name=factory.LazyAttribute(lambda x: fake.unique.name()),
    )
    album_release2 = factory.RelatedFactory(
        AlbumTrackFactory,
        factory_related_name="track",
        album__name=factory.LazyAttribute(lambda x: fake.unique.name()),
    )


class AlbumWithTrackFactory(AlbumFactory):
    """Album и Track фабрика"""

    class Meta:
        skip_postgeneration_save = True

    tracl_release = factory.RelatedFactory(
        AlbumTrackFactory,
        factory_related_name="album",
    )


class AlbumWith2TracksFactory(AlbumFactory):
    """Album и 2 Track фабрика"""

    class Meta:
        skip_postgeneration_save = True

    track_release_1 = factory.RelatedFactory(
        AlbumTrackFactory,
        factory_related_name="album",
        track__name=factory.LazyAttribute(lambda x: fake.unique.name()),
    )
    track_release_2 = factory.RelatedFactory(
        AlbumTrackFactory,
        factory_related_name="album",
        track__name=factory.LazyAttribute(lambda x: fake.unique.name()),
    )
