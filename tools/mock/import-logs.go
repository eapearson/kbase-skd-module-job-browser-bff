package main

import (
	"encoding/json"
	"io/ioutil"
)

type LogRecord struct {
	Id       int    `json: "id"`
	Message  string `json: "message"`
	Is_error bool   `json: "is_error"`
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() {
	// dataDir := "/Users/erikpearson/work/kbase/sprints/2019/q3/s4/job-browser-bff-data/job_logs1"
	dataDir := "/Users/erikpearson/work/kbase/sprints/2019/q3/s4/kbase-sdk-module-job-browser-bff/lib/JobBrowserBFF/model/mockData/logs/"

	dirs, err := ioutils.ReadDir(dataDir)
	check(err)
	for _, dir := range dirs {

	}

	testFile := "job_log_56a0f9d8e4b00c7404a23aee.json"
	contents, err := ioutil.ReadFile(dataDir + testFile)
	check(err)
	var log []LogRecord
	err = json.Unmarshal(contents, &log)
	check(err)
}
