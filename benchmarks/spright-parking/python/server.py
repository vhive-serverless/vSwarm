import argparse
import datetime
import os
import threading
import requests, time, random
# protobuf
import proto.parking.parking_pb2 as parking_pb2
import parking_pb2_grpc
import grpc
import logging
from concurrent import futures
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)



def post(http_url, send_time):
    logger.info("http_url: ", http_url)
    logger.info("Send a request at {}".format(send_time)) # DEBUG

    files = {'file': open('image.jpeg', 'rb')}
    tmp_url = ''
    function_chain = ''
    if random.random() < 0.9:
        tmp_url = http_url + '2/'
        function_chain = f"[detection, search, charging]"
        
    else:
        tmp_url = http_url + '1/'
        function_chain = f"[detection, search, index, persist, charging]"
    r = requests.post(url = tmp_url, files=files)
    result = ''
    if r.status_code != 200:
        result = f"Invoke function chain: {function_chain} fail!"
    else:
        
        result = f"Invoke function chain {function_chain} success!"
    return result


def do_parking_call(nginx_ip, nginx_port):
    
    url = f"http://{nginx_ip}:{nginx_port}/"

    total_sec = 0
    try:
        logger.info("Send snapshots at {}".format(total_sec))
        # Send request to function chain
        response = post(url, total_sec)
        return response

    except KeyboardInterrupt:
        exit(1)

class Parking(parking_pb2_grpc.ParkingServicer):
    def __init__(self,
                 nginx_ip,
                 nginx_port) -> None:
        super().__init__()
        self.nginx_ip = nginx_ip
        self.nginx_port = nginx_port
        
    def DoParking(self, request, context):
        logger.info(f"Receive request from relay, call do_parking")
        result = do_parking_call(nginx_ip, nginx_port)

        return parking_pb2.ParkingReply(result=result)

def serve(addr, port, nginx_ip, nginx_port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    parking_pb2_grpc.add_ParkingServicer_to_server(Parking(nginx_ip, nginx_port), server)
    
    address = f"{addr}:{port}"
    server.add_insecure_port(address)
    logger.info("Start Parking-python server. Addr: " + address)
    server.start()
    logger.info("Parking-python server started and listening on " + address)
    server.wait_for_termination()

if __name__ == "__main__":
    # Initialize the parser
    parser = argparse.ArgumentParser(description='python server that invokes spright-parking')

    # Add arguments
    parser.add_argument('--addr', type=str, help='Address to listen on', default='0.0.0.0')
    parser.add_argument('--port', type=int, help='Port to listen on', default=50051)
    parser.add_argument('--nginxip', type=str, help='Nginx IP address', default='parking-proxy')
    parser.add_argument('--ngixport', type=int, help='Nginx port', default=80)

    # Parse the arguments
    args = parser.parse_args()

    # Access the parsed arguments
    addr = args.addr
    port = args.port
    nginx_ip = args.nginxip
    nginx_port = args.ngixport
    serve(addr, port, nginx_ip, nginx_port)