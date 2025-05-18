#!/usr/bin/env python3

from sys import *
from gtts import gTTS

def printUsageAndExit():
    print(argv[0],"seq out_mp3",file=stderr)
    exit(1)

if __name__=='__main__':
    try:
        seq,out_mp3=arg[1:]
    except:
        printUsageAndExit()

    textToSpeak=""

    for s in seq:
        textToSpeak+=s+". "

    tts=gTTS(textToSpeak,lang='en')
    tts.save(out_mp3)



