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
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"time"

	elasticsearch "github.com/elastic/go-elasticsearch/v7"
	"github.com/elastic/go-elasticsearch/v7/esapi"
	log "github.com/sirupsen/logrus"
)

type Loader struct {
	es *elasticsearch.Client
}

func NewLoader(es *elasticsearch.Client) *Loader {
	return &Loader{es: es}
}

var query = map[string]interface{}{
	"query": map[string]interface{}{
		"bool": map[string]interface{}{
			"must_not": map[string]interface{}{
				"term": map[string]interface{}{
					"name": "probe",
				},
			},
		},
	},
}

func (l *Loader) GetTraces(pageSize int, traces *[]Trace) {
	var r EsResponse
	var buf bytes.Buffer

	if err := json.NewEncoder(&buf).Encode(query); err != nil {
		log.Errorf("Error encoding query: %s", err)
	}
	var batchNum int
	res, err := l.es.Search(
		l.es.Search.WithContext(context.Background()),
		l.es.Search.WithIndex("zipkin*"),
		l.es.Search.WithBody(&buf),
		l.es.Search.WithSort("_doc:desc"),
		l.es.Search.WithSize(pageSize),
		l.es.Search.WithScroll(time.Minute),
	)
	if err != nil {
		log.Errorf("Error getting response: %s", err)
	}
	defer res.Body.Close()

	r, err = getEsResponse(res)
	if err != nil {
		log.Errorf("Error getting response: %s", err)
		return
	}

	for _, hit := range r.Hits.Hits {
		*traces = append(*traces, hit.Trace)
	}

	scrollID := r.ScrollID
	for {
		batchNum++
		res, err := l.es.Scroll(l.es.Scroll.WithScrollID(scrollID), l.es.Scroll.WithScroll(time.Minute))
		defer res.Body.Close()
		if err != nil {
			log.Errorf("Error: %s", err)
		}
		r, err := getEsResponse(res)
		if err != nil {
			log.Errorf("Error: %s", err)
			break
		}

		if len(r.Hits.Hits) < 1 {
			break
		}
		for _, hit := range r.Hits.Hits {
			*traces = append(*traces, hit.Trace)
		}
		scrollID = r.ScrollID
	}
}

func getEsResponse(res *esapi.Response) (EsResponse, error) {
	var r EsResponse
	if res.IsError() {
		return r, errors.New("Error Response " + res.String())
	}

	if err := json.NewDecoder(res.Body).Decode(&r); err != nil {
		return r, err
	}
	return r, nil
}
