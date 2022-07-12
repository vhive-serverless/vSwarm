package loader

import (
	"bytes"
	"context"
	"encoding/json"
	"strings"
	"time"

	"github.com/ease-lab/vSwarm/tools/trace-plotter/models"

	"github.com/elastic/go-elasticsearch/v7"
	log "github.com/sirupsen/logrus"
)

type EsLoader struct {
	es *elasticsearch.Client
}

func NewEsLoader(es *elasticsearch.Client) *EsLoader {
	return &EsLoader{
		es: es,
	}
}

func (l *EsLoader) GetTraces(pageSize int, traces *[]models.Trace) {
	var r models.EsResponse
	var buf bytes.Buffer
	query := map[string]interface{}{
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
	if res.IsError() {
		log.Errorf("Error: %s", res.String())
	}
	if err := json.NewDecoder(res.Body).Decode(&r); err != nil {
		log.Errorf("Error parsing the response body: %s", err)
	}

	for _, hit := range r.Hits.Hits {
		*traces = append(*traces, hit.Trace)
	}

	scrollID := r.ScrollID
	log.Debugln("Batch   ", batchNum)
	log.Debugln("ScrollID", scrollID)
	log.Debugln(strings.Repeat("-", 80))
	for {
		batchNum++
		var r models.EsResponse
		res, err := l.es.Scroll(l.es.Scroll.WithScrollID(scrollID), l.es.Scroll.WithScroll(time.Minute))
		if err != nil {
			log.Errorf("Error: %s", err)
		}
		if res.IsError() {
			log.Errorf("Error response: %s", res)
		}

		if err := json.NewDecoder(res.Body).Decode(&r); err != nil {
			log.Errorf("Error parsing the response body: %s", err)
		}

		if len(r.Hits.Hits) < 1 {
			log.Debugln("Finished")
			break
		} else {
			log.Debugln("Batch   ", batchNum)
			log.Debugln("ScrollID", scrollID)
			log.Debugln(strings.Repeat("-", 80))
		}
		for _, hit := range r.Hits.Hits {
			*traces = append(*traces, hit.Trace)
		}
		scrollID = r.ScrollID
	}
}
