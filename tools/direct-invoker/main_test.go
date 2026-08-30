package main

import (
	"testing"
	"time"

	grpcclients "github.com/vhive-serverless/vSwarm-proto/grpcclient"
)

func validConfig() config {
	return config{
		address:       "10.0.1.1:8080",
		functionName:  "image-rotate-go",
		image:         "registry/image:tag",
		revision:      "snapshot-a-b",
		functionPort:  "50051",
		generator:     "unique",
		lowerBound:    1,
		upperBound:    10,
		sequenceIndex: 0,
		timeout:       time.Second,
	}
}

func TestConfigValidate(t *testing.T) {
	tests := []struct {
		name   string
		mutate func(*config)
	}{
		{name: "bad-address", mutate: func(c *config) { c.address = "10.0.1.1" }},
		{name: "bad-function-port", mutate: func(c *config) { c.functionPort = "0" }},
		{name: "bad-generator", mutate: func(c *config) { c.generator = "unknown" }},
		{name: "negative-sequence", mutate: func(c *config) { c.sequenceIndex = -1 }},
		{name: "aes-empty-random-range", mutate: func(c *config) {
			c.functionName = "aes-go"
			c.generator = "random"
			c.lowerBound = 10
			c.upperBound = 10
		}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			c := validConfig()
			test.mutate(&c)
			if err := c.validate(); err == nil {
				t.Fatal("validate unexpectedly succeeded")
			}
		})
	}
	if err := validConfig().validate(); err != nil {
		t.Fatalf("valid config: %v", err)
	}
}

func TestGeneratorType(t *testing.T) {
	if got := generatorType("unique"); got != grpcclients.Unique {
		t.Fatalf("unique = %v", got)
	}
	if got := generatorType("linear"); got != grpcclients.Linear {
		t.Fatalf("linear = %v", got)
	}
	if got := generatorType("random"); got != grpcclients.Random {
		t.Fatalf("random = %v", got)
	}
	c := validConfig()
	c.generator = "fixed"
	if err := c.validate(); err != nil {
		t.Fatalf("fixed config: %v", err)
	}
}
