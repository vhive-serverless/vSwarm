import os
import sys

import tracing
import cv2

from pymongo import MongoClient
import gridfs

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']

# if LAMBDA is set, then ignore

if not LAMBDA:
    import grpc
    import argparse

    from proto.video_processing import video_processing_pb2
    import video_processing_pb2_grpc

    from concurrent import futures 

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
    parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
    parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
    parser.add_argument("--default_video", default="default.mp4", help="Default video to be converted to grayscale if empty")
    parser.add_argument("--num_frames", default=5, help="Number of frames to be considered")
    parser.add_argument("--db_addr", default="mongodb://video-processing-database:27017", help="Address of the data-base server")

    args = parser.parse_args()
    args.num_frames = int(args.num_frames)

db_name = "video_db"
client = MongoClient(args.db_addr)
db = client[db_name]

if tracing.IsTracingEnabled():
    tracing.initTracer("video-processing-python", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()


def ConvertToGrayscaleFunction(video_path, output_video_path):
    try:
        video = cv2.VideoCapture(video_path)

        width = int(video.get(3))
        height = int(video.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        result_video = cv2.VideoWriter(output_video_path, fourcc, 20.0, (width, height))

        for _ in range(args.num_frames):
            success, frame = video.read()
            if not success: break
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            result_video.write(gray_frame)

        video.release()
        result_video.release()
        return f"python.video_processing.{video_path}"
    except Exception as e:
        return f"python.video_processing.VideoProcessingFailed.Error:{e}"

if not LAMBDA:
    class VideoProcessing(video_processing_pb2_grpc.VideoProcessingServicer):
        def ConvertToGrayscale(self, request, context):
            
            if request.name == "":
                video_name = f"{args.default_video}"
                output_video_name = f"output-{args.default_video}"
            else:
                video_name = f"{request.name}"
                output_video_name = f"output-{request.name}"
            
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
                        msg = f"fn: VideoProcessing | video: {video_name} | Error: VideoNotFound in GridFS | runtime: Python"
                        return video_processing_pb2.GetGrayscaleVideo(message=msg)
                except Exception as e:
                    msg = f"fn: VideoProcessing | video: {video_name} | Error: {e} | runtime: Python"
                    return video_processing_pb2.GetGrayscaleVideo(message=msg)

            with tracing.Span("Video Processing"):
                return_msg = ConvertToGrayscaleFunction(video_name, output_video_name)
            msg = f"fn: VideoProcessing | video: {video_name} | return msg: {return_msg} | runtime: Python"
            return video_processing_pb2.GetGrayscaleVideo(message=msg)
                
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    video_processing_pb2_grpc.add_VideoProcessingServicer_to_server(VideoProcessing(), server)
    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    print("Start VideoProcessing-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
