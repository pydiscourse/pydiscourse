"""Tests for the client methods."""

import urllib.parse

import pytest


def test_empty_content_http_ok(discourse_host, discourse_client, discourse_request):
    """Empty content should not raise error

    Critical to test against *bytestrings* rather than unicode
    """
    discourse_request(
        "get",
        "/users/admin/1/unsuspend",
        headers={"Content-Type": "text/plain; charset=utf-8"},
        content=b" ",
    )

    resp = discourse_client._request("GET", "/users/admin/1/unsuspend", {})

    assert resp is None


class TestUserManagement:
    def test_get_user(self, discourse_host, discourse_client, discourse_request):
        request = discourse_request(
            "get",
            "/users/someuser.json",
            json={"user": "someuser"},
        )
        discourse_client.user("someuser")

        assert request.called_once

    def test_users(self, discourse_client, discourse_request):
        request = discourse_request("get", "/admin/users/list/active.json")
        discourse_client.users()
        assert request.called_once

    def test_create_user(self, discourse_host, discourse_client, discourse_request):
        session_request = discourse_request(
            "get",
            "/session/hp.json",
            json={"challenge": "challenge", "value": "value"},
        )
        user_request = discourse_request("post", "/users")
        discourse_client.create_user(
            "Test User",
            "testuser",
            "test@example.com",
            "notapassword",
        )

        assert session_request.called_once
        assert user_request.called_once

    def test_update_email(self, discourse_host, discourse_client, discourse_request):
        request = discourse_request("put", "/users/someuser/preferences/email")
        discourse_client.update_email("someuser", "newmeail@example.com")

        assert request.called_once

    def test_update_user(self, discourse_client, discourse_request):
        request = discourse_request("put", "/users/someuser")
        discourse_client.update_user("someuser", a="a", b="b")

        assert request.called_once

    def test_update_username(self, discourse_client, discourse_request):
        request = discourse_request("put", "/users/someuser/preferences/username")
        discourse_client.update_username("someuser", "newname")

        assert request.called_once

    def test_by_external_id(self, discourse_client, discourse_request):
        request = discourse_request(
            "get",
            "/users/by-external/123",
            json={"user": "123"},
        )
        discourse_client.by_external_id(123)

        assert request.called_once

    def test_anonymize(self, discourse_client, discourse_request):
        request = discourse_request("put", "/admin/users/123/anonymize")
        discourse_client.anonymize(123)

        assert request.called_once

    @pytest.mark.usefixtures("_frozen_time")
    def test_suspend_user(self, discourse_client, discourse_request):
        request = discourse_request("put", "/admin/users/123/suspend")
        discourse_client.suspend(123, 1, "Testing")

        assert request.called_once
        assert request.last_request.method == "PUT"

        request_payload = urllib.parse.parse_qs(request.last_request.text)

        assert request_payload["reason"] == ["Testing"]
        assert request_payload["suspend_until"] == ["2023-08-14T12:30:15+00:00"]

    def test_unsuspend_user(self, discourse_client, discourse_request):
        request = discourse_request("put", "/admin/users/123/unsuspend")
        discourse_client.unsuspend(123)

        assert request.called_once

    def test_user_bagdes(self, discourse_client, discourse_request):
        request = discourse_request("get", "/user-badges/myusername.json")
        discourse_client.user_badges("myusername")

        assert request.called_once


class TestTopics:
    def test_hot_topics(self, discourse_client, discourse_request):
        request = discourse_request("get", "/hot.json")
        discourse_client.hot_topics()
        assert request.called_once

    def test_latest_topics(self, discourse_client, discourse_request):
        request = discourse_request("get", "/latest.json")
        discourse_client.latest_topics()

        assert request.called_once

    def test_new_topics(self, discourse_client, discourse_request):
        request = discourse_request("get", "/new.json")
        discourse_client.new_topics()
        assert request.called_once

    def test_topic(self, discourse_client, discourse_request):
        request = discourse_request("get", "/t/some-test-slug/22.json")
        discourse_client.topic("some-test-slug", 22)
        assert request.called_once

    def test_topics_by(self, discourse_client, discourse_request):
        request = discourse_request(
            "get",
            "/topics/created-by/someuser.json",
            json={"topic_list": {"topics": []}},
        )
        discourse_client.topics_by("someuser")

        assert request.called_once

    def test_invite_user_to_topic(self, discourse_client, discourse_request):
        request = discourse_request("post", "/t/22/invite.json")
        discourse_client.invite_user_to_topic("test@example.com", 22)
        assert request.called_once

        request_payload = urllib.parse.parse_qs(request.last_request.text)

        assert request_payload["email"] == ["test@example.com"]
        assert request_payload["topic_id"] == ["22"]


class TestPosts:
    def test_latest_posts(self, discourse_client, discourse_request):
        request = discourse_request("get", "/posts.json?before=54321")
        discourse_client.latest_posts(before=54321)
        assert request.called_once

    def test_post_by_number(self, discourse_client, discourse_request):
        request = discourse_request("get", "/posts/by_number/8796/5")
        discourse_client.post_by_number(8796, 5)
        assert request.called_once


class TestSearch:
    def test_search(self, discourse_client, discourse_request):
        request = discourse_request("get", "/search.json?q=needle")
        discourse_client.search(q="needle")
        assert request.called_once


class TestCategories:
    def test_categories(self, discourse_client, discourse_request):
        request = discourse_request(
            "get",
            "/categories.json",
            json={"category_list": {"categories": []}},
        )
        discourse_client.categories()
        assert request.called_once

    def test_update_category(self, discourse_client, discourse_request):
        request = discourse_request("put", "/categories/123")
        discourse_client.update_category(123, a="a", b="b")

        request_payload = request.last_request.json()

        assert request_payload["a"] == "a"
        assert request_payload["b"] == "b"


class TestBadges:
    def test_badges(self, discourse_client, discourse_request):
        request = discourse_request("get", "/admin/badges.json")
        discourse_client.badges()
        assert request.called_once

    def test_grant_badge_to(self, discourse_client, discourse_request):
        request = discourse_request("post", "/user_badges")
        discourse_client.grant_badge_to("username", 1)

        request_payload = urllib.parse.parse_qs(request.last_request.text)

        assert request_payload["username"] == ["username"]
        assert request_payload["badge_id"] == ["1"]


class TestAbout:
    def test_about(self, discourse_client, discourse_request):
        request = discourse_request("get", "/about.json")
        discourse_client.about()
        assert request.called_once
