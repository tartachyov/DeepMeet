import sys
from moviepy.editor import *

originalClipName = sys.argv[1]
audioTrackName = sys.argv[2]

# # To subclip video
#
clip = VideoFileClip(originalClipName)
audio = AudioFileClip(audioTrackName)
clip = clip.set_audio(audio)

clip.write_videofile(originalClipName+"_originalAudio.mp4")
