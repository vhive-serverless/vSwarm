package main

import (
	"os/exec"
	"strconv"
	"time"

	log "github.com/sirupsen/logrus"
)

// Profiler a instance of toplev command
type Profiler struct {
	cmd          *exec.Cmd
	tStart       time.Time
	interval     uint64
	execTime     float64
	warmTime     float64
	tearDownTime float64
	outFile      string
	cores        map[string]bool
	bottlenecks  map[string]float64
}

func NewProfiler(executionTime float64, printInterval uint64, level int, nodes, outFile string, socket, cpu int) (*Profiler, error) {
	profiler := new(Profiler)
	profiler.execTime = executionTime
	profiler.interval = printInterval
	profiler.cores = make(map[string]bool)
	profiler.bottlenecks = make(map[string]float64)

	if outFile == "" {
		outFile = "profile"
	}
	profiler.outFile = outFile + ".csv"

	profiler.cmd = exec.Command("/usr/local/pmu-tools/toplev",
		"-v",
		"--no-desc",
		"-x", ",",
		"-l", strconv.Itoa(level),
		"-I", strconv.FormatUint(printInterval, 10),
		"-o", profiler.outFile)

	if cpu > -1 {
		cpus, err := GetCPUInfo()
		if err != nil {
			return nil, err
		}
		core, err := cpus.GetSocketCoreInString(cpu)
		if err != nil {
			return nil, err
		}
		profiler.cmd.Args = append(profiler.cmd.Args, "--core", core)
	} else {
		// monitor the input socket only. the socket value should be negative if profiler measures globally.
		if socket > -1 {
			profiler.cmd.Args = append(profiler.cmd.Args, "--core", "S"+strconv.Itoa(socket))
		}
		// hide idle CPUs that are <50% of busiest.
		profiler.cmd.Args = append(profiler.cmd.Args, "--idle-threshold", "50")
	}

	// pass `profilerNodes` to pmu-tool if it is not empty, it controls specific metric/metrics to profile.
	if nodes != "" {
		profiler.cmd.Args = append(profiler.cmd.Args, "--nodes", nodes)
	}

	profiler.cmd.Args = append(profiler.cmd.Args, "sleep", strconv.FormatFloat(executionTime, 'f', -1, 64))

	log.Debugf("Profiler command: %s", profiler.cmd)

	return profiler, nil
}
