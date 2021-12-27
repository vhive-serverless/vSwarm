.PHONY : proto clean build run coldstart image

image:
	docker build -t hyhe/trace-func-go .
	docker push hyhe/trace-func-go:latest

proto:
	protoc \
		--go_out=. \
		--go_opt=paths=source_relative \
		--go-grpc_out=. \
		--go-grpc_opt=paths=source_relative \
		server/faas.proto 
	/usr/bin/python3 -m grpc_tools.protoc -I=. \
		--python_out=. \
		--grpc_python_out=. \
		server/faas.proto

# make -i clean
clean: 
	kn service delete --all
	kubectl delete --all pods --namespace=default
	rm -f load
	rm -f *.log
	go mod tidy

build:
	go build cmd/load.go

# make ARGS="--rps X --duration X" run
run:
	go run cmd/load.go $(ARGS)

coldstart: clean run