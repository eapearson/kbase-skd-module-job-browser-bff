base_dir="/Users/erikpearson/work/kbase/sprints/2019/q3/s4/kbase-sdk-module-job-browser-bff/lib/JobBrowserBFF/model/mockData/logs/"

function ()

mongoimport\
  --host=localhost \
  --port=32774 \
  --username=test \
  --collection=job_logs \
  --db=JobBrowserBFF \
  --file=${FILENAME}
