from pydub import AudioSegment

wav_audio = AudioSegment.from_file(
    "audio.m4a", format="m4a")
# raw_audio = AudioSegment.from_file("audio.wav", format="raw",
#                                    frame_rate=44100, channels=2, sample_width=2)

wav_audio.export("audio.mp3", format="mp3")
