import sys
from moviepy.editor import *

originalClipName = sys.argv[1]
# fromTime = sys.argv[2]

# # To subclip video
#
clip = VideoFileClip(originalClipName)
# clip.subclip(int(fromTime), clip.duration)
# clip.set_duration(clip.duration-int(fromTime))

clip.write_videofile(originalClipName+".mp4")

# # To separate audio:
#
# audioOnly = clip.audio
# # audioOnly.set_duration(clip.duration-int(fromTime))
# audioOnly.write_audiofile(originalClipName+"_subclip.mp3")

# # To subclip audio
#
# audioOnly = AudioFileClip(originalClipName)
# audioOnly.subclip(int(fromTime), audioOnly.duration)
# # audioOnly.set_duration(audioOnly.duration-int(fromTime))
# audioOnly.write_audiofile(originalClipName+"_subclip.mp3")
