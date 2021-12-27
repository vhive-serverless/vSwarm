package trace

import (
	"sync"
)

type MinuteInvocationRecord struct {
	Rps              int   `csv:"request_per_sec"`
	MinuteIdx        int   `csv:"index"`
	Duration         int64 `csv:"duration"`
	IdleDuration     int64 `csv:"idle_duration"`
	NumFuncRequested int   `csv:"num_func_requested"`
	NumFuncInvoked   int   `csv:"num_func_invoked"`
	NumFuncFailed    int   `csv:"num_func_failed"`
}

type LatencyRecord struct {
	// Locking should not be necessary (https://stackoverflow.com/a/29497244) but just in case.
	*sync.Mutex

	Rps       int    `csv:"request_per_sec"`
	Timestamp int64  `csv:"timestamp"`
	FuncName  string `csv:"func_name"`
	Latency   int64  `csv:"latency"`
	Runtime   uint32 `csv:"runtime"`
	Memory    uint32 `csv:"memory"`
}
