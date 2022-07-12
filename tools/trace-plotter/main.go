package main

import (
	"flag"
	"net/http"
	"os"
	"strconv"

	"github.com/ease-lab/vSwarm/tools/trace-plotter/loader"
	"github.com/ease-lab/vSwarm/tools/trace-plotter/models"
	"github.com/ease-lab/vSwarm/tools/trace-plotter/plotter"

	"github.com/elastic/go-elasticsearch/v7"

	log "github.com/sirupsen/logrus"
)

var (
	useZipkinApi     = flag.Bool("useZipkinApi", false, "use zipkin api")
	elasticsearchURL = flag.String("elasticsearchURL", "http://127.0.0.1:9200", "Elasticsearch URL")
	pageSize         = flag.Int("pageSize", 100, "Trace request page size")
	zipkinURL        = flag.String("zipkinURL", "http://127.0.0.1:8080", "Zipkin URL")
	asWebServer      = flag.Bool("asWebServer", false, "Run as a webserver")
)

func main() {
	flag.Parse()
	var l loader.Loader
	if *useZipkinApi {
		log.Info("Using zipkin api")
		l = loader.NewZipkinApiLoader(*zipkinURL)
	} else {
		log.Info("Using elasticsearch api")
		es, err := elasticsearch.NewClient(elasticsearch.Config{
			Addresses: []string{*elasticsearchURL},
		})
		if err != nil {
			log.Fatal(err)
		}
		l = loader.NewEsLoader(es)
	}

	if *asWebServer {
		http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
			var (
				traces []models.Trace
				size   = *pageSize
				url    = *zipkinURL
			)

			if r.FormValue("pageSize") != "" {
				s, err := strconv.Atoi(r.FormValue("pageSize"))
				if err != nil {
					log.Errorf("Error parsing page size: %s", err)
				}
				size = s
			}

			if r.FormValue("zipkinURL") != "" {
				url = r.FormValue("zipkinURL")
			}

			l.GetTraces(size, &traces)

			rootTraces, durations := plotter.ParseTraces(traces)
			scatter := plotter.PlotGraph(rootTraces, durations, url)

			scatter.Render(w)
		})
		log.Info("Starting server :8081")
		err := http.ListenAndServe(":8081", nil)
		if err != nil {
			log.Fatal(err)
		}
	} else {
		var traces []models.Trace
		l.GetTraces(*pageSize, &traces)

		rootTraces, durations := plotter.ParseTraces(traces)
		scatter := plotter.PlotGraph(rootTraces, durations, *zipkinURL)

		f, _ := os.Create("plot.html")
		scatter.Render(f)
	}
}
