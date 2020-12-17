# Subtitling

A simple script to generate subtitles from LinSTT transcriptions.

## Requirement
Ths script requires python3 any version.

## Usage

```bash
./create-sub.py transcription.json subtitles.srt
```

```
usage: create-sub.py [-h] [--speaker] [--trace] [--lang LANG] input output

create-sub convert LinSTT transcription output to srt or vtt subtitle format.

positional arguments:
  input        Input json transcription file.
  output       Ouput subtitle file. Must be either .srt or .vtt

optional arguments:
  -h, --help   show this help message and exit
  --speaker    Display speaker
  --trace      Display output
  --lang LANG  Set language (for VTT format only)

```

## LICENCE
This project is licensed under the GNU AFFERO License - see the [LICENSE.md](LICENSE.md) file for details.