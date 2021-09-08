# Video Analytics
![diagram](diagram.png)

This benchmark models a video analysis system, where image recognition is performed on the
individual frames from a video feed. Three functions are involved:
- The **Streaming** function retrieves a video fragment and sends it to the decoder.
- The **Decoder** splits video fragments into individual frames which are sent to the object
recognition function
- The **Object Recognition** function (a.k.a. `recog`) performs object recognition on an image.

The video streaming function is the interface function implementing the standard helloworld grpc
service. Upon invokation, it will send the video fragment to the driver which then sends
singular frames to the recogniser. The result of the object recognition is relayed back to the 
callee, and is displayed in order from most likely to least likely tag.

## Instances
Number of instances per function in a stable flow:
| Function | Instances | Is Configurable |
|----------|-----------|-----------------|
| Streaming | 1 | No |
| Decoder | 1 | No |
| Recog | 6 | Yes - Set in recog knative manifest and should be equal decoder `DecoderFrames`.


## Parameters

### Flags

- `addr` - The address of the Decoder
- `p` - The port used by the Decoder
- `sp` - The port to which the streaming function will listen (which is used for invokation)
- `d` - Debug toggle, enables extra logs
- `video` - The location of the video file, `reference/video.mp4` by default.
- `zipkin` - Address of the zipkin span collector

### Environment Variables

- `TRANSFER_TYPE` - The transfer type to use. Can be `INLINE` (default), `S3`, or `XDT`. Not
all benchmarks support all transfer types.
- `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_REGION` - Standard s3 keys, only needed if the s3
transfer type is used
- `ENABLE_TRACING` - Toggles tracing.
- `DecoderFrames` - Used to set the number of frames being sent and hence the number of object
recognition function instances that are used. 6 by default.
- `CONCURRENT_RECOG` - Used in the decoder to toggle if recog functions are called concurrently.