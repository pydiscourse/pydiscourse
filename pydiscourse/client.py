"""
Core API client module
"""

import logging
import time

import requests

from datetime import timedelta, datetime

from pydiscourse.exceptions import (
    DiscourseError,
    DiscourseServerError,
    DiscourseClientError,
    DiscourseRateLimitedError,
)
from pydiscourse.sso import sso_payload


log = logging.getLogger("pydiscourse.client")

# HTTP verbs to be used as non string literals
DELETE = "DELETE"
GET = "GET"
POST = "POST"
PUT = "PUT"


class DiscourseClient(object):
    """Discourse API client"""

    def __init__(self, host, api_username, api_key, timeout=None):
        """
        Initialize the client

        Args:
            host: full domain name including scheme for the Discourse API
            api_username: username to connect with
            api_key: API key to connect with
            timeout: optional timeout for the request (in seconds)

        Returns:

        """
        self.host = host
        self.api_username = api_username
        self.api_key = api_key
        self.timeout = timeout

    def user(self, username):
        """
        Get user information for a specific user

        TODO: include sample data returned
        TODO: what happens when no user is found?

        Args:
            username: username to return

        Returns:
            dict of user information

        """
        return self._get("/users/{0}.json".format(username))["user"]

    def approve(self, user_id):
        return self._get("/admin/users/{0}/approve.json".format(user_id))

    def activate(self, user_id):
        return self._put("/admin/users/{0}/activate.json".format(user_id))

    def deactivate(self, user_id):
        return self._put("/admin/users/{0}/deactivate.json".format(user_id))

    def user_all(self, user_id):
        """
        Get all user information for a specific user, needs to be admin

        Args:
            user_id: id of the user to return
        Returns:
            dict of user information
        """
        return self._get("/admin/users/{0}.json".format(user_id))

    def invite(self, email, group_names, custom_message, **kwargs):
        """
        Invite a user by email to join your forum

        Args:
            email: their email, will be used for activation and summary emails
            group_names: the group names
            custom_message: message to include
            **kwargs: ???? what else can be sent through?

        Returns:
            API response body (dict)

        """
        return self._post(
            "/invites",
            email=email,
            group_names=group_names,
            custom_message=custom_message,
            **kwargs
        )

    def invite_link(self, email, group_names, custom_message, **kwargs):
        """
        Generate an invite link for a user to join your forum

        Args:
            email: their email, will be used for activation and summary emails
            group_names: the group names
            custom_message: message to include
            **kwargs: ???? what else can be sent through?

        Returns:
            Invite link

        """
        return self._post(
            "/invites/link",
            email=email,
            group_names=group_names,
            custom_message=custom_message,
            **kwargs
        )

    def create_user(self, name, username, email, password, **kwargs):
        """
        Create a Discourse user

        Set keyword argument active='true' to avoid sending activation emails

        TODO: allow optional password and generate a random one

        Args:
            name: the full name of the new user
            username: their username (this is a key... that they can change)
            email: their email, will be used for activation and summary emails
            password: their initial password
            **kwargs: ???? what else can be sent through?

        Returns:
            ????

        """
        r = self._get("/users/hp.json")
        challenge = r["challenge"][::-1]  # reverse challenge, discourse security check
        confirmations = r["value"]
        return self._post(
            "/users",
            name=name,
            username=username,
            email=email,
            password=password,
            password_confirmation=confirmations,
            challenge=challenge,
            **kwargs
        )

    def user_by_external_id(self, external_id):
        """

        Args:
            external_id:

        Returns:

        """
        response = self._get("/users/by-external/{0}".format(external_id))
        return response["user"]

    by_external_id = user_by_external_id

    def log_out(self, userid):
        """

        Args:
            userid:

        Returns:

        """
        return self._post("/admin/users/{0}/log_out".format(userid))

    def trust_level(self, userid, level):
        """

        Args:
            userid:
            level:

        Returns:

        """
        return self._put("/admin/users/{0}/trust_level".format(userid), level=level)

    def suspend(self, userid, duration, reason):
        """
        Suspend a user's account

        Args:
            userid: the Discourse user ID
            duration: the length of time in days for which a user's account
                    should be suspended
            reason: the reason for suspending the account

        Returns:
            ????

        """
        suspend_until = (datetime.now() + timedelta(days=duration)).isoformat()
        return self._put(
            "/admin/users/{0}/suspend".format(userid),
            suspend_until=suspend_until,
            reason=reason,
        )

    def unsuspend(self, userid):
        """
        Unsuspends a user's account

        Args:
            userid: the Discourse user ID

        Returns:
            None???
        """
        return self._put("/admin/users/{0}/unsuspend".format(userid))

    def list_users(self, type, **kwargs):
        """

        optional user search: filter='test@example.com' or filter='scott'

        Args:
            type:
            **kwargs:

        Returns:

        """
        return self._get("/admin/users/list/{0}.json".format(type), **kwargs)

    def update_avatar_from_url(self, username, url, **kwargs):
        """

        Args:
            username:
            url:
            **kwargs:

        Returns:

        """
        return self._post(
            "/users/{0}/preferences/avatar".format(username), file=url, **kwargs
        )

    def update_avatar_image(self, username, img, **kwargs):
        """

        Specify avatar using a URL

        Args:
            username:
            img:
            **kwargs:

        Returns:

        """
        files = {"file": img}
        return self._post(
            "/users/{0}/preferences/avatar".format(username), files=files, **kwargs
        )

    def toggle_gravatar(self, username, state=True, **kwargs):
        """

        Args:
            username:
            state:
            **kwargs:

        Returns:

        """
        url = "/users/{0}/preferences/avatar/toggle".format(username)
        if bool(state):
            kwargs["use_uploaded_avatar"] = "true"
        else:
            kwargs["use_uploaded_avatar"] = "false"
        return self._put(url, **kwargs)

    def pick_avatar(self, username, gravatar=True, generated=False, **kwargs):
        """

        Args:
            username:
            gravatar:
            generated:
            **kwargs:

        Returns:

        """
        url = "/users/{0}/preferences/avatar/pick".format(username)
        return self._put(url, **kwargs)

    def update_avatar(self, username, url, **kwargs):
        """

        Args:
            username:
            url:
            **kwargs:

        Returns:

        """
        kwargs["type"] = "avatar"
        kwargs["synchronous"] = "true"
        upload_response = self._post("/uploads", url=url, **kwargs)
        return self._put(
            "/users/{0}/preferences/avatar/pick".format(username),
            upload_id=upload_response["id"],
            **kwargs
        )

    def update_email(self, username, email, **kwargs):
        """

        Args:
            username:
            email:
            **kwargs:

        Returns:

        """
        return self._put(
            "/users/{0}/preferences/email".format(username), email=email, **kwargs
        )

    def update_user(self, username, **kwargs):
        """

        Args:
            username:
            **kwargs:

        Returns:

        """
        return self._put("/users/{0}".format(username), json=True, **kwargs)

    def update_username(self, username, new_username, **kwargs):
        """

        Args:
            username:
            new_username:
            **kwargs:

        Returns:

        """
        return self._put(
            "/users/{0}/preferences/username".format(username),
            username=new_username,
            **kwargs
        )

    def set_preference(self, username=None, **kwargs):
        """

        Args:
            username:
            **kwargs:

        Returns:

        """
        if username is None:
            username = self.api_username
        return self._put(u"/users/{0}".format(username), **kwargs)

    def sync_sso(self, **kwargs):
        """

        expect sso_secret, name, username, email, external_id, avatar_url,
        avatar_force_update

        Args:
            **kwargs:

        Returns:

        """
        sso_secret = kwargs.pop("sso_secret")
        payload = sso_payload(sso_secret, **kwargs)
        return self._post("/admin/users/sync_sso?{0}".format(payload), **kwargs)

    def generate_api_key(self, userid, **kwargs):
        """

        Args:
            userid:
            **kwargs:

        Returns:

        """
        return self._post("/admin/users/{0}/generate_api_key".format(userid), **kwargs)

    def delete_user(self, userid, **kwargs):
        """

            block_email='true'
            block_ip='false'
            block_urls='false'

        Args:
            userid:
            **kwargs:

        Returns:

        """
        return self._delete("/admin/users/{0}.json".format(userid), **kwargs)

    def users(self, filter=None, **kwargs):
        """

        Args:
            filter:
            **kwargs:

        Returns:

        """
        if filter is None:
            filter = "active"

        return self._get("/admin/users/list/{0}.json".format(filter), **kwargs)

    def private_messages(self, username=None, **kwargs):
        """

        Args:
            username:
            **kwargs:

        Returns:

        """
        if username is None:
            username = self.api_username
        return self._get("/topics/private-messages/{0}.json".format(username), **kwargs)

    def private_messages_unread(self, username=None, **kwargs):
        """

        Args:
            username:
            **kwargs:

        Returns:

        """
        if username is None:
            username = self.api_username
        return self._get(
            "/topics/private-messages-unread/{0}.json".format(username), **kwargs
        )

    def category_topics(self, category_id, **kwargs):
        """
        Returns a list of all topics in a category.

        Args:
            **kwargs:

        Returns:
            JSON API response

        """
        return self._get(
            "/c/{0}.json".format(category_id),
            override_request_kwargs={"allow_redirects": True},
            **kwargs
        )

    def hot_topics(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        return self._get("/hot.json", **kwargs)

    def latest_topics(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        return self._get("/latest.json", **kwargs)

    def new_topics(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        return self._get("/new.json", **kwargs)

    def topic(self, slug, topic_id, **kwargs):
        """

        Args:
            slug:
            topic_id:
            **kwargs:

        Returns:

        """
        return self._get("/t/{0}/{1}.json".format(slug, topic_id), **kwargs)

    def delete_topic(self, topic_id, **kwargs):
        """
        Remove a topic

        Args:
            category_id:
            **kwargs:

        Returns:
            JSON API response

        """
        return self._delete(u"/t/{0}".format(topic_id), **kwargs)

    def post(self, topic_id, post_id, **kwargs):
        """

        Args:
            topic_id:
            post_id:
            **kwargs:

        Returns:

        """
        return self._get("/t/{0}/{1}.json".format(topic_id, post_id), **kwargs)

    def posts(self, topic_id, post_ids=None, **kwargs):
        """
        Get a set of posts from a topic

        Args:
            topic_id:
            post_ids: a list of post ids from the topic stream
            **kwargs:

        Returns:

        """
        if post_ids:
            kwargs["post_ids[]"] = post_ids
        return self._get("/t/{0}/posts.json".format(topic_id), **kwargs)

    def topic_timings(self, topic_id, time, timings={}, **kwargs):
        """
        Set time spent reading a post

        A side effect of this is to mark the post as read

        Args:
            topic_id: { post_number: ms }
            time: overall time for the topic (in what unit????)
            timings:
            **kwargs:

        Returns:

        """
        kwargs["topic_id"] = topic_id
        kwargs["topic_time"] = time
        for post_num, timing in timings.items():
            kwargs["timings[{0}]".format(post_num)] = timing

        return self._post("/topics/timings", **kwargs)

    def topic_posts(self, topic_id, **kwargs):
        """

        Args:
            topic_id:
            **kwargs:

        Returns:

        """
        return self._get("/t/{0}/posts.json".format(topic_id), **kwargs)

    def update_topic(self, topic_url, title, **kwargs):
        """
        Update a topic

        Args:
            topic_url:
            title:
            **kwargs:

        Returns:

        """
        kwargs["title"] = title
        return self._put("{}".format(topic_url), **kwargs)

    def create_post(
        self, content, category_id=None, topic_id=None, title=None, tags=[], **kwargs
    ):
        """

        Args:
            content:
            category_id:
            topic_id:
            title:
            tags:
            **kwargs:

        Returns:

        """
        if tags:
            kwargs["tags[]"] = tags
        return self._post(
            "/posts",
            category=category_id,
            title=title,
            raw=content,
            topic_id=topic_id,
            **kwargs
        )

    def update_topic_status(self, topic_id, status, enabled, **kwargs):
        """
        Open or close a topic

        Args:
            topic_id:
            status:
            enabled:
            **kwargs:

        Returns:

        """
        kwargs["status"] = status
        if bool(enabled):
            kwargs["enabled"] = "true"
        else:
            kwargs["enabled"] = "false"
        return self._put("/t/{0}/status".format(topic_id), **kwargs)

    def update_post(self, post_id, content, edit_reason="", **kwargs):
        """

        Args:
            post_id:
            content:
            edit_reason:
            **kwargs:

        Returns:

        """
        kwargs["post[raw]"] = content
        kwargs["post[edit_reason]"] = edit_reason
        return self._put("/posts/{0}".format(post_id), **kwargs)

    def topics_by(self, username, **kwargs):
        """

        Args:
            username:
            **kwargs:

        Returns:

        """
        url = "/topics/created-by/{0}.json".format(username)
        return self._get(url, **kwargs)["topic_list"]["topics"]

    def invite_user_to_topic(self, user_email, topic_id):
        """

        Args:
            user_email:
            topic_id:

        Returns:

        """
        kwargs = {"email": user_email, "topic_id": topic_id}
        return self._post("/t/{0}/invite.json".format(topic_id), **kwargs)

    def search(self, term, **kwargs):
        """

        Args:
            term:
            **kwargs:

        Returns:

        """
        kwargs["term"] = term
        return self._get("/search.json", **kwargs)

    def badges(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        return self._get("/admin/badges.json", **kwargs)

    def grant_badge_to(self, username, badge_id, **kwargs):
        """

        Args:
            username:
            badge_id:
            **kwargs:

        Returns:

        """
        return self._post(
            "/user_badges", username=username, badge_id=badge_id, **kwargs
        )

    def user_badges(self, username, **kwargs):
        """

        Args:
            username:

        Returns:

        """
        return self._get("/user-badges/{}.json".format(username))

    def user_emails(self, username, **kwargs):
        """
        Retrieve list of users email addresses

        Args:
            username:

        Returns:

        """
        return self._get("/u/{}/emails.json".format(username))

    def create_category(
        self, name, color, text_color="FFFFFF", permissions=None, parent=None, **kwargs
    ):
        """

        Args:
            name:
            color:
            text_color: hex color without number symbol
            permissions: dict of 'everyone', 'admins', 'moderators', 'staff' with values of ???
            parent: name of the category
            parent_category_id:
            **kwargs:

        Returns:

        """
        kwargs["name"] = name
        kwargs["color"] = color
        kwargs["text_color"] = text_color

        if permissions is None and "permissions" not in kwargs:
            permissions = {"everyone": "1"}

        for key, value in permissions.items():
            kwargs["permissions[{0}]".format(key)] = value

        if parent:
            parent_id = None
            for category in self.categories():
                if category["name"] == parent:
                    parent_id = category["id"]
                    continue

            if not parent_id:
                raise DiscourseClientError(u"{0} not found".format(parent))

            kwargs["parent_category_id"] = parent_id

        return self._post("/categories", **kwargs)

    def categories(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        return self._get("/categories.json", **kwargs)["category_list"]["categories"]

    def category(self, name, parent=None, **kwargs):
        """

        Args:
            name:
            parent:
            **kwargs:

        Returns:

        """
        if parent:
            name = u"{0}/{1}".format(parent, name)

        return self._get(u"/category/{0}.json".format(name), **kwargs)

    def delete_category(self, category_id, **kwargs):
        """
        Remove category

        Args:
            category_id:
            **kwargs:

        Returns:

        """
        return self._delete(u"/categories/{0}".format(category_id), **kwargs)

    def site_settings(self, **kwargs):
        """

        Args:
            settings:
            **kwargs:

        Returns:

        """
        for setting, value in kwargs.items():
            setting = setting.replace(" ", "_")
            self._request(
                PUT, "/admin/site_settings/{0}".format(setting), {setting: value}
            )

    def customize_site_texts(self, site_texts, **kwargs):
        """
        Set Text Content for site

        Args:
            site_texts:
            **kwargs:

        Returns:

        """
        for site_text, value in site_texts.items():
            kwargs = {"site_text": {"value": value}}
            self._put(
                "/admin/customize/site_texts/{0}".format(site_text), json=True, **kwargs
            )

    def groups(self, **kwargs):
        """
        Returns a list of all groups.

        Returns:
            List of dictionaries of groups

                [
                  {
                    'alias_level': 0,
                    'automatic': True,
                    'automatic_membership_email_domains': None,
                    'automatic_membership_retroactive': False,
                    'grant_trust_level': None,
                    'has_messages': True,
                    'id': 1,
                    'incoming_email': None,
                    'mentionable': False,
                    'name': 'admins',
                    'notification_level': 2,
                    'primary_group': False,
                    'title': None,
                    'user_count': 9,
                    'visible': True
                  },
                  {
                    'alias_level': 0,
                    'automatic': True,
                    'automatic_membership_email_domains': None,
                    'automatic_membership_retroactive': False,
                    'grant_trust_level': None,
                    'has_messages': False,
                    'id': 0,
                    'incoming_email': None,
                    'mentionable': False,
                    'name': 'everyone',
                    'notification_level': None,
                    'primary_group': False,
                    'title': None,
                    'user_count': 0,
                    'visible': True
                  }
                ]

        """
        return self._get("/groups/search.json", **kwargs)

    def group(self, group_name):
        """
        Get all infos of a group by group name
        """
        return self._get("/groups/{0}/members.json".format(group_name))

    def create_group(
        self,
        name,
        title="",
        visible=True,
        alias_level=0,
        automatic_membership_retroactive=False,
        primary_group=False,
        automatic=False,
        automatic_membership_email_domains="",
        grant_trust_level=1,
        flair_url=None,
        flair_bg_color=None,
        flair_color=None,
        **kwargs
    ):
        """
        Args:

            name: name of the group
            title: "" (title of the member of this group)
            visible: true
            alias_level: 0
            automatic_membership_retroactive: false
            primary_group: false
            automatic: false
            automatic_membership_email_domains: ""
            grant_trust_level: 1
            flair_url: Avatar Flair Image
            flair_bg_color: Avatar Flair Background Color
            flair_color: Avatar Flair Color

        """
        kwargs["name"] = name
        kwargs["title"] = title
        kwargs["visible"] = visible
        kwargs["alias_level"] = alias_level
        kwargs["automatic_membership_retroactive"] = automatic_membership_retroactive
        kwargs["primary_group"] = primary_group
        kwargs["automatic"] = automatic
        kwargs[
            "automatic_membership_email_domains"
        ] = automatic_membership_email_domains
        kwargs["grant_trust_level"] = grant_trust_level
        kwargs["flair_url"] = flair_url
        kwargs["flair_bg_color"] = flair_bg_color
        kwargs["flair_color"] = flair_color
        # Discourse v.1.7.0
        kwargs = {"group": kwargs}

        return self._post("/admin/groups", json=True, **kwargs)

    def delete_group(self, groupid):
        """
        Deletes a group by its ID

        Args:
            groupid: the ID of the group

        Returns:
            JSON API response

        """
        return self._delete("/admin/groups/{0}.json".format(groupid))

    def add_group_owner(self, groupid, username):
        """
        Add an owner to a group by username

        Args:
            groupid: the ID of the group
            username: the new owner usernmae

        Returns:
            JSON API response

        """
        return self._put(
            "/admin/groups/{0}/owners.json".format(groupid), usernames=username
        )

    def delete_group_owner(self, groupid, userid):
        """
        Deletes an owner from a group by user ID

        Does not delete the user from Discourse.

        Args:
            groupid: the ID of the group
            userid: the ID of the user

        Returns:
            JSON API response

        """
        return self._delete(
            "/admin/groups/{0}/owners.json".format(groupid), user_id=userid
        )

    def group_owners(self, group_name):
        """
        Get all owners of a group by group name
        """
        group = self._get("/groups/{0}/members.json".format(group_name))
        return group["owners"]

    def group_members(self, group_name, offset=0, **kwargs):
        """
        Get all members of a group by group name
        """
        kwargs["offset"] = offset
        group = self._get("/groups/{0}/members.json".format(group_name), **kwargs)
        return group["members"]

    def add_group_member(self, groupid, username):
        """
        Add a member to a group by username

        Args:
            groupid: the ID of the group
            username: the new member usernmae

        Returns:
            JSON API response

        Raises:
            DiscourseError if user is already member of group

        """
        return self._put(
            "/admin/groups/{0}/members.json".format(groupid), usernames=username
        )

    def add_group_members(self, groupid, usernames):
        """
        Add a list of members to a group by usernames

        Args:
            groupid: the ID of the group
            usernames: the list of new member usernames

        Returns:
            JSON API response

        Raises:
            DiscourseError if any of the users is already member of group

        """
        usernames = ",".join(usernames)
        return self._put(
            "/admin/groups/{0}/members.json".format(groupid), usernames=usernames
        )

    def add_user_to_group(self, groupid, userid):
        """
        Add a member to a group by with user id.

        Args:
            groupid: the ID of the group
            userid: the member id

        Returns:
            JSON API response

        Raises:
            DiscourseError if user is already member of group

        """
        return self._post("/admin/users/{0}/groups".format(userid), group_id=groupid)

    def delete_group_member(self, groupid, userid):
        """
        Deletes a member from a group by user ID

        Does not delete the user from Discourse.

        Args:
            groupid: the ID of the group
            userid: the ID of the user

        Returns:
            JSON API response

        """
        return self._delete(
            "/admin/groups/{0}/members.json".format(groupid), user_id=userid
        )

    def color_schemes(self, **kwargs):
        """
        List color schemes in site

        Args:
            **kwargs:

        Returns:

        """
        return self._get("/admin/color_schemes.json", **kwargs)

    def create_color_scheme(self, name, enabled, colors, **kwargs):
        """
        Create new color scheme

        Args:
            name:
            enabled:
            colors:
            **kwargs:

        Returns:

        """
        kwargs["name"] = name
        if bool(enabled):
            kwargs["enabled"] = "true"
        else:
            kwargs["enabled"] = "false"
        kwargs["colors"] = [
            {"name": name, "hex": color} for name, color in colors.items()
        ]
        kwargs = {"color_scheme": kwargs}
        return self._post("/admin/color_schemes.json", json=True, **kwargs)

    def create_site_customization(self, name, enabled, stylesheet, **kwargs):
        """
        Add a new Theme

        Args:
            name:
            enabled:
            stylesheet:
            **kwargs:

        Returns:

        """
        kwargs["name"] = name
        if bool(enabled):
            kwargs["enabled"] = "true"
        else:
            kwargs["enabled"] = "false"
        kwargs["stylesheet"] = stylesheet
        kwargs = {"site_customization": kwargs}
        return self._post("/admin/site_customizations", json=True, **kwargs)

    def trust_level_lock(self, user_id, locked, **kwargs):
        """
        Lock user to current trust level

        Args:
            user_id:
            locked:
            **kwargs:

        Returns:

        """
        if bool(locked):
            kwargs["locked"] = "true"
        else:
            kwargs["locked"] = "false"
        return self._put("/admin/users/{}/trust_level_lock".format(user_id), **kwargs)

    def block(self, user_id, **kwargs):
        """
        Prevent user from creating topics or replying to posts.
        To prevent users logging in use suspend()

        Args:
            userid:

        Returns:

        """
        return self._put("/admin/users/{}/block".format(user_id), **kwargs)

    def upload_image(self, image, type, synchronous, **kwargs):
        """
        Upload image or avatar

        Args:
            name:
            file:
            type:
            synchronous:
            **kwargs:

        Returns:

        """
        kwargs["type"] = type
        if bool(synchronous):
            kwargs["synchronous"] = "true"
        else:
            kwargs["synchronous"] = "false"
        files = {"file": open(image, "rb")}
        return self._post("/uploads.json", files=files, **kwargs)

    def user_actions(self, username, filter, offset=0, **kwargs):
        """
        List all possible user actions

        Args:
            username:
            filter:
            **kwargs:

        Returns:

        """
        kwargs["username"] = username
        kwargs["filter"] = filter
        kwargs["offset"] = offset
        return self._get("/user_actions.json", **kwargs)["user_actions"]

    def tag_group(self, name, tag_names, parent_tag_name=None, **kwargs):
        """
        Create a new tag group

        Args:
            name:
            tag_names:
            parent_tag_name:
            **kwargs:

        Returns:

        """
        kwargs["name"] = name
        kwargs["tag_names"] = tag_names
        kwargs["parent_tag_name"] = parent_tag_name
        return self._post("/tag_groups", json=True, **kwargs)["tag_group"]

    def _get(self, path, override_request_kwargs=None, **kwargs):
        """

        Args:
            path:
            **kwargs:

        Returns:

        """
        return self._request(GET, path, params=kwargs, override_request_kwargs=override_request_kwargs)

    def _put(self, path, json=False, override_request_kwargs=None, **kwargs):
        """

        Args:
            path:
            **kwargs:

        Returns:

        """
        if not json:
            return self._request(PUT, path, data=kwargs, override_request_kwargs=override_request_kwargs)

        else:
            return self._request(PUT, path, json=kwargs, override_request_kwargs=override_request_kwargs)

    def _post(self, path, files=None, json=False, override_request_kwargs=None, **kwargs):
        """

        Args:
            path:
            **kwargs:

        Returns:

        """
        if not json:
            return self._request(POST, path, files=files, data=kwargs, override_request_kwargs=override_request_kwargs)

        else:
            return self._request(POST, path, files=files, json=kwargs, override_request_kwargs=override_request_kwargs)

    def _delete(self, path, override_request_kwargs=None, **kwargs):
        """

        Args:
            path:
            **kwargs:

        Returns:

        """
        return self._request(DELETE, path, params=kwargs, override_request_kwargs=override_request_kwargs)

    def _request(
        self, verb, path, params=None, files=None, data=None, json=None, override_request_kwargs=None
    ):
        """
        Executes HTTP request to API and handles response

        Args:
            verb: HTTP verb as string: GET, DELETE, PUT, POST
            path: the path on the Discourse API
            params: dictionary of parameters to include to the API
            override_request_kwargs: dictionary of requests.request keyword arguments to override defaults

        Returns:
            dictionary of response body data or None

        """
        params = params or {}
        files = files or {}
        data = data or {}
        json = json or {}
        override_request_kwargs = override_request_kwargs or {}

        url = self.host + path

        headers = {
            "Accept": "application/json; charset=utf-8",
            "Api-Key": self.api_key,
            "Api-Username": self.api_username,
        }

        # How many times should we retry if rate limited
        retry_count = 4
        # Extra time (on top of that required by API) to wait on a retry.
        retry_backoff = 1

        while retry_count > 0:
            request_kwargs = dict(
                allow_redirects=False,
                params=params,
                files=files,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout,
            )

            request_kwargs.update(override_request_kwargs)

            response = requests.request(verb, url, **request_kwargs)

            log.debug("response %s: %s", response.status_code, repr(response.text))
            if response.ok:
                break
            if not response.ok:
                try:
                    msg = u",".join(response.json()["errors"])
                except (ValueError, TypeError, KeyError):
                    if response.reason:
                        msg = response.reason
                    else:
                        msg = u"{0}: {1}".format(response.status_code, response.text)

                if 400 <= response.status_code < 500:
                    if 429 == response.status_code:
                        # This codepath relies on wait_seconds from Discourse v2.0.0.beta3 / v1.9.3 or higher.
                        rj = response.json()
                        wait_delay = (
                            retry_backoff + rj["extras"]["wait_seconds"]
                        )  # how long to back off for.

                        if retry_count > 1:
                            time.sleep(wait_delay)
                        retry_count -= 1
                        log.info(
                            "We have been rate limited and waited {0} seconds ({1} retries left)".format(
                                wait_delay, retry_count
                            )
                        )
                        log.debug("API returned {0}".format(rj))
                        continue
                    else:
                        raise DiscourseClientError(msg, response=response)

                # Any other response.ok resulting in False
                raise DiscourseServerError(msg, response=response)

        if retry_count == 0:
            raise DiscourseRateLimitedError(
                "Number of rate limit retries exceeded. Increase retry_backoff or retry_count",
                response=response,
            )

        if response.status_code == 302:
            raise DiscourseError(
                "Unexpected Redirect, invalid api key or host?", response=response
            )

        json_content = "application/json; charset=utf-8"
        content_type = response.headers["content-type"]
        if content_type != json_content:
            # some calls return empty html documents
            if not response.content.strip():
                return None

            raise DiscourseError(
                'Invalid Response, expecting "{0}" got "{1}"'.format(
                    json_content, content_type
                ),
                response=response,
            )

        try:
            decoded = response.json()
        except ValueError:
            raise DiscourseError("failed to decode response", response=response)

        if "errors" in decoded:
            message = decoded.get("message")
            if not message:
                message = u",".join(decoded["errors"])
            raise DiscourseError(message, response=response)

        return decoded
