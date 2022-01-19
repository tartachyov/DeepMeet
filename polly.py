import io
import sys
import json
import boto3
from moviepy.editor import *


def getTimeCode(seconds):
    # Format and return a string that contains the converted number of seconds into SRT format

    thund = int(seconds % 1 * 1000)
    tseconds = int(seconds)
    tsecs = ((float(tseconds) / 60) % 1) * 60
    tmins = int(tseconds / 60)
    return str("%02d:%02d:%02d,%03d" % (00, tmins, int(tsecs), thund))


# def getPhrasesFromTranslation(translation):

#     # Now create phrases from the translation
#     words = translation.split()

#     # set up some variables for the first pass
#     phrase = {
#         "words": [],
#     }
#     phrases = []
#     nPhrase = True
#     x = 0
#     c = 0
#     seconds = 0

#     print("==> Creating phrases from translation...")

#     for word in words:

#         # if it is a new phrase, then get the start_time of the first item
#         if nPhrase == True:
#             phrase["start_time"] = getTimeCode(seconds)
#             nPhrase = False
#             c += 1

#         # Append the word to the phrase...
#         phrase["words"].append(word)
#         x += 1

#         # now add the phrase to the phrases, generate a new phrase, etc.
#         if x == 10:

#             # For Translations, we now need to calculate the end time for the phrase
#             psecs = getSecondsFromPronunciation(
#                 ' '.join(phrase["words"]), "phraseAudio_" + str(c) + ".mp3")
#             seconds += psecs
#             phrase["end_time"] = getTimeCode(seconds)

#             phrases.append(phrase)
#             phrase = {
#                 "words": [],
#             }
#             nPhrase = True

#             x = 0

#     return  # phrases

# FIXME: order "Kendra" in the list
# US Joey Matthew** Joanna** Kendra | GB Brian Emma | AU Russel
voicesMap = ["Joey", "Matthew", "Brian", "Russell", "Kendra"]


def getVoice(ind):
    # print(ind, len(voicesMap))
    if ind < len(voicesMap):
        return voicesMap[ind]
    else:
        print("Voice is out of voicesMap range")
        return voicesMap[0]


def getSecondsFromPronunciation(textToSay, audioFileName, speaker=0):
    # Set up the Amazon Polly and Amazon Translate services
    session = boto3.session.Session(
        profile_name='deepmeet',
        region_name='eu-central-1')
    client = session.client('polly')

    # Use the translated text to create the synthesized speech
    voiceId = getVoice(speaker)
    response = client.synthesize_speech(
        OutputFormat="mp3",
        SampleRate="16000",  # 22050 -> 16000 for silence remover
        Text=textToSay,
        VoiceId=voiceId)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        print("\t==> Successfully called Polly for speech synthesis with voice: " + voiceId)
        writeAudioStream(response, audioFileName)
    else:
        print("\t==> Error calling Polly for speech synthesis")

    # Load the temporary audio clip into an AudioFileClip
    audio = AudioFileClip(audioFileName)

    # return the duration
    return  # audio.duration


def writeAudioStream(response, audioFileName):
    # Take the resulting stream and write it to an mp3 file
    if "AudioStream" in response:
        # print(response["AudioStream"])
        # with closing(response["AudioStream"]) as stream:
        output = audioFileName
        writeAudio(output, response["AudioStream"])


def writeAudio(output_file, stream):

    bytes = stream.read()

    print("\t==> Writing ", len(bytes), "bytes to audio file: ", output_file)
    try:
        # Open a file for writing the output as a binary stream
        with open(output_file, "wb") as file:
            file.write(bytes)

        if file.closed:
            print("\t==>", output_file, " is closed")
        else:
            print("\t==>", output_file, " is NOT closed")
    except IOError as error:
        # Could not write to file, exit gracefully
        print(error)
        sys.exit(-1)


# Opening a file
with open(sys.argv[1], 'r') as myfile:
    data = myfile.read()

phrases = json.loads(data)
phrases = phrases["parts"]
for phrase in phrases:
    speaker = 0
    if phrase.__contains__("speaker"):
        speaker = int(phrase["speaker"].split("_")[1])

    getSecondsFromPronunciation(phrase["translation"], sys.argv[1].split(
        "/")[0]+"/"+sys.argv[1].split(
        "/")[1]+"/phraseAudio/"+str(phrase["id"]) + ".mp3", speaker)

# phrases = getPhrasesFromTranslation(data)

# # Opening a file
# pollyFile = open(sys.argv[1]+'polly.jsonl', 'w')

# for phrase in phrases:
#     # Writing a string to file
#     pollyFile.write(str(phrase))
