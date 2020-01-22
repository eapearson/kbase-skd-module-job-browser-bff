import os
import subprocess
import glob

def import_log():
    data_dir = "/Users/erikpearson/work/kbase/sprints/2019/q3/s4/kbase-sdk-module-job-browser-bff/lib/JobBrowserBFF/model/mockData/logs"
    # filename = "job_log_56a0f9d8e4b00c7404a23aee.json"
    # filename = os.path.join(base_dir, filename)

    for file_path in glob.glob(data_dir + '/*.json'):
        result = subprocess.run([
            "mongoimport",
            "--host=localhost",
            "--port=32774",
            "--username=test",
            "--password=test",
            "--authenticationDatabase=admin",
            "--collection=job_logs",
            "--db=JobBrowserBFF",
            "--jsonArray",
            "--file={}".format(file_path)
        ])

    if result.returncode:
        print('OOPS', result.stdout, result.stderr)
    
import_log()
