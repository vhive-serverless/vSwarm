package trace

import (
	"encoding/csv"
	"fmt"
	"io"
	"math/rand"
	"os"
	"strconv"
	"time"

	log "github.com/sirupsen/logrus"
	util "github.com/vSwarm/tools/loader/internal"
)

/** Seed the math/rand package for it to be different on each run. */
func init() {
	rand.Seed(time.Now().UnixNano())
}

const (
	gatewayUrl = "192.168.1.240.sslip.io" // Address of the load balancer.
	namespace  = "default"
	port       = "80"
)

type FunctionDurationStats struct {
	average       int
	count         int
	minimum       int
	maximum       int
	percentile0   int
	percentile1   int
	percentile25  int
	percentile50  int
	percentile75  int
	percentile99  int
	percentile100 int
}

type FunctionMemoryStats struct {
	average       int
	count         int
	percentile1   int
	percentile5   int
	percentile25  int
	percentile50  int
	percentile75  int
	percentile95  int
	percentile99  int
	percentile100 int
}
type Function struct {
	name          string
	url           string
	appHash       string
	hash          string
	deployed      bool
	durationStats FunctionDurationStats
	memoryStats   FunctionMemoryStats
}

type FunctionTraces struct {
	path                       string
	Functions                  []Function
	InvocationsPerMinute       [][]int
	TotalInvocationsEachMinute []int
}

func GenerateExecutionSpecs(function Function) (int, int) {
	var runtime, memory int
	//* Generate a random persentile in [0, 100).
	quantile := rand.Float32()
	runtimePct := function.durationStats
	memoryPct := function.memoryStats
	flag := util.GetRandBool()

	/**
	 * With 50% prob., returns average values.
	 * With 25% prob., returns the upper bound of the quantile interval.
	 * With 25% prob., returns the average between the two bounds of the interval.
	 *
	 * TODO: Later when can choose between the last two base upon #samples.
	 **NB: The smaller the #samples, the closer the pct. values to the actual ones.
	 */
	if runtime, memory = runtimePct.average, memoryPct.average; flag {
		switch {
		case quantile <= 0.01:
			runtime, memory = getSubduedSpecs(
				runtimePct.percentile1, runtimePct.percentile0,
				memoryPct.percentile1, memoryPct.percentile1, // Pct=0 is missing (see: https://github.com/Azure/AzurePublicDataset/blob/master/AzureFunctionsDataset2019.md#notes-2)
			)
		case quantile <= 0.05:
			runtime, memory = getSubduedSpecs(
				runtimePct.percentile1, runtimePct.percentile0,
				memoryPct.percentile5, memoryPct.percentile1,
			)
		case quantile <= 0.25:
			runtime, memory = getSubduedSpecs(
				runtimePct.percentile25, runtimePct.percentile1,
				memoryPct.percentile25, memoryPct.percentile5,
			)
		case quantile <= 0.50:
			runtime, memory = getSubduedSpecs(
				runtimePct.percentile50, runtimePct.percentile25,
				memoryPct.percentile50, memoryPct.percentile25,
			)
		case quantile <= 0.75:
			runtime, memory = getSubduedSpecs(
				runtimePct.percentile75, runtimePct.percentile50,
				memoryPct.percentile75, memoryPct.percentile50,
			)
		case quantile <= 0.95:
			runtime, memory = getSubduedSpecs(
				runtimePct.percentile75, runtimePct.percentile50,
				memoryPct.percentile95, memoryPct.percentile75,
			)
		case quantile <= 0.99:
			runtime, memory = getSubduedSpecs(
				runtimePct.percentile99, runtimePct.percentile75,
				memoryPct.percentile99, memoryPct.percentile95,
			)
		case quantile < 1:
			runtime, memory = getSubduedSpecs(
				runtimePct.percentile100, runtimePct.percentile99,
				memoryPct.percentile100, memoryPct.percentile99,
			)
		}
	}
	return runtime, memory
}

func getSubduedSpecs(
	runtimeUpper int, runtimeLower int,
	memUpper int, memLower int) (int, int) {

	var runtime, memory int
	flag := util.GetRandBool()
	if runtime, memory = runtimeUpper, memUpper; flag {
		runtime, memory = (runtimeUpper+runtimeLower)/2, (memUpper+memLower)/2
	}
	return runtime, memory
}

func ParseInvocationTrace(traceFile string, traceDuration int) FunctionTraces {
	log.Infof("Parsing function invocation trace: %s", traceFile)

	var functions []Function
	// Indices of functions to invoke.
	invocationIdices := make([][]int, traceDuration)
	totalInvocations := make([]int, traceDuration)

	csvfile, err := os.Open(traceFile)
	if err != nil {
		log.Fatal("Failed to load CSV file", err)
	}

	reader := csv.NewReader(csvfile)
	funcIdx := -1
	for {
		// Read each record from csv
		record, err := reader.Read()

		if err != nil {
			if err == io.EOF {
				break
			}
			log.Fatal(err)
		}

		// Skip header
		if funcIdx != -1 {
			// Parse function
			function := Function{appHash: record[1], hash: record[2]}
			function.name = fmt.Sprintf("%s-%d", "trace-func", funcIdx)
			function.url = fmt.Sprintf("%s.%s.%s:%s", function.name, namespace, gatewayUrl, port)
			functions = append(functions, function)

			// Parse invocations
			headerLen := 4
			for i := headerLen; i < headerLen+traceDuration; i++ {
				minute := i - headerLen
				num, err := strconv.Atoi(record[i])
				util.Check(err)

				for j := 0; j < num; j++ {
					//* For `num` invocationso of function of index `funcIdx`,
					//* we append (N*funcIdx) to the `invocationIdices`.
					invocationIdices[minute] = append(invocationIdices[minute], funcIdx)
				}
				totalInvocations[minute] = totalInvocations[minute] + num
			}
		}
		funcIdx++
	}

	return FunctionTraces{
		Functions:                  functions,
		InvocationsPerMinute:       invocationIdices,
		TotalInvocationsEachMinute: totalInvocations,
		path:                       traceFile,
	}
}

/** Get execution times in ms. */
func getDurationStats(record []string) FunctionDurationStats {
	return FunctionDurationStats{
		average:       parseToInt(record[3]),
		count:         parseToInt(record[4]),
		minimum:       parseToInt(record[5]),
		maximum:       parseToInt(record[6]),
		percentile0:   parseToInt(record[7]),
		percentile1:   parseToInt(record[8]),
		percentile25:  parseToInt(record[9]),
		percentile50:  parseToInt(record[10]),
		percentile75:  parseToInt(record[11]),
		percentile99:  parseToInt(record[12]),
		percentile100: parseToInt(record[13]),
	}
}

func parseToInt(text string) int {
	if s, err := strconv.ParseFloat(text, 32); err == nil {
		return int(s)
	} else {
		log.Fatal("Failed to parse duration record", err)
		return 0
	}
}

func ParseDurationTrace(trace *FunctionTraces, traceFile string) {
	log.Infof("Parsing function duration trace: %s", traceFile)

	// Create mapping from function hash to function position in trace
	funcPos := make(map[string]int)
	for i, function := range trace.Functions {
		funcPos[function.hash] = i
	}

	csvfile, err := os.Open(traceFile)
	if err != nil {
		log.Fatal("Failed to load CSV file", err)
	}

	reader := csv.NewReader(csvfile)
	l := -1
	foundDurations := 0
	for {
		// Read each record from csv
		record, err := reader.Read()

		if err != nil {
			if err == io.EOF {
				break
			}
			log.Fatal(err)
		}

		// Skip header
		if l != -1 {
			// Parse durations
			functionHash := record[2]
			funcIdx, contained := funcPos[functionHash]
			if contained {
				trace.Functions[funcIdx].durationStats = getDurationStats(record)
				foundDurations += 1
			}
		}
		l++
	}

	if foundDurations != len(trace.Functions) {
		log.Fatal("Could not find all durations for all invocations in the supplied trace ", foundDurations, len(trace.Functions))
	}
}

/** Get memoru usages in MB. */
func getMemoryStats(record []string) FunctionMemoryStats {
	return FunctionMemoryStats{
		count:         parseToInt(record[3]),
		average:       parseToInt(record[4]),
		percentile1:   parseToInt(record[5]),
		percentile5:   parseToInt(record[6]),
		percentile25:  parseToInt(record[7]),
		percentile50:  parseToInt(record[8]),
		percentile75:  parseToInt(record[9]),
		percentile95:  parseToInt(record[10]),
		percentile99:  parseToInt(record[11]),
		percentile100: parseToInt(record[12]),
	}
}

func ParseMemoryTrace(trace *FunctionTraces, traceFile string) {
	log.Infof("Parsing function memory trace: %s", traceFile)

	// Create mapping from function hash to function position in trace
	funcPos := make(map[string]int)
	for i, function := range trace.Functions {
		funcPos[function.appHash] = i
	}

	csvfile, err := os.Open(traceFile)
	if err != nil {
		log.Fatal("Failed to load CSV file", err)
	}

	r := csv.NewReader(csvfile)
	l := -1
	foundDurations := 0
	for {
		// Read each record from csv
		record, err := r.Read()

		if err != nil {
			if err == io.EOF {
				break
			}
			log.Fatal(err)
		}

		// Skip header
		if l != -1 {
			// Parse durations
			functionHash := record[1]
			funcIdx, contained := funcPos[functionHash]
			if contained {
				trace.Functions[funcIdx].memoryStats = getMemoryStats(record)
				foundDurations += 1
			}
		}
		l++
	}

	if foundDurations != len(trace.Functions) {
		log.Fatal("Could not find all memory footprints for all invocations in the supplied trace ", foundDurations, len(trace.Functions))
	}
}

// func hash(s string) uint32 {
// 	h := fnv.New32a()
// 	h.Write([]byte(s))
// 	return h.Sum32()
// }

func (f *Function) SetHash(hash int) {
	f.hash = fmt.Sprintf("%015d", hash)
}

func (f *Function) SetName(name string) {
	f.name = name
}

func (f *Function) SetStatus(b bool) {
	f.deployed = b
}

func (f *Function) GetStatus() bool {
	return f.deployed
}

func (f *Function) GetName() string {
	return f.name
}

func (f *Function) GetUrl() string {
	return f.url
}

func (f *Function) SetUrl(url string) {
	f.url = url
}

// // Functions is an object for unmarshalled JSON with functions to deploy.
// type Functions struct {
// 	Functions []FunctionType `json:"functions"`
// }

// type FunctionType struct {
// 	Name string `json:"name"`
// 	File string `json:"file"`

// 	// Number of functions to deploy from the same file (with different names)
// 	Count int `json:"count"`

// 	Eventing    bool   `json:"eventing"`
// 	ApplyScript string `json:"applyScript"`
// }

// func getFuncSlice(file string) []fc.FunctionType {
// 	log.Info("Opening JSON file with functions: ", file)
// 	byteValue, err := ioutil.ReadFile(file)
// 	if err != nil {
// 		log.Fatal(err)
// 	}
// 	var functions fc.Functions
// 	if err := json.Unmarshal(byteValue, &functions); err != nil {
// 		log.Fatal(err)
// 	}
// 	return functions.Functions
// }
