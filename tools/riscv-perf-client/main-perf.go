/* MIT License
 *
 * Copyright (c) 2022 David Schall and EASE lab
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */

// Package main implements a client for Greeter service.
package main

// go build -o client main.go
// CGO_ENABLED=0 GOARCH=riscv64 GOOS=linux go build '-extldflags "-static"' -o clientPerf main.go
import (
	"context"
	"flag"
	"os"
	"os/exec"
	"syscall"
	"time"
	log "github.com/sirupsen/logrus"
	"strings"
	grpcClients "github.com/vhive-serverless/vSwarm-proto/grpcclient"
)

const (
	defaultInput = "1"
)

var (
	print_version  = flag.Bool("version", false, "Version of client")
	functionName   = flag.String("function-name", "helloworld", "Specify the name of the function being invoked.")
	event1         = flag.String("event1", "cpu-cycles", "Event 1 to monitor")
	event2         = flag.String("event2", "instructions", "Event 2 to monitor")
	url            = flag.String("url", "0.0.0.0", "The url to connect to")
	port           = flag.String("port", "50051", "the port to connect to")
	input          = flag.String("input", defaultInput, "Input to the function")
	functionMethod = flag.String("function-method", "0", "Which method of benchmark to invoke")
	numInvoke      = flag.Int("n", 10, "Number of invocations")
	numWarm        = flag.Int("w", 0, "Number of invocations for warming")
	delay          = flag.Int("delay", 0, "Add a delay between sending requests (us)")
	logfile        = flag.String("logging", "", "Log to file instead of standart out")
	m5_enable      = flag.Bool("m5ops", false, "Enable m5 magic instructions")
	latencyOutput  = flag.String("latency-output", "", "Output file for latency results")
	// Client
	client    grpcClients.GrpcClient
	generator grpcClients.Generator
)

func main() {
	flag.Parse()


	log.Println("-- Invokation test --")

	ctx := context.Background()


	serviceName := grpcClients.FindServiceName(*functionName)
	client = grpcClients.FindGrpcClient(serviceName)

	client.Init(ctx, *url, *port)
	defer client.Close()

	log.Printf("Connection established.\n")

	generator = client.GetGenerator()
	generator.SetGenerator(grpcClients.Unique)
	generator.SetValue(*input)
	generator.SetMethod(*functionMethod)
	pkt := generator.Next()

	var reply string
	var err error
	log.Printf("event1: %s, event2: %s\n", *event1, *event2)
	perfdata := strings.TrimSuffix(*latencyOutput, ".txt") +"Cold.txt"
	event:= *event1 + "," + *event2
	perfCmd := exec.Command("perf", "stat","-e", event, "-C", "3" , "-o", perfdata, "--append")
    perfCmd.Stderr = os.Stderr
    err = perfCmd.Start()
	if err != nil {
		log.Fatalf("Failed to start perf: %v", err)
	}
	time.Sleep(500 * time.Millisecond)



	reply,err = client.Request(ctx, pkt)
	if err != nil {	
		log.Fatalf("Failed to invoke: %v", err)
	}
	err = perfCmd.Process.Signal(syscall.SIGINT)
	if err != nil {
		log.Fatalf("Failed to stop perf: %v", err)
    }
	


	log.Printf("Greeting: %s", reply)

	if *numWarm > 0 {
		warmFunction(ctx)
	}
	invokeFunction(ctx, *numInvoke)

	log.Printf("Finished invoking: %s", reply)
	if err != nil {
		log.Fatalf("Failed to invoke: %v", err)
	}	
	log.Printf("SUCCESS: Calling functions for %d times", *numInvoke)
}

func warmFunction(ctx context.Context) {
	log.Printf("Invoke functions %d times for warming", *numWarm)


	invokeFunction(ctx, *numWarm )

}

func invokeFunction(ctx context.Context, n int)  {

	mod := 1
	if n > 2*5 {
		mod = n / 5
	}
	var reply string

	for i := 0; i < n-1; i++ {
		pkt := generator.Next()
		reply,_ = client.Request(ctx, pkt)
		print("reply: ", reply, "\n")
		if i%mod == 0 {
			log.Printf("Invoked for %d times\n", i)
		}
		if *delay > 0 {
			time.Sleep(time.Duration(*delay) * time.Microsecond)
		}
	}
	pkt := generator.Next()
	perfdata := strings.TrimSuffix(*latencyOutput, ".txt") +"Warm.txt"
	event:= *event1 + "," + *event2
	perfCmd := exec.Command("perf", "stat","-e",event, "-C", "3", "-o", perfdata, "--append")
    perfCmd.Stderr = os.Stderr
    err := perfCmd.Start()
	if err != nil {
		log.Fatalf("Failed to start perf: %v", err)
	}
	time.Sleep(500 * time.Millisecond)

	_,_=client.Request(ctx, pkt)

	if err != nil {	
		log.Fatalf("Failed to invoke: %v", err)
	}
	err = perfCmd.Process.Signal(syscall.SIGINT)
	if err != nil {
		log.Fatalf("Failed to stop perf: %v", err)
	}
	err = perfCmd.Wait()

		log.Printf("Invoked for %d times\n", n)

		
}

func invokeFunctionInstrumented(ctx context.Context, n int) {
	mod := 1
	if n > 2*5 {
		mod = n / 5
	}
	for i := 0; i < n; i++ {

		pkt := generator.Next()


		client.Request(ctx, pkt)

		if i%mod == 0 {
			log.Printf("Invoked for %d times\n", i)
		}

		if *delay > 0 {
			time.Sleep(time.Duration(*delay) * time.Microsecond)
		}
	}
}
