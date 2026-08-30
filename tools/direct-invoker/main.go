package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"flag"
	"fmt"
	"math/rand"
	"net"
	"os"
	"strconv"
	"strings"
	"time"

	grpcclients "github.com/vhive-serverless/vSwarm-proto/grpcclient"
	"google.golang.org/grpc/metadata"
)

type config struct {
	address       string
	functionName  string
	image         string
	revision      string
	functionArgs  string
	functionEnv   string
	functionPort  string
	generator     string
	value         string
	method        string
	lowerBound    int
	upperBound    int
	seed          int64
	sequenceIndex int
	timeout       time.Duration
	allowError    bool
}

func (c config) validate() error {
	host, port, err := net.SplitHostPort(c.address)
	if err != nil || host == "" || port == "" {
		return fmt.Errorf("invalid address %q", c.address)
	}
	if _, err := strconv.ParseUint(port, 10, 16); err != nil {
		return fmt.Errorf("invalid address port %q", port)
	}
	if c.functionName == "" || c.image == "" || c.revision == "" {
		return errors.New("function-name, image, and revision are required")
	}
	functionPort, err := strconv.ParseUint(c.functionPort, 10, 16)
	if err != nil || functionPort == 0 {
		return fmt.Errorf("invalid function-port %q", c.functionPort)
	}
	switch c.generator {
	case "fixed", "unique", "linear", "random":
	default:
		return fmt.Errorf("invalid generator %q", c.generator)
	}
	if c.lowerBound < 0 || c.upperBound < 0 || c.upperBound < c.lowerBound {
		return fmt.Errorf("invalid bounds [%d,%d]", c.lowerBound, c.upperBound)
	}
	if c.generator == "random" && c.upperBound <= c.lowerBound && strings.HasPrefix(c.functionName, "aes-") {
		return fmt.Errorf("AES random bounds must satisfy lower < upper")
	}
	if c.sequenceIndex < 0 {
		return errors.New("sequence-index must be non-negative")
	}
	if c.timeout <= 0 {
		return errors.New("timeout must be positive")
	}
	return nil
}

func generatorType(value string) grpcclients.GeneratorType {
	switch value {
	case "linear":
		return grpcclients.Linear
	case "random":
		return grpcclients.Random
	default:
		return grpcclients.Unique
	}
}

func invoke(c config) (string, time.Duration, error) {
	if err := c.validate(); err != nil {
		return "", 0, err
	}
	host, port, _ := net.SplitHostPort(c.address)
	ctx, cancel := context.WithTimeout(context.Background(), c.timeout)
	defer cancel()
	ctx = metadata.NewOutgoingContext(ctx, metadata.Pairs(
		"image", c.image,
		"revision", c.revision,
		"args", c.functionArgs,
		"env", c.functionEnv,
		"functionport", c.functionPort,
	))

	serviceName := grpcclients.FindServiceName(c.functionName)
	client := grpcclients.FindGrpcClient(serviceName)
	if err := client.Init(ctx, host, port); err != nil {
		return "", 0, fmt.Errorf("initialize %s client: %w", serviceName, err)
	}
	defer client.Close()

	input := grpcclients.Input{Value: c.value, Method: c.method}
	if c.generator != "fixed" {
		generator := client.GetGenerator()
		generator.SetGenerator(generatorType(c.generator))
		generator.SetLowerBound(c.lowerBound)
		generator.SetUpperBound(c.upperBound)
		generator.SetValue(c.value)
		generator.SetMethod(c.method)
		rand.Seed(c.seed)
		for i := 0; i <= c.sequenceIndex; i++ {
			input = generator.Next()
		}
	}

	started := time.Now()
	reply, err := client.Request(ctx, input)
	elapsed := time.Since(started)
	if err != nil {
		return "", elapsed, err
	}
	if !c.allowError && (strings.Contains(reply, "Error:") || strings.Contains(reply, "Failed")) {
		return reply, elapsed, fmt.Errorf("function returned an application error")
	}
	return reply, elapsed, nil
}

func main() {
	c := config{}
	flag.StringVar(&c.address, "address", "", "outer SnapShare relay address (host:port)")
	flag.StringVar(&c.functionName, "function-name", "", "vSwarm workload name")
	flag.StringVar(&c.image, "image", "", "container image metadata")
	flag.StringVar(&c.revision, "revision", "", "snapshot revision metadata")
	flag.StringVar(&c.functionArgs, "args", "", "function process arguments metadata")
	flag.StringVar(&c.functionEnv, "env", "", "function environment metadata")
	flag.StringVar(&c.functionPort, "function-port", "50051", "native function gRPC port")
	flag.StringVar(&c.generator, "generator", "unique", "input generator: fixed, unique, linear, or random")
	flag.StringVar(&c.value, "value", "", "generator default value")
	flag.StringVar(&c.method, "function-method", "default", "benchmark-specific method")
	flag.IntVar(&c.lowerBound, "lower-bound", 1, "generator lower bound")
	flag.IntVar(&c.upperBound, "upper-bound", 10, "generator upper bound")
	flag.Int64Var(&c.seed, "seed", 1, "deterministic math/rand seed")
	flag.IntVar(&c.sequenceIndex, "sequence-index", 0, "zero-based item in the deterministic generator sequence")
	flag.DurationVar(&c.timeout, "timeout", 900*time.Second, "entire invocation deadline")
	flag.BoolVar(&c.allowError, "allow-error-reply", false, "allow application Error:/Failed replies")
	flag.Parse()

	reply, elapsed, err := invoke(c)
	digest := sha256.Sum256([]byte(reply))
	if reply != "" {
		fmt.Println(reply)
	}
	fmt.Printf("DIRECT_REQUEST_NS=%d REPLY_BYTES=%d REPLY_SHA256=%s\n", elapsed.Nanoseconds(), len(reply), hex.EncodeToString(digest[:]))
	if err != nil {
		fmt.Fprintf(os.Stderr, "direct invocation failed: %v\n", err)
		os.Exit(1)
	}
}
