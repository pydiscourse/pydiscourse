===========
pydiscourse
===========

.. image:: https://github.com/bennylope/pydiscourse/workflows/Tests/badge.svg
    :alt: Build Status
    :target: https://github.com/bennylope/pydiscourse/actions

.. image:: https://img.shields.io/badge/Check%20out%20the-Docs-blue.svg
    :alt: Check out the Docs
    :target: https://discourse.readthedocs.io/en/latest/


A Python library for working with Discourse.

This is a fork of the original Tindie version. It was forked to include fixes,
additional functionality, and to distribute a package on PyPI.

Goals
=====

* Exceptional documentation
* Support all supported Python versions
* Provide functional parity with the Discourse API, for the currently supported
  version of Discourse (something of a moving target)

The order here is important. The Discourse API is itself poorly documented so
the level of documentation in the Python client is critical.

Installation
============

::

    pip install pydiscourse

Examples
========

Create a client connection to a Discourse server::

    from pydiscourse import DiscourseClient
    client = DiscourseClient(
            'http://example.com',
            api_username='username',
            api_key='areallylongstringfromdiscourse')

Get info about a user::

    user = client.user('eviltrout')
    print user

    user_topics = client.topics_by('johnsmith')
    print user_topics

Create a new user::

    user = client.create_user('The Black Knight', 'blacknight', 'knight@python.org', 'justafleshwound')

Implement SSO for Discourse with your Python server::

    @login_required
    def discourse_sso_view(request):
        payload = request.GET.get('sso')
        signature = request.GET.get('sig')
        nonce = sso_validate(payload, signature, SECRET)
        url = sso_redirect_url(nonce, SECRET, request.user.email, request.user.id, request.user.username)
        return redirect('http://discuss.example.com' + url)

Command line
============

To help experiment with the Discourse API, pydiscourse provides a simple command line client::

    export DISCOURSE_API_KEY=your_master_key
    pydiscoursecli --host-http://yourhost --api-user-system latest_topics
    pydiscoursecli --host-http://yourhost --api-user-system topics_by johnsmith
    pydiscoursecli --host-http://yourhost --api-user-system user eviltrout
