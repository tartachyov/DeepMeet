import boto3
import json
import sys

session = boto3.session.Session(
    profile_name='deepmeet',
    region_name='eu-central-1')
translate = session.client(service_name='translate',
                           region_name=sys.argv[2], use_ssl=True)


def translateTranscript(transcript, sourceLangCode, targetLangCode):
    # Get the translation in the target language.  We want to do this first so that the translation is in the full context
    # of what is said vs. 1 phrase at a time.  This really matters in some lanaguages

    # stringify the transcript
    ts = json.loads(transcript)

    # pull out the transcript text and put it in the txt variable
    txt = ts["results"]["transcripts"][0]["transcript"]

    txtParts = txt.split(".")

    translation = " "

    for txtPart in txtParts:
        if len(txtPart) > 0 and len(txtPart.encode("utf8")) < 5000:
            # call Translate  with the text, source language code, and target language code.  The result is a JSON structure containing the
            # translated text
            translationPart = translate.translate_text(
                Text=txtPart, SourceLanguageCode=sourceLangCode, TargetLanguageCode=targetLangCode)
            # print(translationPart)
            translation += translationPart["TranslatedText"] + ". "
        else:
            print(len(txtPart.encode("utf8")), txtPart)
            translation += txtPart

    return translation


# Opening a file
with open(sys.argv[1], 'r') as myfile:
    data = myfile.read()

translation = translateTranscript(data, "es", "en")

# Opening a file
translationFile = open(sys.argv[1]+'_translate.txt', 'w')

# Writing a string to file
translationFile.write(translation)
