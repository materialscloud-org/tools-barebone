# tools-barebone

[![Actions Status](https://github.com/materialscloud-org/tools-barebone/workflows/Continuous%20integration/badge.svg)](https://github.com/materialscloud-org/tools-barebone/actions)


`tools-barebone` is a framework to develop and deploy small web applications,
implemented in Python using Flask Jinja2 templates.

It can be used as a starting point to develop new tools for the
[Materials Cloud Tools section](https://www.materialscloud.org/work/tools/options).

It provides:

- A common layout used for every tool in Materials cloud
- The Materials Cloud theme
- Common API endpoints
- Common widgets, e.g., file upload functionality for crystal structures
- Web server settings
- Scripts to deploy the tool in a docker container

## Prerequisites

- [docker](https://www.docker.com/) >= v18.09

## How to use a tools-barebone framework

The `tools-barebone` framework provides basic templates, that can be extended to develop
a new tool for Materials Cloud.

Here we briefly explain how the `tools-barebone` template (shown
on the left side of the figure below) can be extended to develop a new tool called `custom-tool`
(shown on the right side).

|                                            Tools barebone template                                             |                                               New tool template                                               |
| :------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------: |
| ![](https://github.com/materialscloud-org/tools-barebone/blob/master/misc/screenshots/tools-barebone.png) | ![](https://github.com/materialscloud-org/tools-barebone/blob/master/misc/screenshots/tools-example.png) |

### 1. Get the most recent `tools-barebone` docker image from DockerHub

Browse to the [Tags page on DockerHub for materialscloud/tools-barebone](https://hub.docker.com/repository/docker/materialscloud/tools-barebone/tags?page=1) and find the most recent tagged version (in the form `X.Y.Z`, e.g. 1.0.0). You can also use the `latest` tag, but we strongly suggest that you use a pinned version, rather than latest: this will ensure that your tool will continue to work also if future, incompatible versions are released.

Then, run the following command to get the image:
```
docker pull materialscloud/tools-barebone
```

You can try to see if everything works by running a container from this image, e.g. by running
```
docker run -p 8090:80 materialscloud/tools-barebone:latest
```
and then connecting to http://localhost:8090 with your browser.

You should see a website similar to the image on the left above.

If you want, you can also install the tools-barebone package (use the same version as the one you picked above) using
```
pip install tools-barebone==X.Y.Z
```

This is not technically required, but it is useful e.g. if your editor has inspection capabilities and needs to see the package, or if you are using a linter.

### 2. New tool: `custom-tool`

To write the new tool called `custom-tool`, create a new directory `custom-tool`. Let us first create the minimum set of files required
in this new tool:

```(bash)
mkdir custom-tool
cd custom-tool

# create configuration file
touch config.yaml

# create Dockerfile file
touch Dockerfile

# create file for python requirements
touch requirements.txt

# create the folder in which you will put the
# python code for the backend
mkdir compute
touch compute/__init__.py

# create user templates folder
mkdir user_templates
cd user_templates
touch ack.html                              # add acknowledgement text here
touch about.html                            # add information about this tool here
touch how_to_cite.html                      # add tool citation here
touch additional_content.html               # additional functionality if any, otherwise empty file

```

### 3. Configuration settings

The `config.yaml` file contains the configuration details used in this new tool like window title,
page title, list of html templates, etc. Update the `config.yaml` file and add HTML templates
that will be shown in the section about the tool, for tool citation text and for the acknowledgements.

As an example of the most common variables to be set in the `config.yaml` file, we provide here an example
here below:

```(bash)
window_title: "Materials Cloud Tools: an example app"
page_title: "A simple tool example"

about_section_title: "About this new tool"

# If True, a structure selection block will be shown and it will provide a common set of parsers.
# In this case, you will have to provide an endpoint
# `/compute/process_structure/` to process the results
# as shown later.
use_upload_structure_block: True

# If you have an upload block and want to have some parsers first, you can specify their internal
# name as a list. Those from the list will be shown first (NOTE! if the name is unknown, it is ignored).
# All the remaining ones, if any, are shown afterwards in a default order.
upload_structure_block_order: ['cif-pymatgen', 'xsf-ase']

templates:
  how_to_cite: "how_to_cite.html"
  about: "about.html"
  select_content: "visualizer_select_example.html" # what to show in the selection page (below the upload structure block, if present)
  upload_structure_additional_content: "upload_structure_additional_content.html" # if the upload structure block is present, you can add additional content right above the 'submit' button, if you want (e.g. a disclaimer, terms of use, ...)

# Add here more sections to the accordion shown on the top of the selection page
additional_accordion_entries:
#  - header: "What is this?"
#    template_page: what_is.html
  - header: "Acknowledgements"
    template_page: ack.html
```

### 4. Create the Dockerfile

Once the files are ready, we can write a `Dockerfile` that extends the `tools-barebone` image (with the tag you have chosen earlier),
to build and run the docker container for `custom-tool`.

The snippet below shows a minimal
`Dockerfile` file that achieves this goal. You can create such a file inside `custom-tool/Dockerfile`.
The commands that you need and that are specific to `custom-tool` can be added at the bottom of the file.
Remember to replace the `LABEL` string.

````
FROM materialscloud/tools-barebone:X.Y.Z

LABEL maintainer="Developer Name <developer.email@xxx.yy>"

# Python requirements
COPY ./requirements.txt /home/app/code/requirements.txt
# Run this as sudo to replace the version of pip

RUN pip3 install -U 'pip>=10' setuptools wheel
# install packages as normal user (app, provided by passenger)

USER app
WORKDIR /home/app/code
# Install pinned versions of packages
RUN pip3 install --user -r requirements.txt
# Go back to root.
# Also, it should remain as user root for startup
USER root

# Copy various files: configuration, user templates, the actual python code, ...
COPY ./config.yaml /home/app/code/webservice/static/config.yaml
COPY ./user_templates/ /home/app/code/webservice/templates/user_templates/
COPY ./compute/ /home/app/code/webservice/compute/

# If you put any static file (CSS, JS, images),
#create this folder and put them here
# COPY ./user_static/ /home/app/code/webservice/user_static/

###
# Copy any additional files needed into /home/app/code/webservice/
###

# Set proper permissions on files just copied
RUN chown -R app:app /home/app/code/webservice/
````

### 5. Test it!

You can now build the Docker image, and then launch the container as follows.

First, go in the top folder of your tool, where the `Dockerfile` sits. Then, run this command:

```(bash)
docker build -t custom-tools . && docker run -p 8091:80 --rm --name=custom-tools-instance custom-tools
```

You can now connect to http://localhost:8091 and check if your results starts to look like the right panel of the images above, and it contains the text that you were expecting.

### 6. Fine tune the text
Before looking into the backend python logic, you can now fine-tune the templates that you have written before. Change the `config.yaml` and the various templates. Then, run again the docker build+run commands of the previous sections, and refresh your browser until you are happy with the results.

### 7. Backend implementation
Now it is time to work on the python backend implementation.

`tools-barebone` uses the [Flask](https://flask.palletsprojects.com/) framework, so you might want to look into its documentation to discover all advanced features. Here we describe only how to make a minimal working tool.

You will put the code in the `compute` folder you created before. You can add any number of python files in it, and load them using
```
from compute.XXX import YYY
```
(the `compute` folder will be in the python path).

You will need however to have some minimal content in the `compute/__init__.py` file.

In particular, you will need at least to define a `blueprint` as follows:
```python
import flask

blueprint = flask.Blueprint("compute", __name__, url_prefix="/compute")
```

You can then add your views.
If you are using the structure upload block (see comments in the description of the `config.yaml` section), you will need to define at least a `/compute/process_structure/` endpoint. Here is a minimal working example, that you can use as a starting point. Note that here we are going to use the parsing functionality provided directly by the `tools-barebone` package.

```python
from tools_barebone.structure_importers import get_structure_tuple, UnknownFormatError
import io

@blueprint.route("/process_structure/", methods=["POST"])
def process_structure():
    """Example view to process a crystal structure."""

    # check if the post request has the file part, otherwise redirect to first page
    if "structurefile" not in flask.request.files:
        # This will redirect the user to the selection page, that is called `input_data` in tools-barebone
        return flask.redirect(flask.url_for("input_data"))

    # Get structure, file format, file content, and form data (needed for additional information, e.g. cell in the case of a XYZ file)
    structurefile = flask.request.files["structurefile"]
    fileformat = flask.request.form.get("fileformat", "unknown")
    filecontent = structurefile.read().decode("utf-8")
    fileobject = io.StringIO(str(filecontent))
    form_data = dict(flask.request.form)

    # Use
    try:
        structure_tuple = get_structure_tuple(
            fileobject, fileformat, extra_data=form_data
        )
    except UnknownFormatError:
        # You can use the flask.flash functionality to send a message
        # back to the structure selection page; this
        # will be shown in a red box on the top
        flask.flash("Unknown format '{}'".format(fileformat))
        return flask.redirect(flask.url_for("input_data"))
    except Exception:
        # Let's deal properly with any exception, to avoid to get a 500 error.
        # Feel free to do better error management here,
        # or to pass additional information via flask.flash
        flask.flash(
            "I tried my best, but I wasn't able to load your "
            "file in format '{}'...".format(fileformat)
        )
        return flask.redirect(flask.url_for("input_data"))
    # If we are here, the file was retrieved.
    # It will contain a tuple of length three, with:
    # - the 3x3 unit cell (in angstrom)
    # - a Nx3 list of atomic coordinates (in fractional coordinates)
    # - a list of integer atomic numbers of length N

    # As an example, we just create a string representation of the JSON
    # and send it back to the user, to be rendered in a form
    import json
    data_for_template = {
        "structure_json": json.dumps(
            {
                "cell": structure_tuple[0],
                "atoms": structure_tuple[1],
                "numbers": structure_tuple[2],
            },
            indent=2,
            sort_keys=True,
        )
    }
    return flask.render_template("user_templates/custom-tool.html", **data_for_template)
```
In order to make it work, the last step is to create a `user_templates/custom-tool.html` file, e.g. with the following minimal content:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Add CSS, JS, ... here, e.g, these from tools-barebone;  -->
    <link href="../../static/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="../../static/css/jquery-ui.1.12.1.min.css"/>
    <link rel="stylesheet" type="text/css" href="../../static/css/visualizer_base.min.css"/>
    <link rel="stylesheet" type="text/css" href="../../static/css/visualizer_input.min.css"/>
    <script src="../../static/js/jquery-3.1.0.min.js"></script>
    <script src="../../static/js/jquery-ui.1.12.1.min.js"></script>

    <!-- If you add things in a user_static folder, you will be able to access it via ../../user_static/xxx -->

    <title>Custom-tools example return page</title>

    <!-- Keep this, it's needed to make the tool embeddable in an iframe; it's provided by tools-barebone -->
    <script src="../../static/js/iframeResizer.contentWindow.min.js"></script>
</head>

<body>
<div id='container'>
    <div id='maintitle'>
        <h1 style="text-align: center;">Tools-example return page</h1>
    </div>

    <h2>Successfully parsed structure tuple</h2>
    <p>
        <code id='structureJson'>
{{structure_json}}
        </code>
    </p>
</div>

<!-- Important: leave this tag as the *very last* in your page, just before the end of the body -->
<!-- It is needed to properly detect the size of the iframe -->
<div style ="position: relative" data-iframe-height></div>
</body>
</html>
```

You can now build and run again the container, and you should see the parsed results, in JSON form, in the page once you upload a structure.

### 8. Additional views
You can now continue adding views to your application, inside the blueprint. Check the Flask documentation for more information. Here, we just show an example to create a view for some Terms of use.

- First create a `user_views` folder in the top folder of your application, and create a file `termsofuse.html` inside it. Complete it with the full HTML code that you want to send to the user. Rembember also to add the correct `COPY` line to the `Dockerfile`.

- Then, create the Flask view for it, in the `compute/__init__.py` file:
```python
import os

VIEW_FOLDER = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "user_views"
)

@blueprint.route("/termsofuse/")
def termsofuse():
    """
    View for the terms of use
    """
    return flask.send_from_directory(VIEW_FOLDER, "termsofuse.html")
```

The page will be accessible under the url `/compute/termsofuse/`.

Finally, if e.g. you want to show a link to it in the Structure Upload block, right before the Submit button, you can add the following line in the `templates` dictionary:
```yaml
templates:
  # ...
  upload_structure_additional_content: "upload_structure_additional_content.html"
```
and create a file `upload_structure_additional_content.html` in the `user_templates` folder, e.g. with the following content:
```html
<div class='row' style="text-align:center">
    <p class='small'>By continuing, you agree with the <a href="../compute/termsofuse/" target="_blank">terms of use</a> of this service.</p>
</div>
```

## Some examples

An example based on `tools-barebone`, with additional Python backend functionality, is provided in the
[tools-example](https://github.com/materialscloud-org/tools-example) tool.

For a more advanced tool, you can also check out the [tools-seekpath](https://github.com/materialscloud-org/tools-seekpath) tool or the [tools-phonon-dispersion](https://github.com/materialscloud-org/tools-phonon-dispersion), for instance.

Here you can see also an example of how the python code in the backend is implemented (check the implementation of the API endpoints inside the `compute` subfolder).
You can also get inspiration for the setup of tests with pytest, of continuous integration with GitHub actions, on how to setup pre-commit hooks, etc.
