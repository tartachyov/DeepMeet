# Import everything needed to edit video clips
from moviepy.editor import *

# Load .mp4 and select the subclip 00:00:50 - 00:00:60
clip = VideoFileClip("/.mp4").subclip(4, 68)

# Reduce the audio volume (volume x 0.8)
clip = clip.volumex(0.8)

# Generate a text clip. You can customize the font, color, etc.
txt_clip = TextClip("", fontsize=20, color='yellow')

# Say that you want it to appear 10s at the center of the screen
txt_clip = txt_clip.set_pos('center').set_duration(10)

# Overlay the text clip on the first video
video = CompositeVideoClip([clip, txt_clip])

# Write the result to a file (many options available !)
video.write_videofile("/short.mp4")
