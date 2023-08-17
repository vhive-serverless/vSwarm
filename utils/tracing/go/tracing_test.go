package tracing

import (
	"context"
	"log"
	"os"
	"os/exec"
	"testing"
	"time"

	"github.com/sirupsen/logrus"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
)

func TestMain(m *testing.M) {
	cmd := exec.Command("docker", "pull", "openzipkin/zipkin")
	_, err := cmd.CombinedOutput()
	if err != nil {
		log.Fatalf("Could not create custom tracer: %v", err)
	}
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Start(); err != nil {
		logrus.Print(err)
	}

	cmd = exec.Command("docker", "run", "-d", "--name", "zipkin-test", "-p", "9411:9411", "openzipkin/zipkin")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		logrus.Print(err)
	}
	time.Sleep(30 * time.Second)

	m.Run()

	cmd = exec.Command("docker", "rm", "-f", "zipkin-test")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Start(); err != nil {
		logrus.Print(err)
	}

	os.Exit(0)
}

func TestInitBasicTracer(t *testing.T) {
	_, err := InitBasicTracer("http://localhost:9411/api/v2/spans", "test-tracer")
	if err != nil {
		log.Fatalf("Could not create basic tracer: %v", err)
	}
	tracer := otel.GetTracerProvider().Tracer("test-tracer")
	_, traceSpan := tracer.Start(context.Background(), "test-span")
	traceSpan.End()
}

func TestInitCustomTracer(t *testing.T) {
	logger := log.New(os.Stderr, "tracer-log", log.Ldate|log.Ltime|log.Llongfile)
	_, err := InitCustomTracer("http://localhost:9411/api/v2/spans", 1.0, logger, attribute.String("service.name", "custom tracer"))
	if err != nil {
		log.Fatalf("Could not create custom tracer: %v", err)
	}
	tracer := otel.GetTracerProvider().Tracer("test-tracer")
	_, traceSpan := tracer.Start(context.Background(), "test-span")
	traceSpan.End()
}

func TestInitCustomTracerWithSampling(t *testing.T) {
	logger := log.New(os.Stderr, "tracer-log", log.Ldate|log.Ltime|log.Llongfile)
	_, err := InitCustomTracer("http://localhost:9411/api/v2/spans", 0.1, logger, attribute.String("service.name", "custom tracer"))
	if err != nil {
		log.Fatalf("Could not create custom tracer with sampling: %v", err)
	}
	tracer := otel.GetTracerProvider().Tracer("test-tracer")
	_, traceSpan := tracer.Start(context.Background(), "test-span")
	traceSpan.End()
}

func TestSpan(t *testing.T) {
	_, err := InitBasicTracer("http://localhost:9411/api/v2/spans", "test-tracer")
	if err != nil {
		log.Fatalf("Could not create basic tracer: %v", err)
	}
	span := Span{SpanName: "test-span", TracerName: "test-tracer"}
	span.StartSpan(context.Background())
	time.Sleep(1 * time.Second)
	span.EndSpan()
}
