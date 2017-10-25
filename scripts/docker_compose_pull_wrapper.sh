#!/bin/bash


logger() {
    while true; do
        echo 'Still pulling...'
        sleep 60
    done
}


main() {
    local logger_pid \
        docker_compose_rc

    logger &
    logger_pid=$!
    docker-compose pull --parallel
    docker_compose_rc=$?
    kill "$logger_pid"
    return "$docker_compose_rc"
}


main
