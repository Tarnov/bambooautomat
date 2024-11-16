#!/usr/bin/env bash
BASEDIR=$(dirname "$0")
python3 ${BASEDIR}/filter-checker.py "config_dir=${BASEDIR}/config.d" "${@}"