#!/bin/bash

# Exit if any command fails
set -e

# Env vars of Apache
. /etc/apache2/envvars

# Env vars by Ubuntu (change here if needed to tune performance)
# Note however that the file is not created by default in this
# docker configuration
if [ -e /etc/default/apache2 ]
then
    . /etc/default/apache2
fi

## Delete PID files if exists
## A leftover apache.pid file after a reboot prevents the
## container to start (see issue #26)
rm -f /var/run/apache2/apache2.pid

exec apache2 -D FOREGROUND
