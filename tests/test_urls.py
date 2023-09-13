import pytest
from rest_framework import status
from rest_framework.test import APIClient


class TestStaticURLs:
    @pytest.mark.parametrize(
        "url, expectation",
        [
            ("/api/v1/artists/", status.HTTP_200_OK),
            ("/api/v1/albums/", status.HTTP_200_OK),
            ("/api/v1/tracks/", status.HTTP_200_OK),
            ("/admin/", status.HTTP_302_FOUND),
        ],
    )
    @pytest.mark.django_db()
    def test_api_urls(self, api_client: APIClient, url, expectation):
        response = api_client.get(url)
        assert response.status_code == expectation
