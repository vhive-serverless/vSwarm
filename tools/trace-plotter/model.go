// MIT License
//
// Copyright (c) 2022 Dohyun Park and EASL lab
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
	"errors"
	"sort"
	"strconv"
)

type EsResponse struct {
	Hits     Hits   `json:"hits"`
	ScrollID string `json:"_scroll_id"`
}

type Hits struct {
	Total Total `json:"total"`
	Hits  []Hit `json:"hits"`
}

type Hit struct {
	Index string `json:"_index"`
	Type  string `json:"_type"`
	ID    string `json:"_id"`
	Trace Trace  `json:"_source"`
}

type Trace struct {
	TraceID         string        `json:"traceId"`
	Duration        int64         `json:"duration"`
	LocalEndpoint   LocalEndpoint `json:"localEndpoint"`
	TimestampMillis int64         `json:"timestamp_millis"`
	Name            string        `json:"name"`
	ID              string        `json:"id"`
	ParentID        string        `json:"parentId"`
	Timestamp       int64         `json:"timestamp"`
	Kind            *string       `json:"kind,omitempty"`
	Annotations     []Annotation  `json:"annotations,omitempty"`
	Tags            *Tags         `json:"tags,omitempty"`

	SystemDuration int64
	Child          []*Trace
}

type Annotation struct {
	Timestamp int64  `json:"timestamp"`
	Value     string `json:"value"`
}

type LocalEndpoint struct {
	ServiceName string `json:"serviceName"`
	Ipv4        string `json:"ipv4"`
}

type Tags struct {
	HTTPHost                    string `json:"http.host"`
	HTTPMethod                  string `json:"http.method"`
	HTTPPath                    string `json:"http.path"`
	HTTPStatusCode              string `json:"http.status_code"`
	HTTPURL                     string `json:"http.url"`
	HTTPUserAgent               string `json:"http.user_agent"`
	OpencensusStatusDescription string `json:"opencensus.status_description"`
}

type Total struct {
	Value    int64  `json:"value"`
	Relation string `json:"relation"`
}

func (trace *Trace) DeepestLeaf() (deapest *Trace, depth int) {
	if len(trace.Child) == 0 {
		return trace, 1
	}
	for _, child := range trace.Child {
		child, d := child.DeepestLeaf()
		if d > depth {
			depth = d
			deapest = child
		}
	}
	return deapest, depth + 1
}

func (trace *Trace) GetHTTPStatusCode() (int, error) {
	if trace.Tags != nil {
		return strconv.Atoi(trace.Tags.HTTPStatusCode)
	}

	childCodes := []int{}
	for _, child := range trace.Child {
		if child.Tags != nil {
			if childCode, err := strconv.Atoi(child.Tags.HTTPStatusCode); err == nil {
				childCodes = append(childCodes, childCode)
			}
		}
	}

	if len(childCodes) == 0 {
		for _, child := range trace.Child {
			c, err := child.GetHTTPStatusCode()
			if err == nil {
				childCodes = append(childCodes, c)
			}
		}
	}

	if len(childCodes) == 0 {
		return -1, errors.New("no http status code found in trace")
	}

	sort.Ints(childCodes)
	return childCodes[len(childCodes)-1], nil
}
