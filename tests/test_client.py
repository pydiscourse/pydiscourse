import sys
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from pydiscourse import client


if sys.version_info < (3,):

    def b(x):
        return x


else:
    import codecs

    def b(x):
        return codecs.latin_1_encode(x)[0]


def prepare_response(request):
    # we need to mocked response to look a little more real
    request.return_value = mock.MagicMock(
        headers={"content-type": "application/json; charset=utf-8"}
    )


class ClientBaseTestCase(unittest.TestCase):
    """

    """

    def setUp(self):
        self.host = "http://testhost"
        self.api_username = "testuser"
        self.api_key = "testkey"

        self.client = client.DiscourseClient(self.host, self.api_username, self.api_key)

    def assertRequestCalled(self, request, verb, url, **params):
        self.assertTrue(request.called)

        args, kwargs = request.call_args

        self.assertEqual(args[0], verb)
        self.assertEqual(args[1], self.host + url)

        kwargs = kwargs["params"]
        self.assertEqual(kwargs.pop("api_username"), self.api_username)
        self.assertEqual(kwargs.pop("api_key"), self.api_key)

        if verb == "GET":
            self.assertEqual(kwargs, params)


class TestClientRequests(ClientBaseTestCase):
    """
    Tests for common request handling
    """

    @mock.patch("pydiscourse.client.requests")
    def test_empty_content_http_ok(self, mocked_requests):
        """Empty content should not raise error

        Critical to test against *bytestrings* rather than unicode
        """
        mocked_response = mock.MagicMock()
        mocked_response.content = b(" ")
        mocked_response.status_code = 200
        mocked_response.headers = {"content-type": "text/plain; charset=utf-8"}

        assert "content-type" in mocked_response.headers

        mocked_requests.request = mock.MagicMock()
        mocked_requests.request.return_value = mocked_response

        resp = self.client._request("GET", "/users/admin/1/unsuspend", {})
        self.assertIsNone(resp)


@mock.patch("requests.request")
class TestUser(ClientBaseTestCase):

    def test_user(self, request):
        prepare_response(request)
        self.client.user("someuser")
        self.assertRequestCalled(request, "GET", "/users/someuser.json")

    def test_create_user(self, request):
        prepare_response(request)
        self.client.create_user(
            "Test User", "testuser", "test@example.com", "notapassword"
        )
        self.assertEqual(request.call_count, 2)

    # XXX incomplete

    def test_update_email(self, request):
        prepare_response(request)
        email = "test@example.com"
        self.client.update_email("someuser", email)
        self.assertRequestCalled(
            request, "PUT", "/users/someuser/preferences/email", email=email
        )

    def test_update_user(self, request):
        prepare_response(request)
        self.client.update_user("someuser", a="a", b="b")
        self.assertRequestCalled(request, "PUT", "/users/someuser", a="a", b="b")

    def test_update_username(self, request):
        prepare_response(request)
        self.client.update_username("someuser", "newname")
        self.assertRequestCalled(
            request, "PUT", "/users/someuser/preferences/username", username="newname"
        )

    def test_by_external_id(self, request):
        prepare_response(request)
        self.client.by_external_id(123)
        self.assertRequestCalled(request, "GET", "/users/by-external/123")

    def test_suspend_user(self, request):
        prepare_response(request)
        self.client.suspend(123, 1, "Testing")
        self.assertRequestCalled(
            request, "PUT", "/admin/users/123/suspend", duration=1, reason="Testing"
        )

    def test_unsuspend_user(self, request):
        prepare_response(request)
        self.client.unsuspend(123)
        self.assertRequestCalled(request, "PUT", "/admin/users/123/unsuspend")

    def test_user_bagdes(self, request):
        prepare_response(request)
        self.client.user_badges("username")
        self.assertRequestCalled(
            request, "GET", "/user-badges/{}.json".format("username")
        )


@mock.patch("requests.request")
class TestTopics(ClientBaseTestCase):

    def test_hot_topics(self, request):
        prepare_response(request)
        self.client.hot_topics()
        self.assertRequestCalled(request, "GET", "/hot.json")

    def test_latest_topics(self, request):
        prepare_response(request)
        self.client.latest_topics()
        self.assertRequestCalled(request, "GET", "/latest.json")

    def test_new_topics(self, request):
        prepare_response(request)
        self.client.new_topics()
        self.assertRequestCalled(request, "GET", "/new.json")

    def test_topic(self, request):
        prepare_response(request)
        self.client.topic("some-test-slug", 22)
        self.assertRequestCalled(request, "GET", "/t/some-test-slug/22.json")

    def test_topics_by(self, request):
        prepare_response(request)
        r = self.client.topics_by("someuser")
        self.assertRequestCalled(request, "GET", "/topics/created-by/someuser.json")
        self.assertEqual(r, request().json()["topic_list"]["topics"])

    def invite_user_to_topic(self, request):
        prepare_response(request)
        email = "test@example.com"
        self.client.invite_user_to_topic(email, 22)
        self.assertRequestCalled(
            request, "POST", "/t/22/invite.json", email=email, topic_id=22
        )


@mock.patch("pydiscourse.client.requests.request")
class MiscellaneousTests(ClientBaseTestCase):

    def test_search(self, request):
        prepare_response(request)
        self.client.search("needle")
        self.assertRequestCalled(request, "GET", "/search.json", term="needle")

    def test_categories(self, request):
        prepare_response(request)
        r = self.client.categories()
        self.assertRequestCalled(request, "GET", "/categories.json")
        self.assertEqual(r, request().json()["category_list"]["categories"])

    def test_users(self, request):
        prepare_response(request)
        self.client.users()
        self.assertRequestCalled(request, "GET", "/admin/users/list/active.json")

    def test_badges(self, request):
        prepare_response(request)
        self.client.badges()
        self.assertRequestCalled(request, "GET", "/admin/badges.json")

    def test_grant_badge_to(self, request):
        prepare_response(request)
        self.client.grant_badge_to("username", 1)
        self.assertRequestCalled(
            request, "POST", "/user_badges", username="username", badge_id=1
        )
