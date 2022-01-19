Set of dirty scripts

`python convert_video.py videos/{filename}/{filename}.avi videos/{filename}/{filename}.mp3 `

`python transcribe.py "{bucket}" "{filename}.mp3"`

`python translate_subtitles.py videos/{filename}/{transcriptionResultFilename}.json`

`python polly.py videos/{filename}/phrases_translated.json`

`python merge_audio.py videos/{filename}`
