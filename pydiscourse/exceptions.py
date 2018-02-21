from requests.exceptions import HTTPError


class DiscourseError(HTTPError):
    """ A generic error while attempting to communicate with Discourse """


class DiscourseServerError(DiscourseError):
    """ The Discourse Server encountered an error while processing the request """


class DiscourseClientError(DiscourseError):
    """ An invalid request has been made """


class DiscourseRateLimitedError(DiscourseError):
        """ Request required more than the permissible number of retries """

