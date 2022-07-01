package main

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestProfilerRun(t *testing.T) {
	fileName := "testFile"

	p, err := NewProfiler(-1, 100, 1, "", fileName, -1, -1)
	require.NoError(t, err, "Cannot create a profiler instance")
	err = p.Run()
	require.EqualError(t, err, "profiler execution time is less than 0s", "Failed running profiler")

	p, err = NewProfiler(0, 1, 1, "", fileName, -1, -1)
	require.NoError(t, err, "Cannot create a profiler instance")
	err = p.Run()
	require.EqualError(t, err, "profiler print interval is less than 10ms", "Failed running profiler")

	p, err = NewProfiler(0, 100, 1, "", fileName, -1, -1)
	require.NoError(t, err, "Cannot create a profiler instance")
	err = p.Run()
	require.NoError(t, err, "profiler run returned error: %v.", err)

	time.Sleep(1 * time.Second)
}
