package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	deployer "github.com/ease-lab/vSwarm/tools/deployer"
	log "github.com/sirupsen/logrus"
)

type ProfilingJobs struct {
	ProfilingJobs []ProfilingJob `json:"profiling_jobs"`
}

type ProfilingJob struct {
	Instruction_id int    `json:"instr_id"`
	JobType        string `json:"job_type"`
	FunctionType   string `json:"func_name"`
}

var (
	profilingJobFile = flag.String("jobFile", "profiling_job.json", "JSON file that contains the list of jobs to run")
)

func isDebuggingEnabled() bool {
	if val, ok := os.LookupEnv("ENABLE_DEBUGGING"); !ok || val == "false" {
		return false
	} else if val == "true" {
		return true
	} else {
		log.Errorf("ENABLE_DEBUGGING has unexpected value: `%s`", val)
		return false
	}
}
func main() {
	flag.Parse()

	if isDebuggingEnabled() {
		log.SetLevel(log.DebugLevel)
		log.Info("Debugging is enabled.")
	}

	jsonFile, err := os.Open(*profilingJobFile)

	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()

	byteValue, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		log.Fatal(err)
	}
	var profilingJobs ProfilingJobs

	json.Unmarshal(byteValue, &profilingJobs)
	listFunctions := map[string]bool{}
	log.Debugf("Start to read each job...")

	for i := 0; i < len(profilingJobs.ProfilingJobs); i++ {
		job := profilingJobs.ProfilingJobs[i]
		if _, exists := listFunctions[job.FunctionType]; exists {
			log.Debugf("Function is already running.")
		} else {
			deployer.deploy("", [], 0)
			log.Debugf("Function %s started", job.FunctionType)
			listFunctions[job.FunctionType] = true
		}
	}
}
