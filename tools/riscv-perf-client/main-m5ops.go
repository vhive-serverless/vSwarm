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

// CGO_ENABLED=0 GOARCH=riscv64 GOOS=linux go build -ldflags='-extldflags "-static"' -o client main.go

// Package main implements a client for Greeter service.
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"time"
	log "github.com/sirupsen/logrus"

	grpcClients "github.com/vhive-serverless/vSwarm-proto/grpcclient"
)

const (
	defaultInput = "1"
)

var (
	print_version  = flag.Bool("version", false, "Version of client")
	functionName   = flag.String("function-name", "helloworld", "Specify the name of the function being invoked.")
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
	// m5        m5ops.M5Ops
)

func main() {
	flag.Parse()

	if *logfile != "" {
		file, err := os.OpenFile(*logfile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			log.Fatal(err)
		}
		defer file.Close()
		log.SetOutput(file)
	}

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
	if *m5_enable {	
		cmd := exec.Command("m5" ,"checkpoint")
		stdout, err := cmd.Output()
		if err != nil {
			
			log.Fatal(err)
		}
		fmt.Println(string(stdout))
	}

	var reply string
	var err error
	var firstExec time.Duration
	print("m5_enable: ", *m5_enable, "\n")
	if *m5_enable {
		
		cmd := exec.Command("m5" ,"resetstats")
		stdout, err := cmd.Output()
	
		if err != nil {
		
			log.Fatal(err)
		}
	
		fmt.Println(string(stdout))
		reply,err = client.Request(ctx, pkt)
		cmd = exec.Command("m5" ,"dumpstats")
		stdout, err = cmd.Output()
	
		if err != nil {
			log.Fatal(err)
		}
	
		fmt.Println(string(stdout))
	}else{
		timeStart := time.Now()
		reply,err = client.Request(ctx, pkt)
		timeEnd := time.Now()
		if err != nil {	
			log.Fatalf("Failed to invoke: %v", err)
		}
		firstExec = timeEnd.Sub(timeStart)
	}
	log.Printf("Greeting: %s", reply)

	if *numWarm > 0 {
		warmFunction(ctx)
	}

	var executionTimes []time.Duration

	if *m5_enable {
		invokeFunction(ctx, *numInvoke, false)
		
	}else{
		executionTimes = invokeFunction(ctx, *numInvoke, true)

		if *latencyOutput != "" {
			file, err := os.OpenFile(*latencyOutput, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
			if err != nil {
				log.Fatal(err)
			}
			defer file.Close()
			file.WriteString(*functionName + "\n")
			file.WriteString(fmt.Sprintf("%d\n", firstExec.Microseconds()))
			for _, latency := range executionTimes {
				file.WriteString(fmt.Sprintf("%d\n", latency.Microseconds()))
			}
		}
	}
	log.Printf("Finished invoking: %s", reply)
	if err != nil {
		log.Fatalf("Failed to invoke: %v", err)
	}	
	log.Printf("SUCCESS: Calling functions for %d times", *numInvoke)
}

func warmFunction(ctx context.Context) {
	log.Printf("Invoke functions %d times for warming", *numWarm)


	invokeFunction(ctx, *numWarm , true)

}

func invokeFunction(ctx context.Context, n int, dataCollect bool) []time.Duration {


	var executionTimes []time.Duration
	mod := 1
	if n > 2*5 {
		mod = n / 5
	}
	var reply string
	if dataCollect {
		for i := 0; i < n; i++ {

			pkt := generator.Next()
			timeStart := time.Now()
			reply,_ = client.Request(ctx, pkt) 
			timeEnd := time.Now()
			print("reply: ", reply, "\n")
			elapsedTime := timeEnd.Sub(timeStart)
			executionTimes = append(executionTimes, elapsedTime)
			if i%mod == 0 {
				log.Printf("Invoked for %d times\n", i)
			}
			if *delay > 0 {
				time.Sleep(time.Duration(*delay) * time.Microsecond)
			}
		}
		return executionTimes
	}else{
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
		// exec.Command("echo m5 resetstats")
		cmd := exec.Command("m5" ,"resetstats")
		stdout, err := cmd.Output()
	
		if err != nil {
			log.Fatal(err)
		}
	
		fmt.Println(string(stdout))
		client.Request(ctx, pkt)
		cmd = exec.Command("m5" ,"dumpstats")
		stdout, err = cmd.Output()
	
		if err != nil {
			log.Fatal(err)
		}
	
		fmt.Println(string(stdout))
		log.Printf("Invoked for %d times\n", n)

		return nil
	}
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
