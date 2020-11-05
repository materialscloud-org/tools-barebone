#!/usr/bin/env python
"""
Main Flask python function that manages the server backend

If you just want to try it out, just run this file and connect to
http://localhost:5000 from a browser. Otherwise, read the instructions
in README_DEPLOY.md to deploy on a Apache server.
"""
import flask
import datetime
import io
import json
import os
import traceback

from web_module import static_bp, user_static_bp, get_secret_key, get_config
from tools_barebone import get_style_version, ReverseProxied
from tools_barebone.structure_importers import get_structure_tuple, UnknownFormatError
from conf import static_folder

import logging
import logging.handlers

## Logging condfiguration
logger = logging.getLogger("tools-app")
logHandler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(os.path.split(os.path.realpath(__file__))[0], "logs", "requests.log"),
    when="midnight",
)
formatter = logging.Formatter("[%(asctime)s]%(levelname)s-%(funcName)s ^ %(message)s")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

## Create the app
app = flask.Flask(__name__, static_folder=static_folder)
app.use_x_sendfile = True
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.secret_key = get_secret_key()
# When sending static files, set the max-age to 10 seconds only (for longer, a request will be done to check the actual
# file timestamp, and decide whether to reload based on that)
app.send_file_max_age_default = datetime.timedelta(seconds=10)


def get_visualizer_select_template(request):
    if get_style_version(request) == "lite":
        return "visualizer_select_lite.html"
    return "visualizer_select.html"


@app.route("/")
def input_data():
    """
    Main view, input data selection and upload
    """
    return flask.render_template(
        get_visualizer_select_template(flask.request), **get_config()
    )


# Register blueprints
app.register_blueprint(static_bp)
app.register_blueprint(user_static_bp)

exception_message = ""

try:
    from compute import blueprint
except ImportError:
    exception_traceback = traceback.format_exc()
    blueprint = flask.Blueprint("compute", __name__, url_prefix="/compute")

    @blueprint.route("/process_structure/", methods=["GET", "POST"])
    def process_structure():
        """Template view, should be replaced when extending tools-barebone."""
        global exception_traceback

        if flask.request.method == "POST":
            # check if the post request has the file part
            if "structurefile" not in flask.request.files:
                return flask.redirect(flask.url_for("input_data"))
            structurefile = flask.request.files["structurefile"]
            fileformat = flask.request.form.get("fileformat", "unknown")
            filecontent = structurefile.read().decode("utf-8")
            fileobject = io.StringIO(str(filecontent))
            form_data = dict(flask.request.form)
            try:
                structure_tuple = get_structure_tuple(
                    fileobject, fileformat, extra_data=form_data
                )
            except UnknownFormatError:
                flask.flash("Unknown format '{}'".format(fileformat))
                return flask.redirect(flask.url_for("input_data"))
            except Exception:
                flask.flash(
                    "I tried my best, but I wasn't able to load your "
                    "file in format '{}'...".format(fileformat)
                )
                return flask.redirect(flask.url_for("input_data"))
            data_for_template = {
                "structure_json": json.dumps(
                    {
                        "cell": structure_tuple[0],
                        "atoms": structure_tuple[1],
                        "numbers": structure_tuple[2],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                "exception_traceback": exception_traceback,
            }
            return flask.render_template("tools_barebone.html", **data_for_template)

        # GET request
        flask.flash(
            "This is tools-barebone. You need to define a blueprint in a compute submodule. Import error traceback:\n{}".format(
                exception_traceback
            )
        )
        return flask.redirect(flask.url_for("input_data"))


app.register_blueprint(blueprint)


if __name__ == "__main__":
    # Don't use x-sendfile when testing it, because this is only good
    # if deployed with Apache
    # Use the local version of app, not the installed one
    app.use_x_sendfile = False
    app.run(debug=True)
