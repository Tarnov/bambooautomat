#!/usr/bin/env bash
BASEDIR=$(dirname "$0")
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
export PYTHONFAULTHANDLER=1
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "${@}"