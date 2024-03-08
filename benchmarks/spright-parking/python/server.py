import argparse
import datetime
import os
import threading
import requests, time, random
# protobuf
import parking_pb2
import parking_pb2_grpc
import grpc
from concurrent import futures

global stat_file 

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--nginxip', action='store', type=str, default='127.0.0.1')
    parser.add_argument('-p', '--nginxport', action='store', type=str, default='80')
    parser.add_argument('-I', '--istioip', action='store', type=str, default='127.0.0.1')
    parser.add_argument('-P', '--istioport', action='store', type=str, default='80')
    args = parser.parse_args()

    return args

def post(http_url, send_time):
    print("http_url: ", http_url)
    print("Send a request at {}".format(send_time)) # DEBUG

    files = {'file': open('image.jpeg', 'rb')}
    tmp_url = ''
    if random.random() < 0.9:
        tmp_url = http_url + '2/'
    else:
        tmp_url = http_url + '1/'
    r = requests.post(url = tmp_url, files=files)
    # DEBUG
    body_len = len(r.request.body if r.request.body else [])
    print(body_len)
    print(str(time.time()) + ";" + str(r.elapsed.total_seconds()))

    lock.acquire()
    stat_file.write(str(time.time()) + ";" + str(r.elapsed.total_seconds()) + "\n")
    lock.release()

def warm_up(fname):
    h = fname + '.default.example.com'
    print("Wake up " + h)
    r = requests.get(url = INGRESS_URL, headers = {"Host": h})
    print("Cold start + Processing delay = " + str(r.elapsed.total_seconds()))

def do_parking_call():
    stat_file = open('kn.parking_output.csv', 'w')
    
    args = get_args()
    URL = "http://" + args.nginxip + ":" + args.nginxport + "/"

    lock=threading.Lock()

    functions = ['detection-1', 'search-2', 'index-3', 'charging-4', 'persist-5']
    threads = []

    # for x in threads:
    #     x.join()

    max_run_time_sec = 600
    total_sec = 0
    st_1 = 220
    st_2 = 20
    try:
        while(1):
            print("Send snapshots at {}".format(total_sec))
            # Send request to function chain
            for i in range(0, 164):
                th = threading.Thread(target=post, args=(URL, total_sec))
                th.daemon = True
                th.start()
            time.sleep(st_1)
            print("Sleep for {}".format(st))
            total_sec = total_sec + st_1
            if total_sec >= max_run_time_sec:
                break
    except KeyboardInterrupt:
        stat_file.close()
        exit(1)
    stat_file.close()

class Parking(parking_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        if request.plaintext_message in ["", "world"]:
            plaintext = args.default_plaintext
            print(plaintext)
            do_parking_call()
        else:
            plaintext = request.plaintext_message
            print("else: ", plaintext)

        return parking_pb2.parkingReply(result="reply")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    parking_pb2_grpc.add_GreeterServicer_to_server(Parking(), server)
    
    # address = (args.addr + ":" + args.port) # TODO
    address = ("0.0.0.0:50051")
    server.add_insecure_port(address)
    print("Start Parking-python server. Addr: " + address)
    server.start()
    print("Parking-python server started and listening on " + address)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()