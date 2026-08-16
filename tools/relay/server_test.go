package main

import "testing"

func TestReplyIndicatesFailure(t *testing.T) {
	tests := []struct {
		name  string
		reply string
		want  bool
	}{
		{name: "success", reply: "fn: VideoProcessing | return msg: success", want: false},
		{name: "explicit error", reply: "fn: VideoProcessing | Error: no space left", want: true},
		{name: "function failure", reply: "VideoProcessingFailed", want: true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := replyIndicatesFailure(test.reply); got != test.want {
				t.Fatalf("replyIndicatesFailure(%q) = %v, want %v", test.reply, got, test.want)
			}
		})
	}
}
