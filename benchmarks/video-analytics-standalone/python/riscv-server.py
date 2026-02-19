import os
import io
import grpc
import argparse
from concurrent import futures
import shutil
from cassandra.cluster import Cluster
from cassandra import DriverException
from PIL import Image
import torch
import torchvision.models as models
from torchvision import transforms
import cv2
import logging

from proto.video_analytics_standalone import video_analytics_standalone_pb2
import video_analytics_standalone_pb2_grpc

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="Server IP")
parser.add_argument("-p", "--port", dest="port", default="50051", help="Server port")
parser.add_argument("--default_video", default="default.mp4", help="Default video")
parser.add_argument("--num_frames", default=10, help="Number of frames")
parser.add_argument("--db_addr", default="database", help="Cassandra server IP")
args = parser.parse_args()
args.num_frames = int(args.num_frames)

CACHE_DIR = "./cached_videos"
if os.path.exists(CACHE_DIR):
    shutil.rmtree(CACHE_DIR)

os.makedirs(CACHE_DIR, exist_ok=True)

cluster = Cluster([args.db_addr], protocol_version=5,
    connect_timeout=60,
    control_connection_timeout=60,
    idle_heartbeat_interval=10
)

session = cluster.connect('video_db')

session.default_timeout = 60

model = models.squeezenet1_1(pretrained=True)
labels_fd = open('imagenet_labels.txt', 'r')
labels = []
for i in labels_fd:
    labels.append(i)
labels_fd.close()

def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    img_t = transform(image)
    return torch.unsqueeze(img_t, 0)

def infer(batch_t):
    model.eval()
    with torch.no_grad():
        out = model(batch_t)
    _, indices = torch.sort(out, descending=True)
    out = ""
    for idx in indices[0][:1]:
        out = out + labels[idx] + ","
    return out

def ObjectDetectionFunction(video_path):
    try:
        video = cv2.VideoCapture(video_path)
        classification = ""
        print(video.isOpened())

        for _ in range(args.num_frames):
            success, frame = video.read()
            if not success:
                break
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            batch = preprocess_image(image)
            classification += infer(batch) 
        video.release()
        return f"python.video_analytics_standalone.{video_path}.frames:{args.num_frames}.classification:{classification}"
        
    except Exception as e:
        return f"python.video_analytics_standalone.VideoAnalyticsFailed.Error:{e}"

def fetch_video_from_cassandra(video_name):
    cached_path = os.path.join(CACHE_DIR, video_name)
    if os.path.exists(cached_path):
        return cached_path
    # print(video_name)
    try:
        row = session.execute(
            "SELECT file_id FROM files WHERE filename = %s",
            (video_name,)
        ).one()
    except DriverException as e:
        print("Error fetching file_id:", e)
        return None

    file_id = row.file_id
    chunks = session.execute(
        "SELECT data FROM chunks WHERE file_id=%s ORDER BY chunk_index  ALLOW FILTERING", 
        (file_id,)
    )

    with open(cached_path, "wb") as f:
        for chunk in chunks:
            f.write(chunk.data)
    print("edw 1")
    return cached_path

class VideoAnalytics(video_analytics_standalone_pb2_grpc.VideoAnalyticsServicer):
    def ObjectDetection(self, request, context):
        video_name = request.name if request.name else args.default_video
        video_path = os.path.join(CACHE_DIR, video_name)
        # print(video_name, video_path)
        if not os.path.exists(video_path):
            result = fetch_video_from_cassandra(video_name)
            if not result:
                return video_analytics_standalone_pb2.GetResult(
                    message=f"Video not found in Cassandra: {video_name}"
                )
            video_path = result
        result_msg = ObjectDetectionFunction(video_path)
        return video_analytics_standalone_pb2.GetResult(
            message=f"fn: VideoAnalyticsStandalone | video: {video_name} | {result_msg}"
        )

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    video_analytics_standalone_pb2_grpc.add_VideoAnalyticsServicer_to_server(VideoAnalytics(), server)

    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    logging.info("Start VideoAnalyticsStandalone-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)    
    serve()
