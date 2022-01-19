import sys
import json
import boto3
import os
import binascii

session = boto3.session.Session(
    profile_name='deepmeet',
    region_name='eu-central-1')
translate = session.client(service_name='translate',
                           region_name='eu-central-1', use_ssl=True)


def getPhrasesFromTranscript(transcript):

    ts = json.loads(transcript)
    items = ts['results']['items']
    all_sp_items = []

    if ts["results"].__contains__("speaker_labels"):
        for segment in ts["results"]["speaker_labels"]["segments"]:
            for sp_item in segment["items"]:
                all_sp_items.append(sp_item)

    phrase = {
        "words": [],
    }
    translatePhrase = {
        "words": [],
    }
    subtitlesPhrases = []
    translatedPhrases = []
    dialoguePhrases = []
    nPhrase = True
    nTranslatePhrase = True
    x = 0
    n = 0
    startTime = 0
    endTime = 0
    totalTranslation = ""
    sp_index = 0
    false_speakers_count = 0

    print("==> Creating phrases from transcript...")

    for item in items:
        if item["type"] == "pronunciation":
            item["speaker"] = all_sp_items[sp_index]["speaker_label"]
            sp_index += 1

        # FIXME: append punctuation to previous string words item instead of separate item in words list
        phrase["words"].append(item['alternatives'][0]["content"])
        translatePhrase["words"].append(item['alternatives'][0]["content"])
        x += 1

        if nPhrase == True:
            if item["type"] == "pronunciation":
                phrase["start_time"] = getTimeCode(float(item["start_time"]))
                nPhrase = False
        else:
            if item["type"] == "pronunciation":
                phrase["end_time"] = getTimeCode(float(item["end_time"]))

        if nTranslatePhrase == True:
            if item["type"] == "pronunciation":
                speakerInd = item["speaker"]
                translatePhrase["start_time"] = getTimeCode(
                    float(item["start_time"]))
                startTime = float(item["start_time"])
                translatePhrase["end_time"] = getTimeCode(
                    float(item["end_time"]))
                endTime = float(item["end_time"])
                if endTime < startTime:
                    print("-> Ended earlier by item duration ->", x, n,
                          startTime, endTime)
                nTranslatePhrase = False

                # if n == 202:
                #     print("-> 202_0 ->",
                #           startTime,
                #           endTime,
                #           translatePhrase["start_time"],
                #           translatePhrase["end_time"],
                #           item["start_time"],
                #           item["end_time"])
        else:
            if item["type"] == "pronunciation":
                if speakerInd != item["speaker"]:
                    false_speakers_count += 1

                translatePhrase["end_time"] = getTimeCode(
                    float(item["end_time"]))
                endTime = float(item["end_time"])
                if endTime < startTime:
                    print("-> Ended earlier by item duration ->", x, n,
                          startTime, endTime)

                # if n == 201 or n == 197:
                #     print("-> 198_202 ->",
                #           startTime,
                #           endTime,
                #           translatePhrase["start_time"],
                #           translatePhrase["end_time"],
                #           item["start_time"],
                #           item["end_time"])
            else:
                if item["type"] == "punctuation":
                    txtPart = ' '.join(translatePhrase["words"])
                    if len(txtPart) > 0 and len(txtPart.encode("utf8")) < 5000:
                        # call Translate  with the text, source language code, and target language code.  The result is a JSON structure containing the
                        # translated text
                        translationPart = translate.translate_text(
                            Text=txtPart, SourceLanguageCode="es", TargetLanguageCode="en")
                        # print(translationPart)
                        translation = translationPart["TranslatedText"]
                    else:
                        print(len(txtPart.encode("utf8")), txtPart)
                        translation = txtPart

                    totalTranslation += " "+translation
                    if len(translation) > 60:
                        partsQty = int(len(translation) / 30)
                        translationWords = translation.split(" ")
                        wordPartsQty = int(len(translationWords)/partsQty)
                        # print(len(translation), partsQty, len(translationWords),
                        #       wordPartsQty, startTime, endTime)
                        for part in range(partsQty):
                            # print(part)
                            translatePhrasePart = {}
                            if part == 0:
                                translatePhrasePart["orig"] = ' '.join(
                                    translatePhrase["words"])

                            translatePhrasePart["speaker"] = speakerInd
                            startTimePart = float(startTime +
                                                  (endTime-startTime)/partsQty*part)
                            translatePhrasePart["start_time"] = getTimeCode(
                                startTimePart)
                            endTimePart = float(startTime +
                                                (endTime-startTime)/partsQty*(part+1))
                            if endTimePart < startTimePart:
                                print("-> Ended earlier than started ->", startTimePart, endTimePart, startTime, endTime,
                                      part, translation, partsQty, len(translationWords), wordPartsQty, x, n)

                            translatePhrasePart["end_time"] = getTimeCode(
                                endTimePart)
                            fromIndex = part*wordPartsQty
                            tillIndex = (part+1)*wordPartsQty

                            if part == partsQty-1:
                                # print("-> Last part of translation ->", part, partsQty, tillIndex, len(translationWords), translationWords, translationWords[slice(
                                #     fromIndex, len(translationWords))])
                                tillIndex = len(translationWords)

                            # if n == 200 or n == 198:
                            #     print("-> 199_201 ->", part, partsQty,
                            #           startTimePart,
                            #           startTime,
                            #           endTime,
                            #           translatePhrasePart["start_time"],
                            #           endTimePart,
                            #           translatePhrasePart["end_time"])

                            translatePhrasePart["translation"] = ' '.join(translationWords[slice(
                                fromIndex, tillIndex)])
                            translatePhrasePart["id"] = n
                            n += 1
                            # binascii.b2a_hex(
                            #     os.urandom(6))
                            translatedPhrases.append(translatePhrasePart)
                    else:
                        translatePhrase["translation"] = translation
                        translatePhrase["id"] = n
                        n += 1
                        # binascii.b2a_hex(os.urandom(6))
                        translatePhrase["orig"] = ' '.join(
                            translatePhrase["words"])
                        dialoguePhrases.append({
                            "speaker": speakerInd,
                            "phrase": (' '.join(
                                translatePhrase["words"])).replace(" ,", ", ").replace(
                                " .", ". ").replace(" ?", "? ").replace("  ", " "),
                            "start_time": translatePhrase["start_time"]
                        })
                        translatePhrase.pop("words")
                        translatePhrase["speaker"] = speakerInd
                        translatedPhrases.append(translatePhrase)

                    translatePhrase = {
                        "words": [],
                    }
                    nTranslatePhrase = True

        if x == 10:
            subtitlesPhrases.append(phrase)
            phrase = {
                "words": [],
            }
            nPhrase = True
            x = 0

    print("Total false speaker words count: "+str(false_speakers_count))

    return subtitlesPhrases, translatedPhrases, totalTranslation, dialoguePhrases


def getTimeCode(seconds):
    # Format and return a string that contains the converted number of seconds into SRT format

    thund = int(seconds % 1 * 1000)
    tseconds = int(seconds)
    tsecs = ((float(tseconds) / 60) % 1) * 60
    tmins = int(tseconds / 60)
    # if int(round(tsecs)) != int(tsecs):
    #     print(tsecs, round(tsecs), int(tsecs), int(round(tsecs)))

    return str("%02d:%02d:%02d,%03d" % (00, tmins, int(round(tsecs)), thund))


def generateString(subtitles):
    completeString = ""
    i = 1
    for line in subtitles:
        completeString += str(i)+"\n"
        completeString += line["start_time"]+" --> "+line["end_time"]+"\n"
        if "words" in line:
            completeString += ' '.join(line["words"])+"\n\n"
        else:
            completeString += line["translation"]+"\n\n"
        i += 1

    return completeString


def generateDialogueString(subtitles):
    completeString = ""
    for ind, line in enumerate(subtitles):

        if "phrase" in line:
            phrase = line["phrase"]
        else:
            phrase = line["translation"]

        if ind > 0 and line["speaker"] == subtitles[ind-1]["speaker"]:
            completeString += phrase+" "
        else:
            completeString += "\n\n"+"speaker_" + \
                str(line["speaker"])+" "+line["start_time"] + \
                "\n"+phrase

    return completeString


# Opening a file
with open(sys.argv[1], 'r') as myfile:
    data = myfile.read()

subtitles, translatedSubtitles, totalTranslation, dialoguePhrases = getPhrasesFromTranscript(
    data)
# print(translatedSubtitles)

completeString = generateString(subtitles)
translatedCompleteString = generateString(translatedSubtitles)
dialogueString = generateDialogueString(dialoguePhrases)
translatedDialogueString = generateDialogueString(translatedSubtitles)

# Opening a file
subtitlesFile = open(sys.argv[1].split("/")[0]+'/subtitles.srt', 'w')
translatedSubtitlesFile = open(sys.argv[1].split(
    "/")[0]+'/subtitles_translated.srt', 'w')
dialogueFile = open(sys.argv[1].split("/")[0]+'/dialogue.txt', 'w')
translatedDialogueFile = open(sys.argv[1].split(
    "/")[0]+'/translatedDialogue.txt', 'w')
# translatedPhrasesFile = open(sys.argv[1].split(
#     "/")[0]+'/phrases_translated.json', 'w')

# Writing a string to file
subtitlesFile.write(completeString)
translatedSubtitlesFile.write(translatedCompleteString)
dialogueFile.write(dialogueString)
translatedDialogueFile.write(translatedDialogueString)
translatedOutput = {
    "result": totalTranslation,
    "parts": translatedSubtitles,
}
# translatedPhrasesFile.write(json.dumps(translatedOutput))

with open(sys.argv[1].split(
        "/")[0]+'/phrases_translated.json', "w") as outfile:
    json.dump(translatedOutput, outfile)
