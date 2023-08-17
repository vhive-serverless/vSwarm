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
	"fmt"
	"sort"

	log "github.com/sirupsen/logrus"

	"github.com/go-echarts/go-echarts/v2/charts"
	"github.com/go-echarts/go-echarts/v2/opts"
	"github.com/gonum/stat"
)

func ParseTraces(traces []Trace, latencyType string) ([]*Trace, []float64) {

	m := make(map[string]*Trace)

	for i := range traces {
		m[traces[i].ID] = &traces[i]
	}

	for i := range traces {
		if m[traces[i].ParentID] != nil {
			m[traces[i].ParentID].Child = append(m[traces[i].ParentID].Child, &traces[i])
		}
	}

	parsedTraces := []*Trace{}
	for _, trace := range m {
		if m[trace.ParentID] == nil {
			deepestLeaf, _ := trace.DeepestLeaf()
			trace.SystemDuration = trace.Duration - deepestLeaf.Duration

			parsedTraces = append(parsedTraces, trace)
		}
	}

	switch latencyType {
	case "e2e":
		sort.Slice(parsedTraces, func(i, j int) bool {
			return parsedTraces[i].Duration < parsedTraces[j].Duration
		})
	case "system":
		sort.Slice(parsedTraces, func(i, j int) bool {
			return parsedTraces[i].SystemDuration < parsedTraces[j].SystemDuration
		})
	}

	durations := make([]float64, len(parsedTraces))
	for i, trace := range parsedTraces {
		switch latencyType {
		case "e2e":
			durations[i] = float64(trace.Duration)
		case "system":
			if float64(trace.SystemDuration) > 0 {
				durations[i] = float64(trace.SystemDuration)
			} else {
				durations[i] = 1e-12 // avoid 0 or negative value
			}
		}
	}
	return parsedTraces, durations
}

func getPercentiles(durations []float64) map[string]float64 {
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

func PlotGraph(traces []*Trace, durations []float64, zipkinURL string, latencyType string) *charts.Scatter {
	successItems := make([]opts.ScatterData, 0)
	errorItems := make([]opts.ScatterData, 0)
	for i, trace := range traces {
		resp, err := trace.GetHTTPStatusCode()
		if err != nil || resp > 300 {
			errorItems = append(errorItems, opts.ScatterData{
				Name:         trace.TraceID,
				Value:        []interface{}{durations[i], stat.CDF(float64(durations[i]), stat.Empirical, durations, nil)},
				Symbol:       "roundRect",
				SymbolSize:   10,
				SymbolRotate: 0,
			})
		} else {
			successItems = append(successItems, opts.ScatterData{
				Name:         trace.TraceID,
				Value:        []interface{}{durations[i], stat.CDF(float64(durations[i]), stat.Empirical, durations, nil)},
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
	scatter.PageTitle = latencyType + " traces"

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
	percentiles := getPercentiles(durations)

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
