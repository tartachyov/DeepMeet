import sys
import json


def getPhrasesFromTranscript(transcript):

    # This function is intended to be called with the JSON structure output from the Transcribe service.  However,
    # if you only have the translation of the transcript, then you should call getPhrasesFromTranslation instead

    # Now create phrases from the translation
    ts = json.loads(transcript)
    items = ts['results']['items']

    # set up some variables for the first pass
    phrase = {
        "words": [],
    }  # newPhrase()
    phrases = []
    nPhrase = True
    x = 0
    c = 0

    print("==> Creating phrases from transcript...")

    for item in items:

        # if it is a new phrase, then get the start_time of the first item
        if nPhrase == True:
            if item["type"] == "pronunciation":
                phrase["start_time"] = getTimeCode(float(item["start_time"]))
                nPhrase = False
            c += 1
        else:
            # We need to determine if this pronunciation or puncuation here
            # Punctuation doesn't contain timing information, so we'll want
            # to set the end_time to whatever the last word in the phrase is.
            # Since we are reading through each word sequentially, we'll set
            # the end_time if it is a word
            if item["type"] == "pronunciation":
                phrase["end_time"] = getTimeCode(float(item["end_time"]))

        # in either case, append the word to the phrase...
        phrase["words"].append(item['alternatives'][0]["content"])
        x += 1

        # now add the phrase to the phrases, generate a new phrase, etc.
        if x == 10:
            # print c, phrase
            phrases.append(phrase)
            phrase = {
                "words": [],
            }  # newPhrase()
            nPhrase = True
            x = 0

    return phrases


def getTimeCode(seconds):
    # Format and return a string that contains the converted number of seconds into SRT format

    thund = int(seconds % 1 * 1000)
    tseconds = int(seconds)
    tsecs = ((float(tseconds) / 60) % 1) * 60
    tmins = int(tseconds / 60)
    return str("%02d:%02d:%02d,%03d" % (00, tmins, int(tsecs), thund))


def generateString(subtitles):
    completeString = ""
    i = 1
    for line in subtitles:
        completeString += str(i)+"\n"
        completeString += line["start_time"]+" --> "+line["end_time"]+"\n"
        completeString += ' '.join(line["words"])+"\n\n"
        i += 1

    return completeString


# Opening a file
with open(sys.argv[1], 'r') as myfile:
    data = myfile.read()

subtitles = getPhrasesFromTranscript(data)
# print(subtitles)

completeString = generateString(subtitles)

# Opening a file
subtitlesFile = open(sys.argv[1]+'_subtitles.srt', 'w')

# Writing a string to file
subtitlesFile.write(completeString)
