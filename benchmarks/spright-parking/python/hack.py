#!/usr/bin/env python3

import subprocess
import logging

def replaceServiceAddr(filename, ingress):
    stream = open(filename, 'r')
    input_data = stream.read()
    stream.close()

    input_data = input_data.replace('INGRESS_IP:INGRESS_PORT', ingress)

    # Save it again
    stream = open(filename, 'w')
    stream.write(input_data)
    stream.close()

# ingressIP = subprocess.check_output("docker inspect parking-proxy -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ", shell=True).decode('UTF-8')
logging.basicConfig(level=logging.INFO)
ingressIP = subprocess.check_output("kubectl get po -l istio=ingressgateway -n istio-system -o jsonpath=\'{.items[0].status.hostIP}\'", shell=True).decode('UTF-8')
ingressPort = subprocess.check_output("kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name==\"http2\")].nodePort}'", shell=True).decode('UTF-8')
ingress = ingressIP + ':' + ingressPort

replaceServiceAddr('../cfg/default.conf', ingress)
replaceServiceAddr('../cfg/nginx.conf', ingress)
