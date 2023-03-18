import unittest, json
from unittest.mock import patch

from requests import Session
from kf_backend import KFBackend


class MockResponse:
    def __init__(self, json_data, text, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text

    def json(self):
        return self.json_data


def mocked_requests_get(*args, **kwargs):
    if args[0] == "https://mock_url/outages":
        return MockResponse(
            [
                {
                    "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                    "begin": "2021-07-26T17:09:31.036Z",
                    "end": "2021-08-29T00:37:42.253Z",
                },
                {
                    "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                    "begin": "2022-05-23T12:21:27.377Z",
                    "end": "2022-11-13T02:16:38.905Z",
                },
                {
                    "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                    "begin": "2022-12-04T09:59:33.628Z",
                    "end": "2022-12-12T22:35:13.815Z",
                },
                {
                    "id": "04ccad00-eb8d-4045-8994-b569cb4b64c1",
                    "begin": "2022-07-12T16:31:47.254Z",
                    "end": "2022-10-13T04:05:10.044Z",
                },
                {
                    "id": "086b0d53-b311-4441-aaf3-935646f03d4d",
                    "begin": "2022-07-12T16:31:47.254Z",
                    "end": "2022-10-13T04:05:10.044Z",
                },
                {
                    "id": "27820d4a-1bc4-4fc1-a5f0-bcb3627e94a1",
                    "begin": "2021-07-12T16:31:47.254Z",
                    "end": "2022-10-13T04:05:10.044Z",
                },
                {
                    "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                    "begin": "2022-01-01T00:00:00.000Z",
                    "end": "2022-01-02T00:00:00.000Z",
                },
            ],
            "",
            200,
        )
    elif args[0] == "https://mock_url/site-info/kingfisher":
        return MockResponse(
            {
                "id": "kingfisher",
                "name": "KingFisher",
                "devices": [
                    {"id": "002b28fc-283c-47ec-9af2-ea287336dc1b", "name": "Battery 1"},
                    {"id": "086b0d53-b311-4441-aaf3-935646f03d4d", "name": "Battery 2"},
                ],
            },
            "",
            200,
        )

    return MockResponse(None, "", 404)


def mocked_requests_post(*args, **kwargs):
    return MockResponse(None, "", 200)


class KFBackendTest(unittest.TestCase):
    def setUp(self) -> None:
        self.kf_backend = KFBackend("https://mock_url", "mock_api_key")

    @patch.object(Session, "get", side_effect=mocked_requests_get)
    @patch.object(Session, "post", side_effect=mocked_requests_post)
    def test_kf_backend_handler(self, mock_post, mock_get):
        expected_data = [
            {
                "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                "begin": "2022-05-23T12:21:27.377Z",
                "end": "2022-11-13T02:16:38.905Z",
                "name": "Battery 1",
            },
            {
                "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                "begin": "2022-12-04T09:59:33.628Z",
                "end": "2022-12-12T22:35:13.815Z",
                "name": "Battery 1",
            },
            {
                "id": "086b0d53-b311-4441-aaf3-935646f03d4d",
                "begin": "2022-07-12T16:31:47.254Z",
                "end": "2022-10-13T04:05:10.044Z",
                "name": "Battery 2",
            },
            {
                "id": "002b28fc-283c-47ec-9af2-ea287336dc1b",
                "begin": "2022-01-01T00:00:00.000Z",
                "end": "2022-01-02T00:00:00.000Z",
                "name": "Battery 1",
            },
        ]
        self.kf_backend.handler(site_id="kingfisher", after="2022-01-01T00:00:00.000Z")
        mock_post.assert_called_with(
            "https://mock_url/site-outages/kingfisher", data=json.dumps(expected_data)
        )

    @patch.object(
        Session,
        "get",
        side_effect=[
            MockResponse(None, "test error", 500),
            MockResponse(None, "", 200),
        ],
    )
    @patch.object(Session, "post", side_effect=mocked_requests_post)
    def test_kf_backend_exit_1_when_outages_returns_error(self, mock_post, mock_get):
        with self.assertRaises(SystemExit):
            self.kf_backend.handler(
                site_id="kingfisher", after="2022-01-01T00:00:00.000Z"
            )

    @patch.object(
        Session,
        "get",
        side_effect=[
            MockResponse(None, "test error", 200),
            MockResponse(None, "test error", 500),
        ],
    )
    @patch.object(Session, "post", side_effect=mocked_requests_post)
    def test_kf_backend_exit_1_when_site_info_returns_error(self, mock_post, mock_get):
        with self.assertRaises(SystemExit):
            self.kf_backend.handler(
                site_id="kingfisher", after="2022-01-01T00:00:00.000Z"
            )

    @patch.object(Session, "get", side_effect=mocked_requests_get)
    @patch.object(Session, "post", side_effect=mocked_requests_post)
    def test_kf_backend_sets_api_key_header(self, mock_post, mock_get):
        self.assertEqual(self.kf_backend.session.headers["x-api-key"], "mock_api_key")


if __name__ == "__main__":
    unittest.main()
