#!/usr/bin/env bash
BASEDIR=$(dirname "$0")
python3 ${BASEDIR}/branch-starter.py "config_dir=${BASEDIR}/config.d" ${@}