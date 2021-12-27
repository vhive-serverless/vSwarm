package main

import (
	"flag"
	"fmt"
	"os"
	"strconv"
	"time"

	log "github.com/sirupsen/logrus"

	tracer "github.com/ease-lab/vhive/utils/tracing/go"
	fc "github.com/vSwarm/tools/loader/internal/function"
	tc "github.com/vSwarm/tools/loader/internal/trace"
)

const (
	zipkinAddr = "http://localhost:9411/api/v2/spans"
)

var (
	traces            tc.FunctionTraces
	serviceConfigPath = "workloads/trace_func_go.yaml"

	debug       = flag.Bool("dbg", false, "Enable debug logging")
	rps         = flag.Int("rps", 1, "Request per second")
	duration    = flag.Int("duration", 1, "Duration of the experiment")
	sampleSize  = flag.Int("size", 5, "Sample size of the traces")
	withTracing = flag.Bool("trace", false, "Enable tracing in the client")
)

func init() {
	/** Logging. */
	flag.Parse()

	log.SetFormatter(&log.TextFormatter{
		TimestampFormat: time.StampMilli,
		FullTimestamp:   true,
	})
	log.SetOutput(os.Stdout)
	if *debug {
		log.SetLevel(log.DebugLevel)
		log.Debug("Debug logging is enabled")
	} else {
		log.SetLevel(log.InfoLevel)
	}
	if *withTracing {
		shutdown, err := tracer.InitBasicTracer(zipkinAddr, "loader")
		if err != nil {
			log.Print(err)
		}
		defer shutdown()
	}

	/** Trace parsing. */
	traces = tc.ParseInvocationTrace(
		"data/traces/"+strconv.Itoa(*sampleSize)+"/invocations.csv", *duration)
	tc.ParseDurationTrace(
		&traces, "data/traces/"+strconv.Itoa(*sampleSize)+"/durations.csv")
	tc.ParseMemoryTrace(
		&traces, "data/traces/"+strconv.Itoa(*sampleSize)+"/memory.csv")

	log.Info("Traces contain the following: ", len(traces.Functions), " functions")
	for _, function := range traces.Functions {
		fmt.Println("\t" + function.GetName())
	}
}

func main() {
	/** Deployment */
	log.Info("Using service config file: ", serviceConfigPath)
	functions := fc.Deploy(traces.Functions, serviceConfigPath, 1) // TODO: Fixed number of functions per pod.

	/** Invokation */
	defer fc.Invoke(*rps, functions, traces.InvocationsPerMinute, traces.TotalInvocationsEachMinute)
}
