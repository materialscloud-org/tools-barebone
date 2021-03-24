"""tools-barebone module."""
import datetime
import json
from functools import wraps, update_wrapper

import flask

# tools-barebone version
__version__ = "1.1.1"

# This flag changes the style of the webpage (CSS, etc.)
# and decides whether some of the headers (e.g. the App title) and the
# description of what app can do should appear or not
#
# Options:
# - 'lite': simple version, not title, no info description, different CSS
# - anything else: default
#
# How to pass: with Apache, when forwarding, in a ReverseProxy section, add
#   RequestHeader set X-App-Style lite
def get_style_version(request):
    """Return a string with the 'style' for the app.

    - 'lite' means to remove headers and other information.
    - anything else is at the moment to be considered as the default.
    """
    return request.environ.get("HTTP_X_APP_STYLE", "")


def get_tools_barebone_version():
    """Return the version of tools-barebone."""
    return __version__


def nocache(view):
    """Add @nocache right between @app.route and the 'def' line.
    From http://arusahni.net/blog/2014/03/flask-nocache.html"""

    @wraps(view)
    def no_cache(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers["Last-Modified"] = datetime.datetime.now()
        response.headers[
            "Cache-Control"
        ] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response

    return update_wrapper(no_cache, view)


def logme(logger, *args, **kwargs):
    """
    Log information on the passed logger.

    See docstring of generate_log for more info on the
    accepted kwargs.

    :param logger: a valid logger. If you pass `None`, no log is output.
    """
    if logger is not None:
        logger.debug(generate_log(*args, **kwargs))


def generate_log(  # pylint: disable=too-many-arguments
    filecontent, fileformat, request, call_source, reason, extra=None,
):
    """
    Given a string with the file content, a file format, a Flask request and
    a string identifying the reason for logging, stores the
    correct logs.

    :param filecontent: a string with the file content
    :param fileformat: string with the file format
    :param request: a Flask request
    :param call_source: a string identifying who called the function
    :param reason: a string identifying the reason for this log
    :param extra: additional data to add to the logged dictionary.
        NOTE! it must be JSON-serializable
    """
    if extra is None:
        extra = {}

    # I don't know the fileformat
    data = {"filecontent": filecontent, "fileformat": fileformat}

    logdict = {
        "data": data,
        "reason": reason,
        "request": str(request.headers),
        "call_source": call_source,
        "source": request.headers.get("X-Forwarded-For", request.remote_addr),
        "time": datetime.datetime.now().isoformat(),
    }
    logdict.update(extra)
    return json.dumps(logdict)


class ReverseProxied:
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    Inspired by  http://flask.pocoo.org/snippets/35/

    In apache: use the following reverse proxy (adapt where needed)
    <Location /proxied>
      ProxyPass http://localhost:4444/
      ProxyPassReverse http://localhost:4444/
      RequestHeader set X-Script-Name /proxied
      RequestHeader set X-Scheme http
    </Location>

    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        server = environ.get("HTTP_X_FORWARDED_HOST", "")
        if server:
            environ["HTTP_HOST"] = server
        return self.app(environ, start_response)
