"""
Most of the functions needed by the web service are here.
In run_app.py we just keep the main web logic.
"""
import os
from collections import OrderedDict

import yaml
import flask
from flask import Blueprint

from conf import (
    directory,
    static_folder,
    user_static_folder,
    config_file_path,
    ConfigurationError,
)

# Key: internal value; value: string to show
upload_structure_block_known_formats = OrderedDict(
    {
        "qeinp-qetools": "Quantum ESPRESSO input [parser: qe-tools]",
        "vasp-ase": "VASP POSCAR [parser: ase]",
        "xsf-ase": "XCrySDen (.xsf) [parser: ase]",
        "castep-ase": "CASTEP (.cell) [parser: ase]",
        "pdb-ase": "Protein Data Bank format (.pdb) [parser: ase]",
        "xyz-ase": "XYZ File (.xyz) [parser: ase]",
        "cif-ase": "CIF File (.cif) [parser: ase]",
        "cif-pymatgen": "CIF File (.cif) [parser: pymatgen]",
    }
)


def get_secret_key():
    try:
        with open(os.path.join(directory, "SECRET_KEY")) as f:
            secret_key = f.readlines()[0].strip()
            if len(secret_key) < 16:
                raise ValueError
            return secret_key
    except Exception:
        raise ConfigurationError(
            "Please create a SECRET_KEY file in {} with a random string "
            "of at least 16 characters".format(directory)
        )


def parse_config(config):
    default_templates_folder = "default_templates"
    user_templates_folder = "user_templates"
    retdict = {}

    templates = config.get("templates", {})

    known_templates = [
        "how_to_cite",
        "about",
        "select_content",
        "upload_structure_additional_content",
    ]

    for template_name in known_templates:
        # Note that this still allows to set it to None explicitly to skip this section
        try:
            retdict[template_name] = templates[template_name]
            if retdict[template_name] is not None:
                retdict[template_name] = os.path.join(
                    user_templates_folder, retdict[template_name]
                )
        except KeyError:
            retdict[template_name] = os.path.join(
                default_templates_folder, "{}.html".format(template_name)
            )

    for template_name in templates:
        if (
            template_name not in known_templates
            and templates[template_name] is not None
        ):
            retdict[template_name] = os.path.join(
                user_templates_folder, templates[template_name]
            )

    additional_accordion_entries = config.get("additional_accordion_entries", [])
    retdict["additional_accordion_entries"] = []
    for accordian_entry in additional_accordion_entries:
        retdict["additional_accordion_entries"].append(
            {
                "header": accordian_entry["header"],
                "template_page": os.path.join(
                    user_templates_folder, accordian_entry["template_page"]
                ),
            }
        )

    return retdict


def set_config_defaults(config):
    """Add defaults so the site works"""
    new_config = config.copy()

    new_config.setdefault("window_title", "Materials Cloud Tool")
    new_config.setdefault(
        "page_title",
        "<PLEASE SPECIFY A PAGE_TITLE AND A WINDOW_TITLE IN THE CONFIG FILE>",
    )

    new_config.setdefault("custom_css_files", {})
    new_config.setdefault("custom_js_files", {})
    new_config.setdefault("templates", {})

    return new_config


def get_config():
    try:
        with open(config_file_path) as config_file:
            config = yaml.safe_load(config_file)
    except IOError as exc:
        if exc.errno == 2:  # No such file or directory
            config = {}
        else:
            raise

    # set defaults
    config = set_config_defaults(config)

    return {
        "config": config,
        "include_pages": parse_config(config),
        "upload_structure_block_known_formats": upload_structure_block_known_formats,
    }


static_bp = Blueprint("static", __name__, url_prefix="/static")
user_static_bp = Blueprint("user_static", __name__, url_prefix="/user_static")


@static_bp.route("/js/<path:path>")
def send_js(path):
    """
    Serve static JS files
    """
    return flask.send_from_directory(os.path.join(static_folder, "js"), path)


@user_static_bp.route("/js/<path:path>")
def send_custom_js(path):
    """
    Serve static JS files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, "js"), path)


@static_bp.route("/img/<path:path>")
def send_img(path):
    """
    Serve static image files
    """
    return flask.send_from_directory(os.path.join(static_folder, "img"), path)


@user_static_bp.route("/img/<path:path>")
def send_custom_img(path):
    """
    Serve static image files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, "img"), path)


@static_bp.route("/css/<path:path>")
def send_css(path):
    """
    Serve static CSS files
    """
    return flask.send_from_directory(os.path.join(static_folder, "css"), path)


@user_static_bp.route("/css/<path:path>")
def send_custom_css(path):
    """
    Serve static CSS files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, "css"), path)


@user_static_bp.route("/data/<path:path>")
def send_custom_data(path):
    """
    Serve static font files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, "data"), path)


@static_bp.route("/css/images/<path:path>")
def send_cssimages(path):
    """
    Serve static CSS images files
    """
    return flask.send_from_directory(os.path.join(static_folder, "css", "images"), path)


@user_static_bp.route("/css/images/<path:path>")
def send_custom_cssimages(path):
    """
    Serve static CSS images files
    """
    return flask.send_from_directory(
        os.path.join(user_static_folder, "css", "images"), path
    )


@static_bp.route("/fonts/<path:path>")
def send_fonts(path):
    """
    Serve static font files
    """
    return flask.send_from_directory(os.path.join(static_folder, "fonts"), path)


@user_static_bp.route("/fonts/<path:path>")
def send_custom_fonts(path):
    """
    Serve static font files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, "fonts"), path)
