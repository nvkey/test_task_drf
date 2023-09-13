import json

from django.db import migrations

"""
Миграции тестовых данных из json
Формат импорта:
[путь, приложение, модель]

"""

data_list = [
    ["data/artists.json", "catalog", "Artist"],
    ["data/albums.json", "catalog", "Album"],
    ["data/tracks.json", "catalog", "Track"],
    ["data/albums_tracks.json", "catalog", "AlbumTrack"],
]


def add_data(apps, schema_editor):
    for data_flow in data_list:
        path = data_flow[0]
        with open(path, encoding="utf-8") as file:
            initial_data = json.load(file)
        model = apps.get_model(data_flow[1], data_flow[2])
        initial_data_list = []
        for data in initial_data:
            new_data = model(**data)
            initial_data_list.append(new_data)
        model.objects.bulk_create(initial_data_list)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [migrations.RunPython(add_data)]
