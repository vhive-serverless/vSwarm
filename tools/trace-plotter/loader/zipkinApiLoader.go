package loader

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"

	"github.com/ease-lab/vSwarm/tools/trace-plotter/models"

	log "github.com/sirupsen/logrus"
)

type ZipkinApiLoader struct {
	zipkinHost string
	client     *http.Client
}

func NewZipkinApiLoader(zipkinHost string) *ZipkinApiLoader {
	return &ZipkinApiLoader{
		zipkinHost: zipkinHost,
		client:     http.DefaultClient,
	}
}

func (l *ZipkinApiLoader) GetTraces(pageSize int, traces *[]models.Trace) {
	u, err := url.Parse(fmt.Sprintf("%s%s", l.zipkinHost, "/zipkin/api/v2/traces"))
	if err != nil {
		log.Errorf("Error parsing url: %s", err)
	}
	r := [][]models.Trace{}

	q := u.Query()
	q.Set("limit", strconv.Itoa(pageSize))
	q.Set("lookback", strconv.Itoa(3600000*24))
	u.RawQuery = q.Encode()
	log.Debugf("Requesting %s", u.String())

	req, err := http.NewRequest(http.MethodGet, u.String(), nil)
	if err != nil {
		log.Error("client: could not create request: %s\n", err)
	}

	res, err := l.client.Do(req)
	if err != nil {
		log.Errorf("client: error making http request: %s\n", err)
	}

	defer res.Body.Close()
	if err := json.NewDecoder(res.Body).Decode(&r); err != nil {
		log.Errorf("Error parsing the response body: %s", err)
	}
	for t := range r {
		*traces = append(*traces, r[t]...)
	}
}
