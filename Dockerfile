# Use phusion/baseimage as base image. To make your builds
# reproducible, make sure you lock down to a specific version, not
# to `latest`! See
# https://github.com/phusion/baseimage-docker/blob/master/Changelog.md
# for a list of version numbers.
# Note also that we use phusion because, as explained on the
# http://phusion.github.io/baseimage-docker/ page, it automatically
# contains and starts all needed services (like logging), it
# takes care of sending around signals when stopped, etc.
##
# Actually, I use passenger-full that already has python
# https://github.com/phusion/passenger-docker#using
FROM phusion/passenger-customizable:1.0.11

LABEL maintainer="Materials Cloud <developers@materialscloud.org>"

# Everything will be run as root
USER root

# Set correct environment variables.
ENV HOME /root

# If you're using the 'customizable' variant, you need to explicitly opt-in
# for features. Uncomment the features you want:
#
    #   Build system and git.
    #   Python support (2.7 and 3.x - it is 3.6.x in this ubuntu 18.04)
RUN /pd_build/utilities.sh && \
    /pd_build/python.sh

##########################################
############ Installation Setup ##########
##########################################

# Install required software

# Install Apache
# (nginx doesn't have the X-Sendfile support that we want to use)
## NOTE: Here and below we install everything with python3
RUN apt-get update \
    && apt-get -y install \
    python3-pip \
    apache2 \
    libapache2-mod-xsendfile \
    libapache2-mod-wsgi-py3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean all

# set $HOME
ENV HOME /home/app

# Run this as sudo to replace the version of pip
RUN pip3 install -U 'pip>=10' setuptools wheel

# Setup apache
# Disable default apache site, enable tools site; also
# enable needed modules
ADD ./.docker_files/apache-site.conf /etc/apache2/sites-available/app.conf
RUN a2enmod wsgi && a2enmod xsendfile && \
    a2dissite 000-default && a2ensite app

# Activate apache at startup
RUN mkdir /etc/service/apache
RUN mkdir /var/run/apache2
ADD ./.docker_files/apache_run.sh /etc/service/apache/run

# Web
EXPOSE 80

# Set startup script to create the secret key
RUN mkdir -p /etc/my_init.d
ADD ./.docker_files/create_secret_key.sh /etc/my_init.d/create_secret_key.sh

# Download code
RUN mkdir -p $HOME/code/
WORKDIR $HOME/code/
COPY ./requirements.txt requirements.txt
RUN pip3 install -r $HOME/code/requirements.txt

COPY ./setup.py setup.py
COPY README.md README.md
COPY ./tools_barebone/ tools_barebone
RUN pip3 install -e .

# Actually, don't download, but get the code directly from this repo
COPY ./webservice/ webservice
# Create a proper wsgi file file
ENV SP_WSGI_FILE=webservice/app.wsgi
RUN echo "import sys" > $SP_WSGI_FILE && \
    echo "sys.path.insert(0, '/home/app/code/webservice')" >> $SP_WSGI_FILE && \
    echo "from run_app import app as application" >> $SP_WSGI_FILE


# Set proper permissions for user 'app' who will be used to run the service
RUN chmod -R o+rX $HOME
RUN chown -R app:app $HOME

# Final cleanup, in case it's needed
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]