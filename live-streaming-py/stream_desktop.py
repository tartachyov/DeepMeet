import ffmpeg_streaming

video = ffmpeg_streaming.input('./video.mp4')

capture = ffmpeg_streaming.input('', capture=True)

_360p = ffmpeg_streaming.Representation(ffmpeg_streaming.Size(
    640, 360), ffmpeg_streaming.Bitrate(276 * 1024, 128 * 1024))

# dash = video.dash(ffmpeg_streaming.Formats.h264())
# dash.representations(_360p)
# dash.output('./dash.mpd')

hls = video.hls(ffmpeg_streaming.Formats.h264())
hls.representations(_360p)
hls.output('./hls.m3u8')
