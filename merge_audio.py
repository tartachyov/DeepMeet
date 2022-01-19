import os
from pydub import AudioSegment
import glob
import sys

# # Grab the Audio files in "audio" folder
audiofiles = glob.glob(sys.argv[1]+"/phraseAudio/*.mp3")
# audiofiles.sort()
# print(audiofiles)

# Loopting each file and include in Audio Segment
afs = [AudioSegment.from_mp3(
    sys.argv[1]+"/phraseAudio/"+str(af)+".mp3") for af in range(len(audiofiles))]

combined = afs[0]

# Appending all the audio file
for af in afs[1:]:
    combined = combined.append(af)

# Export Merged Audio File
combined.export(sys.argv[1]+"/mergedAudio.mp3",
                format="mp3")
