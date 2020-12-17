#!/usr/bin/env python3

import argparse
import json
import time

clean_dict = {
    ord('.') : None,
    ord(',') : None,
    ord(':') : None,
    ord(';') : None,
    ord('!') : None,
    ord('?') : None,
}

end_chars = ['.', '?', '!', ';']

class SubItem:
    def __init__(self, speaker: str,
                       start: str, 
                       stop: str, 
                       text: str):
        self.speaker = speaker
        self.start = start
        self.stop = stop
        self.text = text        

    def toSRT(self, index: int,
                    max_char_line: int = 40,
                    display_spk: bool = False) -> str:
        output = "{}\n{} --> {}\n".format(index, 
                            self.timeStampSRT(self.start),
                            self.timeStampSRT(self.stop))
        
        if display_spk:
            output += "{}: ".format(self.speaker)

        for line in self.splitStr():
            output += "{}\n".format(line)
        return output + "\n"

    def toVTT(self) -> str:
        output = "{} --> {}\n".format(self.timeStampVTT(self.start),
                                      self.timeStampVTT(self.stop))
        
        output += "<v {}>{}\n\n".format(self.speaker, self.text)
        return output

    def splitStr(self, char_line: int = 40):
        """ Limit the number of character on a line. Split when needed"""
        output = []
        words = self.text.split(" ")
        current_line = ""
        for word in words:
            if len(current_line) + len(word) > char_line:
                output.append(current_line.strip())
                current_line = ""
            current_line += "{} ".format(word)
        output.append(current_line.strip())

        return output


    def timeStampSRT(self, t_str) -> str:
        """ Format second string format to hh:mm:ss,ms SRT format """
        t = float(t_str)
        ms = t % 1
        timeStamp = time.strftime('%H:%M:%S,', time.gmtime(t))
        return "{}{:03d}".format(timeStamp, int(ms*1000))

    def timeStampVTT(self, t_str) -> str:
        """ Format second string format to hh:mm:ss,ms SRT format """
        t = float(t_str)
        ms = t % 1
        t = int(t)
        s = t % 60
        t -= s
        m = t // 60
        return "{:02d}:{:02d}.{:03d}".format(m, s, int(ms*1000))


def extract_segments_format_1(word_list: dict, punctuation_output: str, speaker : str = None) -> list:
    subItems = []
    sentenceItems = []
    start_time = None
    new_sentence = True
    word_index = 0

    # remove <unk>
    word_list = [w for w in word_list if w["word"] != "<unk>"]
    word_list.sort(key=lambda x: x["start"])

    for word in punctuation_output.replace("'", "' ").split(): #Split concatenated word
        if new_sentence:
            sentenceItems = []
        sentenceItems.append(word)
        base_word = word.lower().translate(clean_dict)

        if word_list[word_index]["word"] == base_word:
            if new_sentence:
                start_time = word_list[word_index]["start"]
                new_sentence = False
            word_index += 1
        else:
            print("Error: expected to find {} but found {}".format(base_word, word_list[word_index]["word"]))
            exit(-1)
        
        for end_char in end_chars:
            if end_char in word:
                subItems.append(SubItem(speaker, start_time, word_list[word_index - 1]["end"], " ".join(sentenceItems).replace("' ", "'")))
                new_sentence = True
                break
        if len(sentenceItems) > 15:
            subItems.append(SubItem(speaker, start_time, word_list[word_index - 1]["end"], " ".join(sentenceItems).replace("' ", "'")))
            new_sentence = True
    return subItems

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='create-sub convert LinSTT transcription output to srt or vtt subtitle format.')
    parser.add_argument('input', help="Input json transcription file.")
    parser.add_argument('output', help="Ouput subtitle file. Must be either .srt or .vtt    ")
    parser.add_argument('--speaker', help="Display speaker", action="store_true")
    parser.add_argument('--trace', help="Display output", action="store_true")
    parser.add_argument('--lang', default="en", help="Set language (for VTT format only)")
    
    args = parser.parse_args()

    # Output format
    target_format = args.output.split(".")[-1]

    if target_format not in ["srt", "vtt"]:
        print("Target output file must be .srt or .vtt")
        exit(-1)

    try:
        f = open(args.input, 'r')
    except Exception:
        print("Could not open file at {}".format(args.input))
        exit(-1)
    try:
        content = json.load(f)
        f.close()
    except Exception:
        print("Could not read file content: bad format")
        exit(-1)
    

    # Detect json format
    """
    Format :
    punctuation + words -> Format 1
    punctuation + speaker + words -> Format 2
    speaker + words + text -> Format 3 
    """

    speaker_data =  "speakers" in content.keys()
    punctuation_data = "punctuation" in content.keys()
    text_data = "text" in content.keys()
    words_data = "words" in content.keys()

    if punctuation_data and words_data:
        #format 1
        items = extract_segments_format_1(content["words"], content["punctuation"])
    elif punctuation_data and speaker_data:
        #format 2
        items = extract_segments_format_1(content["speakers"][0]["words"], content["punctuation"], speaker=content["speakers"][0]['speaker_id'])
    elif text_data and speaker_data:
        print("Format not supported yet.")
        exit(-1)
    else:
        print("Unrecognized format.")
        exit(-1)

    try:
        f = open(args.output, 'w')
    except Exception:
        print("Could not open output file at {}".format(args.output))
        exit(-1)

    if target_format == "vtt":
        f.write("WEBVTT Kind: captions; Language: {}\n\n".format(args.lang))

    for i, item in enumerate(items):
        if target_format == "srt":
            to_write = item.toSRT(i + 1, display_spk=(speaker_data and args.speaker==True))
        else:
            to_write = item.toVTT()
        
        f.write(to_write)
        
        if args.trace:
            print(to_write)
    f.close()