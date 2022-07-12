package models

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

	Child []*Trace
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

type Shards struct {
	Total      int64 `json:"total"`
	Successful int64 `json:"successful"`
	Skipped    int64 `json:"skipped"`
	Failed     int64 `json:"failed"`
}
