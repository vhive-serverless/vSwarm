package plotter

import (
	"fmt"
	"sort"
	"strconv"

	log "github.com/sirupsen/logrus"

	"github.com/ease-lab/vSwarm/tools/trace-plotter/models"

	"github.com/go-echarts/go-echarts/v2/charts"
	"github.com/go-echarts/go-echarts/v2/opts"
	"github.com/gonum/stat"
)

func ParseTraces(traces []models.Trace) ([]*models.Trace, []float64) {

	m := make(map[string]*models.Trace)

	for i := range traces {
		if traces[i].Name != "probe" {
			m[traces[i].ID] = &traces[i]
		}
	}

	for i := range traces {
		if m[traces[i].ParentID] != nil {
			m[traces[i].ParentID].Child = append(m[traces[i].ParentID].Child, &traces[i])
		}
	}

	rootTraces := []*models.Trace{}
	for _, trace := range m {
		if m[trace.ParentID] == nil {
			rootTraces = append(rootTraces, trace)
		}
	}

	sort.Slice(rootTraces, func(i, j int) bool {
		return rootTraces[i].Duration < rootTraces[j].Duration
	})

	durations := make([]float64, len(rootTraces))
	for i, trace := range rootTraces {
		durations[i] = float64(trace.Duration)
	}

	return rootTraces, durations
}

func getPercentiles(rootTraces []*models.Trace, durations []float64) map[string]float64 {
	if len(durations) == 0 { // no traces
		return map[string]float64{
			"Mean":   0,
			"Median": 0,
			"90th":   0,
			"99th":   0,
		}
	}

	mean := stat.Mean(durations, nil)
	median := stat.Quantile(0.5, stat.Empirical, durations, nil)
	p90th := stat.Quantile(0.9, stat.Empirical, durations, nil)
	p99th := stat.Quantile(0.99, stat.Empirical, durations, nil)

	log.Debugf("Mean: %.2fms\n", mean/1000)
	log.Debugf("Median: %.2fms\n", median/1000)
	log.Debugf("90th: %.2fms\n", p90th/1000)
	log.Debugf("99th: %.2fms\n", p99th/1000)
	log.Debugf("========================================================\n")

	return map[string]float64{
		"Mean":   mean,
		"Median": median,
		"90th":   p90th,
		"99th":   p99th,
	}

}

func PlotGraph(rootTraces []*models.Trace, durations []float64, zipkinURL string) *charts.Scatter {
	successItems := make([]opts.ScatterData, 0)
	errorItems := make([]opts.ScatterData, 0)
	for _, trace := range rootTraces {
		resp, err := strconv.Atoi(trace.Tags.HTTPStatusCode)
		if err != nil || resp > 300 {
			errorItems = append(errorItems, opts.ScatterData{
				Name:         trace.TraceID,
				Value:        []interface{}{trace.Duration, stat.CDF(float64(trace.Duration), stat.Empirical, durations, nil)},
				Symbol:       "roundRect",
				SymbolSize:   10,
				SymbolRotate: 0,
			})
		} else {
			successItems = append(successItems, opts.ScatterData{
				Name:         trace.TraceID,
				Value:        []interface{}{trace.Duration, stat.CDF(float64(trace.Duration), stat.Empirical, durations, nil)},
				Symbol:       "roundRect",
				SymbolSize:   10,
				SymbolRotate: 0,
			})
		}
	}
	log.Debugf("Success: %d\n", len(successItems))
	log.Debugf("Error: %d\n", len(errorItems))
	log.Debugf("========================================================\n")

	var ToolTipFormatter = fmt.Sprintf(`
	function (info) {
		var item = info[0];
		var traceId = item.name;
		var zipkinURL = '%s/zipkin/traces/' + traceId;
		return 'Latency : ' + item.value[0] + ' (us)' + '<br>' + 'CDF : ' + item.value[1] + '<br>' + 'Go To : <a href="' + zipkinURL + '">' + 'zipkin' + '</a>';
	}
	`, zipkinURL)

	scatter := charts.NewScatter()
	scatter.PageTitle = "Zipkin Traces"

	scatter.SetGlobalOptions(
		charts.WithTitleOpts(opts.Title{Title: scatter.PageTitle}),
		charts.WithXAxisOpts(opts.XAxis{
			Name: "Latency",
			Type: "log",
		}),
		charts.WithYAxisOpts(opts.YAxis{
			Name: "CDF",
			Type: "value",
		}),
		charts.WithTooltipOpts(opts.Tooltip{
			Show:        true,
			Trigger:     "axis",
			TriggerOn:   "click",
			Formatter:   opts.FuncOpts(ToolTipFormatter),
			AxisPointer: &opts.AxisPointer{},
		}),
		charts.WithToolboxOpts(opts.Toolbox{
			Show:   true,
			Orient: "horizontal",
			Left:   "80%",
			Feature: &opts.ToolBoxFeature{
				SaveAsImage: &opts.ToolBoxFeatureSaveAsImage{
					Show:  true,
					Type:  "svg",
					Title: "Save",
				},
				DataZoom: &opts.ToolBoxFeatureDataZoom{
					Show:  true,
					Title: map[string]string{"zoom": "Data Zoom", "back": "Restore"},
				},
				DataView: &opts.ToolBoxFeatureDataView{
					Show:  true,
					Title: "View Data",
					Lang:  []string{"Data View", "Exit", "refresh"},
				},
				Restore: nil,
			},
		}),
		charts.WithLegendOpts(opts.Legend{Show: true}),
	)
	percentiles := getPercentiles(rootTraces, durations)

	scatter.
		AddSeries("Successful Traces Latency", successItems, charts.WithItemStyleOpts(opts.ItemStyle{Color: "blue"})).
		AddSeries("Error Traces Latency", errorItems, charts.WithItemStyleOpts(opts.ItemStyle{Color: "red"})).
		AddSeries("Percentiles", []opts.ScatterData{}, charts.WithMarkLineNameXAxisItemOpts(
			opts.MarkLineNameXAxisItem{
				Name:  "Mean",
				XAxis: percentiles["Mean"],
			},
			opts.MarkLineNameXAxisItem{
				Name:  "Median",
				XAxis: percentiles["Median"],
			},
			opts.MarkLineNameXAxisItem{
				Name:  "90th",
				XAxis: percentiles["90th"],
			},
			opts.MarkLineNameXAxisItem{
				Name:  "99th",
				XAxis: percentiles["99th"],
			},
		),
			charts.WithItemStyleOpts(opts.ItemStyle{Color: "grey"}),
			charts.WithMarkLineStyleOpts(opts.MarkLineStyle{
				Symbol:     []string{"none", "none"},
				SymbolSize: 0,
				Label: &opts.Label{
					Show:      true,
					Color:     "grey",
					Formatter: "{b}",
				},
			}),
		)

	return scatter
}
