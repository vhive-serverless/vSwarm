// MIT License
//
// Copyright (c) 2022 Dohyun Park and EASE lab
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

package main

import (
	"flag"
	"os"
	"path/filepath"

	elasticsearch "github.com/elastic/go-elasticsearch/v7"

	log "github.com/sirupsen/logrus"
)

var (
	elasticsearchURL = flag.String("elasticsearchURL", "http://127.0.0.1:9200", "Elasticsearch URL")
	pageSize         = flag.Int("pageSize", 100, "The number of traces to fetch per page while paginating")
	zipkinURL        = flag.String("zipkinURL", "http://127.0.0.1:8080", "Zipkin URL")
	fileName         = flag.String("fileName", "plot.html", "output file name")
	latencyType      = flag.String("latencyType", "e2e", "which latency type to plot, e2e or system(e2e - leaf trace execution time)")
)

func main() {
	flag.Parse()
	switch *latencyType {
	case "e2e", "system":
	default:
		log.Fatalf("latencyType must be one of e2e or system")
	}

	es, err := elasticsearch.NewClient(elasticsearch.Config{
		Addresses: []string{*elasticsearchURL},
	})
	if err != nil {
		log.Fatal(err)
	}
	l := NewLoader(es)

	var traces []Trace
	l.GetTraces(*pageSize, &traces)

	parsedTraces, durations := ParseTraces(traces, *latencyType)
	scatter := PlotGraph(parsedTraces, durations, *zipkinURL)

	if filepath.Ext(*fileName) != ".html" {
		*fileName += ".html"
	}
	f, _ := os.Create(*fileName)
	if err := scatter.Render(f); err != nil {
		log.Errorf("Error rendering plot: %s", err)
	}
}
