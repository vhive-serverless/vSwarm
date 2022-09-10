// MIT License
//
// Copyright (c) 2020 Dmitrii Ustiugov and EASE lab
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

package deployer

import (
	"encoding/json"
	"flag"
	"io/ioutil"
	"os"
	"os/exec"

	"github.com/ease-lab/vSwarm/tools/endpoint"
	log "github.com/sirupsen/logrus"
)

// Functions is an object for unmarshalled JSON with functions to deploy
type Functions struct {
	Functions []functionType `json:"functions"`
}

type functionType struct {
	Name string `json:"name"`
}

var (
	// gatewayURL            = flag.String("gatewayURL", "192.168.1.240.sslip.io", "URL of the gateway")
	knativeYamlPathsFile = flag.String("knativeYamlFile", "yaml_loc.json", "JSON file that contains the locations of all benchmarks")
	deployFunctionPath   = flag.String("deployFunctionPath", "deploy_functions.json", "JSON file that contains the locations of all benchmarks")
	// namespaceName         = flag.String("namespace", "default", "name of namespace in which services exists")
	// endpointsFile         = flag.String("endpointsFile", "endpoints.json", "File with endpoints' metadata")
	deploymentConcurrency = flag.Int("conc", 5, "Number of functions to deploy concurrently (for serving)")
)

func isDebuggingEnabled() bool {
	if val, ok := os.LookupEnv("ENABLE_DEBUGGING"); !ok || val == "false" {
		return false
	} else if val == "true" {
		return true
	} else {
		log.Fatalf("ENABLE_DEBUGGING has unexpected value: `%s`", val)
		return false
	}
}

// func main() {
// 	if isDebuggingEnabled() {
// 		log.SetLevel(log.DebugLevel)
// 		log.Info("Debugging is enabled.")
// 	}

// 	flag.Parse()

// 	funcSlice := getFuncSlice(*deployFunctionPath)

// 	urls := deploy(funcSlice, *deploymentConcurrency)

// 	writeEndpoints(*endpointsFile, urls)

// 	log.Infoln("Deployment finished")
// }

func getFuncSlice(file string) []functionType {
	log.Debug("Opening JSON file with functions: ", file)
	byteValue, err := ioutil.ReadFile(file)
	if err != nil {
		log.Fatalf("Error while reading func slice file: %s", err)
	}
	var functions Functions
	if err := json.Unmarshal(byteValue, &functions); err != nil {
		log.Fatalf("Error while Unmarshalling func slice: %s", err)
	}
	return functions.Functions
}

// func deploy(funcSlice []functionType, deploymentConcurrency int) []string {
// 	var urls []string
// 	sem := make(chan bool, deploymentConcurrency) // limit the number of parallel deployments

// 	for _, fType := range funcSlice {
// 		sem <- true
// 		funcName := fType.Name
// 		url := fmt.Sprintf("%s.%s.%s", funcName, *namespaceName, *gatewayURL)
// 		urls = append(urls, url)

// 		go func(funcName string) {
// 			defer func() { <-sem }()

// 			DeployFunction(funcName, *knativeYamlPathsFile)
// 		}(funcName)
// 	}

// 	for i := 0; i < cap(sem); i++ {
// 		sem <- true
// 	}

// 	return urls
// }

func DeployFunction(funcName string, knativePathFile string) {
	if isDebuggingEnabled() {
		pwd, err := exec.Command("pwd").Output()
		if err != nil {
			log.Warn(err)
		}
		log.Debugf("Currently working in %s", pwd)
	}

	// Read locations of yaml files
	var locs map[string]interface{}
	byteValue, err := ioutil.ReadFile(knativePathFile)
	if err != nil {
		log.Fatalf("Error while reading knative yaml file: %s", err)
	}
	if err := json.Unmarshal(byteValue, &locs); err != nil {
		log.Fatalf("Error while Unmarshalling knative yaml: %s", err)
	}

	filePath := locs[funcName].(string)

	cmd := exec.Command(
		"kn",
		"service",
		"apply",
		funcName,
		"-f",
		filePath,
		"--concurrency-target",
		"1",
	)
	cmd.Dir = "../../benchmarks"
	stdoutStderr, err := cmd.CombinedOutput()
	if err != nil {
		log.Warnf("Failed to deploy function %s, %s: %v\n%s\n", funcName, filePath, err, stdoutStderr)
	}

	log.Info("Deployed function ", funcName)
}

func writeEndpoints(filePath string, urls []string) {
	var endpoints []endpoint.Endpoint
	for _, url := range urls {
		endpoints = append(endpoints, endpoint.Endpoint{
			Hostname: url,
			Eventing: false,
			Matchers: nil,
		})
	}
	data, err := json.MarshalIndent(endpoints, "", "\t")
	if err != nil {
		log.Fatalln("failed to marshal", err)
	}
	if err := ioutil.WriteFile(filePath, data, 0644); err != nil {
		log.Fatalln("failed to write", err)
	}
}
