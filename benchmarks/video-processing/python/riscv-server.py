import os
import sys

# import tracing
import cv2
import shutil

# from pymongo import MongoClient
# import gridfs
from cassandra.cluster import Cluster
import logging

from cassandra import DriverException

import grpc
import argparse

from proto.video_processing import video_processing_pb2
import video_processing_pb2_grpc

from concurrent import futures 

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="Server IP")
parser.add_argument("-p", "--port", dest="port", default="50051", help="Server port")
parser.add_argument("--default_video", default="default.mp4", help="Default video")
parser.add_argument("--num_frames", default=50, help="Number of frames")
parser.add_argument("--db_addr", default="video-processing-database", help="Cassandra server IP")
args = parser.parse_args()
args.num_frames = int(args.num_frames)


CACHE_DIR = "./cached_videos"
if os.path.exists(CACHE_DIR):
    shutil.rmtree(CACHE_DIR)

os.makedirs(CACHE_DIR, exist_ok=True)

cluster = Cluster([args.db_addr]  ,  protocol_version=5,
    connect_timeout=60,
    control_connection_timeout=60,
    idle_heartbeat_interval=10
)

session = cluster.connect('video_processing_db')

session.default_timeout = 60




def ConvertToGrayscaleFunction(video_path, output_video_path):
    try:
        video = cv2.VideoCapture(video_path)

        width = int(video.get(3))
        height = int(video.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        result_video = cv2.VideoWriter(output_video_path, fourcc, 20.0, (width, height))

        for _ in range(args.num_frames):
            success, frame = video.read()
            if not success: break
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            result_video.write(cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR))

        video.release()
        result_video.release()
        return f"python.video_processing.{video_path}"
    except Exception as e:
        return f"python.video_processing.VideoProcessingFailed.Error:{e}"


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


class VideoProcessing(video_processing_pb2_grpc.VideoProcessingServicer):
    def ConvertToGrayscale(self, request, context):
        video_name = request.name if request.name else args.default_video
        output_video_name = f"output-{video_name}"
        video_path = os.path.join(CACHE_DIR, video_name)            

        if not os.path.exists(video_path):
            result = fetch_video_from_cassandra(video_name)
            if not result:
                return video_analytics_standalone_pb2.GetResult(
                    message=f"Video not found in Cassandra: {video_name}"
                )
            video_path = result            
        # try:
        #     with open(video_name):
        #         pass
        # except FileNotFoundError:
        #     try:
        #         fs = gridfs.GridFS(db)
        #         video_file_data = fs.find_one({"filename": video_name})
        #         if video_file_data:
        #             with open(video_name, "wb") as file:
        #                 file.write(video_file_data.read())
        #         else:
        #             msg = f"fn: VideoProcessing | video: {video_name} | Error: VideoNotFound in GridFS | runtime: Python"
        #             return video_processing_pb2.GetGrayscaleVideo(message=msg)
        #     except Exception as e:
        #         msg = f"fn: VideoProcessing | video: {video_name} | Error: {e} | runtime: Python"
        #         return video_processing_pb2.GetGrayscaleVideo(message=msg)

        # with tracing.Span("Video Processing"):
        return_msg = ConvertToGrayscaleFunction(video_path, output_video_name)
        msg = f"fn: VideoProcessing | video: {video_name} | return msg: {return_msg} | runtime: Python"
        return video_processing_pb2.GetGrayscaleVideo(message=msg)
                
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    video_processing_pb2_grpc.add_VideoProcessingServicer_to_server(VideoProcessing(), server)
    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    logging.info("Start VideoProcessing-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()