#!/bin/bash

source venv/bin/activate

python3 ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  # The compilation report is created by the in the build phase,
  # so we just need to copy it.
  # Note that /kb/module/work is bind mounted to a temporary directory
  # in order to collect the compilation report.
  echo "Copying compilation report to /work"
  cp /kb/compile_report.json /kb/module/work
else
  @echo "unknown entrypoint command"
fi
