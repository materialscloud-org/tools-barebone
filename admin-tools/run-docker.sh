#!/bin/bash
OLD_INSTANCE=`docker ps -q -f name=tools-barebone-instance`
if [ "$OLD_INSTANCE" != "" ]
then
    docker kill $OLD_INSTANCE
fi
docker run -d -p 8090:80 --rm --name=tools-barebone-instance tools-barebone && echo "You can connect to http://localhost:8090"