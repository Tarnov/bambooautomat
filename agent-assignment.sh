#!/usr/bin/env bash
BASEDIR=$(dirname "$0")
python3 ${BASEDIR}/agent-assignment.py "config_dir=${BASEDIR}/config.d" "${@}"