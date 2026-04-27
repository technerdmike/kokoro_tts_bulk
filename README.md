# kokoro_tts_bulk

## Requirements
* FFMPEG
* Espeak-NG
* Python 3.11.9

## Additional notes
Added a feature to add pauses using the tag \[\[s=300\]\]. The number is the value for the milliseconds to pause. An issue with this pause is that the previous word should end with a punctuation, else it will be cut off. 

The script needs to run once with internet to download the model. Afterwards, it does not require internet connection. 