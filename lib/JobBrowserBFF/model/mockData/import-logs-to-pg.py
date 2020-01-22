import os
import subprocess
import glob

def import_log():
    data_dir = "/Users/erikpearson/work/kbase/sprints/2019/q3/s4/kbase-sdk-module-job-browser-bff/lib/JobBrowserBFF/model/mockData/out"
    # filename = "job_log_56a0f9d8e4b00c7404a23aee.json"
    # filename = os.path.join(base_dir, filename)

    # sql = "COPY job_logs FROM '{}' CSV HEADER"

    sql = "COPY job_logs FROM STDIN CSV HEADER"

    for file_path in glob.glob(data_dir + '/split-*'):
        with open(file_path) as fin:
            print('importing {}'.format(file_path))
            print(sql.format(file_path))
            result = subprocess.run([
                "psql",
                "--host=localhost",
                "--port=32779",
                "--username=test",
                "--dbname=jobbrowserbff",
                "-c", sql
            ], stdin=fin)
            print('...done! {}'.format(result.stdout))

    if result.returncode:
        print('OOPS', result.stdout, result.stderr)
    
import_log()
