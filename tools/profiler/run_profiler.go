package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strconv"

	"github.com/ease-lab/vSwarm/tools/deployer"
	"github.com/ease-lab/vSwarm/tools/endpoint"
	log "github.com/sirupsen/logrus"
)

type ProfilingJobs struct {
	ProfilingJobs []ProfilingJob `json:"profiling_jobs"`
}

type ProfilingJob struct {
	JobType      string `json:"job_type"`
	FunctionName string `json:"func_name"`
	RunDuration  int    `json:"runDuration"`
	Rps          int    `json:"rps"`
}

var (
	profilingJobFile = flag.String("jobFile", "profiling_job.json", "JSON file that contains the list of jobs to run")
	gatewayURL       = flag.String("gatewayURL", "192.168.1.240.sslip.io", "URL of the gateway")
	namespaceName    = flag.String("namespace", "default", "name of namespace in which services exists")
	endpointsFile    = flag.String("endpointsFile", "endpoints.json", "File with endpoints' metadata")
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
	makeInvoker()

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
	listFunctionsRunning := map[string]bool{}
	log.Debugf("Start to read each job...")

	// Deploy each function
	for i := 0; i < len(profilingJobs.ProfilingJobs); i++ {
		job := profilingJobs.ProfilingJobs[i]
		if _, exists := listFunctionsRunning[job.FunctionName]; exists {
			log.Debugf("Function is already running.")
		} else {
			deployer.DeployFunction(job.FunctionName, "../deployer/yaml_loc.json")
			log.Debugf("Function %s started", job.FunctionName)
			listFunctionsRunning[job.FunctionName] = true
		}

		// Write endpoints for invoker
		jobURL := fmt.Sprintf("%s.%s.%s", job.FunctionName, *namespaceName, *gatewayURL)
		jobEndpoint := endpoint.Endpoint{
			Hostname: jobURL,
			Eventing: false,
			Matchers: nil,
		}
		var jobEndpoints []endpoint.Endpoint
		jobEndpoints = append(jobEndpoints, jobEndpoint)

		data, err := json.MarshalIndent(jobEndpoints, "", "\t")
		if err != nil {
			log.Fatalln("Failed to marshal endpoints", err)
		}
		if err := ioutil.WriteFile("../invoker/"+*endpointsFile, data, 0644); err != nil {
			log.Fatalln("Failed to write endpoints file", err)
		}

		// Read locations of yaml files
		var locs map[string]interface{}
		byteValue, err := ioutil.ReadFile("../deployer/yaml_loc.json")
		if err != nil {
			log.Fatalf("Error while reading knative yaml file: %s", err)
		}
		if err := json.Unmarshal(byteValue, &locs); err != nil {
			log.Fatalf("Error while Unmarshalling knative yaml: %s", err)
		}

		// Wait for knative to get deployed
		waitForDeployCmd := exec.Command(
			"kubectl wait --for=condition=Ready -f",
			locs[job.FunctionName].(string),
			"--timeout 120s",
		)
		waitForDeployCmd.Dir = "../../benchmarks"
		stdoutStderr, err := waitForDeployCmd.CombinedOutput()
		if err != nil {
			log.Warnf("Failed to make invoker: %v, %s", err, stdoutStderr)
		}
		callInvoker(job.Rps, job.RunDuration)

	}

}

func callInvoker(rps int, runDuration int) {
	// Call invoker
	cmd := exec.Command(
		"./invoker",
		"-port",
		"50051",
		"-rps",
		strconv.Itoa(rps),
		"-time",
		strconv.Itoa(runDuration),
	)
	cmd.Dir = "../invoker"
	stdoutStderr, err := cmd.CombinedOutput()
	if err != nil {
		log.Warnf("Failed to call invoker: %v, %s", err, stdoutStderr)
	}
}

func makeInvoker() {
	cmd := exec.Command(
		"make",
		"invoker",
	)
	cmd.Dir = "../invoker"
	log.Debug("Building invoker")
	stdoutStderr, err := cmd.CombinedOutput()
	if err != nil {
		log.Warnf("Failed to make invoker: %v, %s", err, stdoutStderr)
	}
}
