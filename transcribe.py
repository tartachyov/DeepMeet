import boto3
import uuid
import requests
import sys
import time

# Set up the Transcribe client
# boto3.setup_default_session(profile_name='deepmeet')
session = boto3.session.Session(
    profile_name='deepmeet',
    region_name='eu-central-1')
# transcribe = boto3.client('transcribe')
transcribe = session.client('transcribe')

# purpose: Function to format the input parameters and invoke the Transcribe service


def createTranscribeJob(bucket, mediaFile):

    # Set up the full uri for the bucket and media file
    mediaUri = "https://" + bucket + ".s3.eu-central-1" + \
        ".amazonaws.com/" + mediaFile

    print("Creating Job: " + "transcribe " + mediaFile + " for " + mediaUri)

    # Use the uuid functionality to generate a unique job name.  Otherwise, the Transcribe service will return an error
    response = transcribe.start_transcription_job(
        TranscriptionJobName="transcribe_" + uuid.uuid4().hex + "_" + mediaFile,
        # FIXME: choose language from env
        LanguageCode="ru-RU",
        MediaFormat="mp4",
        Media={
            "MediaFileUri": mediaUri
        },
        Settings={
            "ShowSpeakerLabels": True,
            "MaxSpeakerLabels": 2
            #   "VocabularyName": "MyVocabulary"
        })

    # return the response structure found in the Transcribe Documentation
    return response


# purpose: simply return the job status
def getTranscriptionJobStatus(jobName):
    response = transcribe.get_transcription_job(TranscriptionJobName=jobName)
    return response

# purpose: get and return the transcript structure given the provided uri


def getTranscript(transcriptURI):
    # Get the resulting Transcription Job and store the JSON response in transcript
    result = requests.get(transcriptURI)

    return result.text


# Create Transcription Job
response = createTranscribeJob(sys.argv[1], sys.argv[2])

# loop until the job successfully completes
print("\n==> Transcription Job: " +
      response["TranscriptionJob"]["TranscriptionJobName"] + "\n\tIn Progress"),

# # For the fucked up scenario manual response from previous run
# response = {}
# response['TranscriptionJob'] = {
#     "TranscriptionJobStatus": "IN_PROGRESS",
#     "TranscriptionJobName": "transcribe_5ec41199b45a40aba245084b57c34d95_08.01-Aritz.mp3"
# }

while(response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS"):
    print("-> ", response),
    time.sleep(300)
    response = getTranscriptionJobStatus(
        response["TranscriptionJob"]["TranscriptionJobName"])

print("\nJob Complete")
print("\tStart Time: " + str(response["TranscriptionJob"]["CreationTime"]))
print("\tEnd Time: " + str(response["TranscriptionJob"]["CompletionTime"]))
print("\tTranscript URI: " +
      str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]))

# Now get the transcript JSON from AWS Transcribe
transcript = getTranscript(
    str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]))

# print( "\n==> Transcript: \n" + transcript)

# Opening a file
# sys.argv[2].split("/")[0]+"/"+
transcriptFile = open(response["TranscriptionJob"]
                      ["TranscriptionJobName"]+'.json', 'w')

# Writing a string to file
transcriptFile.write(transcript)
