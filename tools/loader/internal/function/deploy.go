package function

import (
	"os/exec"

	log "github.com/sirupsen/logrus"

	tc "github.com/vSwarm/tools/loader/internal/trace"
)

func Deploy(
	functions []tc.Function,
	serviceConfigPath string,
	deploymentConcurrency int) []tc.Function {
	var urls []string
	/**
	 * Limit the number of parallel deployments
	 * using a channel (like semaphore).
	 */
	sem := make(chan bool, deploymentConcurrency)

	for idx, function := range functions {
		sem <- true

		go func(function tc.Function, idx int) {
			defer func() { <-sem }()

			has_deployed := deployFunction(&function, serviceConfigPath)
			function.SetStatus(has_deployed)
			if has_deployed {
				urls = append(urls, function.GetUrl())
			}

			functions[idx] = function
		}(function, idx)
	}

	for i := 0; i < cap(sem); i++ {
		sem <- true
	}
	return functions
}

func deployFunction(function *tc.Function, workloadPath string) bool {
	//TODO: Make concurrency configurable.
	cmd := exec.Command(
		"kn",
		"service",
		"apply",
		function.GetName(),
		"-f",
		workloadPath,
		"--concurrency-target",
		"1",
	)
	stdoutStderr, err := cmd.CombinedOutput()
	log.Debug("CMD response: ", string(stdoutStderr))

	if err != nil {
		log.Warnf("Failed to deploy function %s: %v\n%s\n", function.GetName(), err, stdoutStderr)
		return false
	}

	log.Info("Deployed function ", function.GetUrl())
	return true
}
