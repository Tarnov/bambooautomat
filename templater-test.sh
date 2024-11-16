#!/usr/bin/env bash
PRG=$0
if [ ! -e "${PRG}" ]; then
  case ${PRG} in
    (*/*) exit 1;;
    (*) PRG=$(command -v -- "${PRG}") || exit;;
  esac
fi
dir=$( cd -P -- "$(dirname -- "${PRG}")" && pwd -P ) || exit
PRG=${dir}/$(basename -- "${PRG}") || exit

BASEDIR=$(dirname "$PRG")

if [ "$#" -ne 2 ]; then
  echo "Usage: /path/to/panbet user@email.ru"
  exit 1
fi
PROJECT="pan"

export PYTHONWARNINGS="ignore:Unverified HTTPS request"
TEMPDIR="${BASEDIR}/tmp/templater-test"
rm -rf ${TEMPDIR}
mkdir -p ${TEMPDIR}
PANDIR=${1}
echo "Path to panbet directory: ${PANDIR}"
cd "$PANDIR" || exit 1
export bamboo_mail_to=""
echo "Email to: ${bamboo_mail_to}"
export bamboo_buildResultKey=DEVENG-PANBETMAILSENDER-0
export bamboo_updates=false
echo

echo "Mail 2 hour before master_rc (Sheduled/Manual):"
TEMPLATE="2-hours-before-rc.html"
export bamboo_planRepository_branch="master_rc"
NOTIFY="${TEMPDIR}/${bamboo_planRepository_branch}-${TEMPLATE}"
git checkout -f ${bamboo_planRepository_branch}
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "template=${PROJECT}/${TEMPLATE}" "output=${NOTIFY}"
{ echo -n '<html><body><meta charset="utf-8">'; cat $NOTIFY; echo -n '</body></html>';} > $NOTIFY.new
mv $NOTIFY{.new,}
echo

echo "Mail just before master_rc creation (Sheduled/Manual):"
TEMPLATE="master-rc.start.html"
export bamboo_planRepository_branch="master_rc"
export bamboo_parent_build=
NOTIFY="${TEMPDIR}/${bamboo_planRepository_branch}-${TEMPLATE}"
git checkout -f ${bamboo_planRepository_branch}
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "template=${PROJECT}/${TEMPLATE}" "output=${NOTIFY}"
{ echo -n '<html><body><meta charset="utf-8">'; cat $NOTIFY; echo -n '</body></html>';} > $NOTIFY.new
mv $NOTIFY{.new,}
echo

echo "Filters just before master_rc creation (Manual):"
TEMPLATE="master-rc.start-filters.html"
NOTIFY="${TEMPDIR}/${TEMPLATE}"
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "template=${PROJECT}/${TEMPLATE}" "output=${NOTIFY}"
echo

echo "Mail just after master_rc build (TriggeredByParent/CustomManual):"
TEMPLATE="master-rc.html"
export bamboo_planRepository_branch="master_rc"
export bamboo_dependency_parent_0=PANBUILD-PANBETMASTER111/latest
NOTIFY="${TEMPDIR}/${bamboo_planRepository_branch}-${TEMPLATE}"
git checkout -f ${bamboo_planRepository_branch}
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "template=${PROJECT}/${TEMPLATE}" "output=${NOTIFY}"
{ echo -n '<html><body><meta charset="utf-8">'; cat $NOTIFY; echo -n '</body></html>';} > $NOTIFY.new
mv $NOTIFY{.new,}
echo

echo "Mail branch report for master_rc (TriggeredByParent/CustomManual):"
TEMPLATE="branch-report.html"
export bamboo_planRepository_branch="master_rc"
export bamboo_dependency_parent_0=PANBUILD-PANBETMASTER111/latest
NOTIFY="${TEMPDIR}/${bamboo_planRepository_branch}-${TEMPLATE}"
git checkout -f ${bamboo_planRepository_branch}
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "template=${PROJECT}/${TEMPLATE}" "output=${NOTIFY}"
{ echo -n '<html><body><meta charset="utf-8">'; cat $NOTIFY; echo -n '</body></html>';} > $NOTIFY.new
mv $NOTIFY{.new,}
echo

echo "Filters just before master creation (Manual):"
TEMPLATE="master.start-filters.html"
NOTIFY="${TEMPDIR}/${TEMPLATE}"
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "template=${PROJECT}/${TEMPLATE}" "output=${NOTIFY}"
echo

echo "Mail after release master (TriggeredByParent/Manual):"
TEMPLATE="master.html"
export bamboo_planRepository_branch="master"
export bamboo_dependency_parent_0=PANBUILD-PANBETMASTER/latest
NOTIFY="${TEMPDIR}/${bamboo_planRepository_branch}-${TEMPLATE}"
git checkout -f ${bamboo_planRepository_branch}
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "template=${PROJECT}/${TEMPLATE}" "output=${NOTIFY}"
{ echo -n '<html><body><meta charset="utf-8">'; cat $NOTIFY; echo -n '</body></html>';} > $NOTIFY.new
mv $NOTIFY{.new,}

echo "Filters after release (Manual):"
TEMPLATE="master.end-filters.html"
NOTIFY="${TEMPDIR}/${TEMPLATE}"
python3 ${BASEDIR}/templater.py "config_dir=${BASEDIR}/config.d" "template=${PROJECT}/${TEMPLATE}" "output=${NOTIFY}"
echo
