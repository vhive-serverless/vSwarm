import os
import sys

import tracing

from torchvision import transforms
from PIL import Image
import torch
import torchvision.models as models
import cv2

from pymongo import MongoClient
import gridfs

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']

# if LAMBDA is set, then ignore

if not LAMBDA:
    import grpc
    import argparse

    from proto.video_analytics_standalone import video_analytics_standalone_pb2
    import video_analytics_standalone_pb2_grpc

    from concurrent import futures 

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
    parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
    parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
    parser.add_argument("--default_video", default="default.mp4", help="Default video to be object-detected")
    parser.add_argument("--num_frames", default=5, help="Number of frames to be considered")
    parser.add_argument("--db_addr", default="mongodb://video-analytics-standalone-database:27017", help="Address of the data-base server")

    args = parser.parse_args()
    args.num_frames = int(args.num_frames)

db_name = "video_db"
client = MongoClient(args.db_addr)
db = client[db_name]

# Load model
model = models.squeezenet1_1(pretrained=True)
labels_fd = open('imagenet_labels.txt', 'r')
labels = []
for i in labels_fd:
    labels.append(i)
labels_fd.close()


if tracing.IsTracingEnabled():
    tracing.initTracer("video-analytics-standalone-python", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()


def preprocessImage(image):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    img_t = transform(image)
    return torch.unsqueeze(img_t, 0)


def infer(batch_t):

    model.eval()
    with torch.no_grad():
        out = model(batch_t)
    _, indices = torch.sort(out, descending=True)
    # percentages = torch.nn.functional.softmax(out, dim=1)[0] * 100
    out = ""
    for idx in indices[0][:1]:
        out = out + labels[idx] + ","
    return out


def ObjectDetectionFunction(video_path):

    try:
        video = cv2.VideoCapture(video_path)
        classification = ""        
        for _ in range(args.num_frames):
            success, image = video.read()
            if not success: break
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            preprocessed_image = preprocessImage(image)
            classification += infer(preprocessed_image)
        video.release()
        return f"python.video_analytics_standalone.{video_path}.frames:{args.num_frames}.classification:{classification}"

    except Exception as e:
        return f"python.video_analytics_standalone.VideoAnalyticsFailed.Error:{e}"


if not LAMBDA:
    class VideoAnalytics(video_analytics_standalone_pb2_grpc.VideoAnalyticsServicer):
        def ObjectDetection(self, request, context):
            
            if request.name == "":
                video_name = f"videos/{args.default_video}"
            else:
                video_name = f"videos/{request.name}"
            
            try:
                with open(video_name):
                    pass
            except FileNotFoundError:
                try:
                    fs = gridfs.GridFS(db)
                    video_file_data = fs.find_one({"filename": video_name})
                    if video_file_data:
                        with open(video_name, "wb") as file:
                            file.write(video_file_data.read())
                    else:
                        msg = f"fn: VideoAnalyticsStandalone | video: {video_name} | Error: VideoNotFound in GridFS | runtime: Python"
                        return video_analytics_standalone_pb2.GetResult(message=msg)
                except Exception as e:
                    msg = f"fn: VideoAnalyticsStandalone | video: {video_name} | Error: {e} | runtime: Python"
                    return video_analytics_standalone_pb2.GetResult(message=msg)

            with tracing.Span("Video Analytics Standalone"):
                return_msg = ObjectDetectionFunction(video_name)
            msg = f"fn: VideoAnalyticsStandalone | video: {video_name} | return msg: {return_msg} | runtime: Python"
            return video_analytics_standalone_pb2.GetResult(message=msg)
                
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    video_analytics_standalone_pb2_grpc.add_VideoAnalyticsServicer_to_server(VideoAnalytics(), server)
    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    print("Start VideoAnalyticsStandalone-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
