import sys
import json
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import time
from pydub import AudioSegment

import collections
import contextlib
import sys
import wave
import webrtcvad


def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        # print(wf.getframerate())
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""

    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.
    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.
    Arguments:
    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])


def speed_change(audio, sound, speed, filename, i, clipDuration):
    if speed > 1.2:
        # Uncomment for silence removal
        beforeDuration = audio.duration
        # FIXME: 455.wav corrupted issue when reading .wav on Jose-09.01 probably too short < 1sec
        if beforeDuration >= 2:
            sound.export(
                filename+"wav/"+i+'.wav',
                format="wav",
                #   bitrate=16000
            )

            pcmSound, sample_rate = read_wave(filename+"wav/"+i+'.wav')
            # from 1 to 3 aggresiveness of silence removal
            vad = webrtcvad.Vad(3)
            frames = frame_generator(30, pcmSound, sample_rate)
            frames = list(frames)
            segments = vad_collector(sample_rate, 30, 300, vad, frames)
            # Segmenting the Voice pcmSound and save it in list as bytes
            concataudio = [segment for segment in segments]
            joinedaudio = b"".join(concataudio)
            write_wave(filename+"wav/"+i+'.wav', joinedaudio, sample_rate)

            audio = AudioFileClip(filename+"wav/"+i+'.wav')
            sound = AudioSegment.from_file(filename+"wav/"+i+'.wav')
            print("-> Silence removed ->",
                  filename+"wav/" + i+'.wav',
                  "{:.2f}".format(beforeDuration - audio.duration))

        speed = audio.duration/clipDuration
        # audio.close()
        if speed > 1.2:
            speed = 1.03

    # print("-> Changing rate ->", alternateAudioFileName +
    #       str(i), audio.duration, speed)
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    sound_with_altered_frame_rate.export(
        filename+"wav/"+i+'.wav', format="wav")


def annotate(alternateAudioFileName, useOriginalAudio, i, clip, txt, txt_color='yellow', fontsize=20, font='Arial-Bold'):
    """ Writes a text at the bottom of the clip. """
    # print("Annotate "+str(i))
    # if i == 125:
    #     print(alternateAudioFileName, useOriginalAudio, i, txt)

    txtclip = TextClip(txt, fontsize=fontsize,
                       font=font, color=txt_color, bg_color="black")

    # print("Annotate_text "+str(i))

    if useOriginalAudio == False:
        audio = AudioFileClip(alternateAudioFileName+str(i)+".mp3")
        if audio.duration > clip.duration:
            # print("Annotate_duration "+str(i))
            if clip.duration < 0:
                print("-> Clip duration is negative ->",
                      alternateAudioFileName+str(i)+".mp3", clip.duration)

            rate = audio.duration/clip.duration
            if rate < 0.9:
                # print("-> Too small rate ->", "{:.2f}".format(rate))
                rate = 0.97

            sound = AudioSegment.from_file(
                alternateAudioFileName+str(i)+".mp3")
            # print("-> Changing rate ->", alternateAudioFileName +
            #       str(i), audio.duration, rate)
            speed_change(audio,
                         sound, rate, alternateAudioFileName, str(i), clip.duration)

            # audio.close()
            audio = AudioFileClip(alternateAudioFileName+"wav/"+str(i)+".wav")
            if audio.duration > clip.duration and audio.duration-clip.duration > 0.2:
                print("-> Freezed frame ->", str(i))
            #     print("-> SUBCLIPPED ->", str(i),
            #           "{:.2f}".format(audio.duration),
            #           "{:.2f}".format(clip.duration),
            #           "{:.2f}".format(audio.duration-clip.duration),
            #           str("{:.2f}".format((audio.duration-clip.duration)/audio.duration*100)+"%"))
            #     audio = audio.subclip(0, clip.duration)

        # audio.set_duration(clip.duration)
        # print("Annotate_setDuration "+str(i))
        clip.set_duration(audio.duration)
        clip = clip.set_audio(audio)
        # audio.close()

    # print("Annotate_return "+str(i))
    cvc = CompositeVideoClip(
        [clip, txtclip.set_pos(('center', 'bottom'))])
    return cvc.set_duration(audio.duration)


def createVideo(originalClipName, subtitlesFileName, outputFileName, alternateAudioFileName, useOriginalAudio=True):

    clip = VideoFileClip(originalClipName)

    if useOriginalAudio == True:
        print(time.strftime("\t" + "%H:%M:%S", time.gmtime()),
              "Using original audio track...")

    # read in the subtitles files
    print("\t" + time.strftime("%H:%M:%S", time.gmtime()),
          "Reading subtitle file: " + subtitlesFileName)
    subs = SubtitlesClip(subtitlesFileName)  # , generator)
    print("\t\t==> Subtitles duration before: " + str(subs.duration))
    subs = subs.subclip(0, clip.duration - .001)
    subs.set_duration(clip.duration - .001)
    print("\t\t==> Subtitles duration after: " + str(subs.duration))
    print("\t" + time.strftime("%H:%M:%S", time.gmtime()),
          "Reading subtitle file complete: " + subtitlesFileName)

    print("\t" + time.strftime("%H:%M:%S", time.gmtime()),
          "Creating Subtitles Track...")
    # annotated_clips = [annotate(clip.subclip(from_t, to_t), txt)
    #                    for (from_t, to_t), txt in subs]
    i = 0
    annotated_clips = []
    for (from_t, to_t), txt in subs:
        annotated_clips.append(
            annotate(alternateAudioFileName, useOriginalAudio, i, clip.subclip(from_t, to_t), txt))
        # print("next")
        i += 1

    print("\t" + time.strftime("%H:%M:%S", time.gmtime()),
          "Creating composited video: " + outputFileName)
    # Overlay the text clip on the first video clip
    final = concatenate_videoclips(annotated_clips)

    print("\t" + time.strftime("%H:%M:%S", time.gmtime()),
          "Writing video file: " + outputFileName)
    final.write_videofile(outputFileName)


createVideo(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], False)
