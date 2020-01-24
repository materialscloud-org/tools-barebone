# tools-barebone

[![Actions Status](https://github.com/materialscloud-org/tools-barebone/workflows/Docker%20Image%20Build%20CI/badge.svg)](https://github.com/materialscloud-org/tools-barebone/actions)
[![Actions Status](https://github.com/materialscloud-org/tools-barebone/workflows/Publish%20Docker/badge.svg)](https://github.com/materialscloud-org/tools-barebone/actions)


`tools-barebone` is a framework to develop and deploy small web apps,
implemented in Python using Flask Jinja2 templates.
It can be used as a starting point to develop new tools for the
[Materials Cloud Tools section](https://www.materialscloud.org/work/tools/options).

It provides:

- A common layout used for every tool in Materials cloud
- the Materials Cloud theme
- Common REST API endpoints
- Common widgets, e.g., file upload functionality
- Web server settings
- Scripts to deploy the tool in a docker container

## Prerequisites

- [docker](https://www.docker.com/) >= v18.09

## How to use a tools-barebone framework

The `tools-barebone` framework provides basic templates, that can be extended to develop
a new tool for Materials Cloud.
Here we will explain how the `tools-barebone` template (shown
on the left side of the figure below) can be extended to develop a new tool called `custom-tool`
(shown on the right side).

|                                            Tools barebone template                                             |                                               New tool template                                               |
| :------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------: |
| ![](https://github.com/materialscloud-org/tools-barebone/blob/master/webservice/static/img/tools-barebone.png) | ![](https://github.com/materialscloud-org/tools-barebone/blob/master/webservice/static/img/tools-example.png) |

### 1. Create a parent directory which will contain both the `tools-barebone` and `custom-tool` directories

For this example we will call it `materialscloud-tools`.

```(bash)
mkdir materialscloud-tools
cd materialscloud-tools
```

### 2. `tools-barebone` framework

Let's clone the `tools-barebone` repository to extend it further in the `materialscloud-tools` directory.

```(bash)
cd materialscloud-tools
git clone https://github.com/materialscloud-org/tools-barebone
```

In `tools-barebone`, a `SECRET KEY` is used to encrypt data in a web session when communicating between the browser and the server. You need to create one; to this aim, create a file called
`SECRET_KEY` within the folder `tools-barebone/webservice`, containing a random
string of at least 16 characters.
Also, change the permissions of the _SECRET_KEY_ file to 600 as shown below:

```(javascript)
function gen_pwd_char() {
    s=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890-_%/
    # Length of the string
    p=$(( $RANDOM % 66))
    echo -n ${s:$p:1}
}

#16-char password
THE_SECRET_KEY=`gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char;`

echo "$THE_SECRET_KEY" > webservice/SECRET_KEY
chmod 600 webservice/SECRET_KEY
```

The `tools-barebone` can be used either locally or in docker. We provide shell scripts
to help you building a docker image, launching a docker container, getting the apache log from a running container, etc.

For example:

```(bash)
cd tools-barebone

# to build docker
./build-docker.sh
```

To run the `tools-barebone` framework locally, one needs to install all the dependencies provided
in `requirements.txt` file. To do this, run the command below to install the `tools-barebone` dependencies using pip:

```(bash)
cd tools-barebone
pip install -r requirements.txt
```

Once your app `custom-tool` is ready, update its path in `run-example.sh` file as shown below:

```(bash)
vim run-example.sh

# inside run-example.sh file update below line
TOOLS_EXAMPLE_DIR="../custom-tools"
```

Now you can run your app locally by running the `run-example.sh` script. This script copies the files from
the `custom-tool` app to the `tools-barebone` framework in predefined places and runs the app
at http://localhost:5000.

```(bash)
./run-example.sh   # launch the server at http://127.0.0.1:5000
```

### 3. New tool: `custom-tool`

To write the new tool called `custom-tool`, create a new directory `custom-tool` inside the
`materialscloud-tools` folder. We will first create the minimum set of files required
in this new tool as shown below.

```(bash)
mkdir custom-tool
cd custom-tool

# create configuration file
touch config.yaml

# create Dockerfile file
touch Dockerfile

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

The `config.yaml` file contains the configuration details used in this new tool like window title,
page title, list of html templates, etc. Update the `config.yaml` file and add HTML templates
that will be shown in the section about the tool, for tool citation text and for the acknowledgements.

As an example of the most common variables to be set in the `config.yaml` file, we provide here an example
here below:

```(bash)
window_title: "Materials Cloud Tools: an example app"
page_title: "A simple tool example"

about_section_title: "About this new tool"

templates:
  how_to_cite: "how_to_cite.html"
  about: "about.html"

use_upload_structure_block: True

additional_accordion_entries:
#  - header: "What is this?"
#    template_page: what_is.html
  - header: "Acknowledgements"
    template_page: ack.html

```

Once the files are ready, we can write a `Dockerfile` that extends the `tools-barebone` image,
to build and run the docker container for `custom-tool`. The snippet below shows a minimal
`Dockerfile` file that achieves this goal. You can create such a file inside `custom-tool/Dockerfile`.
The commands that you need and that are specific to `custom-tool` can be added at the bottom of the file.
Remember to replace the MAINTAINER string.

````(bash)
FROM tools-barebone

MAINTAINER developers_name <developers_email>

COPY ./config.yaml /home/app/code/webservice/static/config.yaml
COPY ./user_templates/* /home/app/code/webservice/templates/user_templates/
COPY ./compute/ /home/app/code/webservice/compute/

# Set proper permissions
RUN chown -R app:app $HOME

#### Add custom-tool's specific commands here below


You are now ready to build and run the `custom-tool` container using the commands below.
They will start a new web server at http://127.0.0.1:8091. Feel free to put these
into a script inside the `custom-tool` folder to facilitate testing.

to launch container
```(bash)
docker build -t custom-tools .
````

to launch container

```(bash)
docker run -p 8091:80 --rm --name=custom-tools-instance custom-tools
```

## Backend functionality: `tools-example`

As a more complete example based on `tools-barebone`, with additional Python backend functionality, is available
[here](https://github.com/materialscloud-org/tools-example).

Here you can see also an example of how the python code in the backend is implemented (check the implementation of the API endpoints inside the `compute` subfolder).
