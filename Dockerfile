# Use phusion/passenger image that is a good starting point for webapps
# see also: https://phusion.github.io/baseimage-docker
FROM phusion/passenger-customizable:2.6.2

LABEL maintainer="Materials Cloud <developers@materialscloud.org>"

# Everything will be run as root
USER root

# Set correct environment variables.
ENV HOME /root

# If you're using the 'customizable' variant, you need to explicitly opt-in
# for features. Uncomment the features you want:

RUN /pd_build/python.sh 3.10

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

# Setup apache
# Disable default apache site, enable tools site; also
# enable needed modules
ADD ./.docker_files/apache-site.conf /etc/apache2/sites-available/app.conf
RUN a2enmod wsgi && a2enmod xsendfile \
    && a2dissite 000-default && a2ensite app \
    && a2enmod headers

# Activate apache at startup
RUN mkdir /etc/service/apache
#RUN mkdir /var/run/apache2
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
RUN pip install -r $HOME/code/requirements.txt --verbose

COPY ./setup.py setup.py
COPY README.md README.md
COPY ./tools_barebone/ tools_barebone
RUN pip install -e .

# Actually, don't download, but get the code directly from this repo
COPY ./webservice/ webservice

# Get Materials Cloud header
RUN git clone https://github.com/materialscloud-org/frontend-theme.git && \
    cp -r frontend-theme/header/jinja/app/* webservice/

# Create a proper wsgi file
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