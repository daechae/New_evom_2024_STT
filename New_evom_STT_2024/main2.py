import requests, json
import time
from midiutil import MIDIFile
import os
from automation import daw_rendering_automation
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
API_URL = 'https://musia.kr/api/'


def download_melody(url, idx):
    with open("midis/" + str(idx) + "_melody.mid", "wb") as file:
        response = requests.get(url)
        file.write(response.content)

def make_chord(chord, idx):
    chord = json.loads(chord)

    track    = 0
    channel  = 0
    time     = 0    # In beats
    duration = 1    # In beats
    tempo    = 60   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
    MyMIDI.addTempo(track, time, tempo)
    MyMIDI.addTrackName(track, time, "Chord Track")

    MyMIDI2 = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
    MyMIDI2.addTempo(track, time, tempo)
    MyMIDI2.addTrackName(track, time, "Bass Track")

    for i, notes in enumerate(chord):
        print('-----')
        for j, note in enumerate(notes):
            MyMIDI.addNote(track, channel, note + 36, time + i * 2, duration * 2, volume)
            if j == 0:
                MyMIDI2.addNote(track, channel, note + 36, time + i * 2, duration * 2, volume)

    with open("midis/" + str(idx) + "_chord.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)

    with open("midis/" + str(idx) + "_bass.mid", "wb") as output_file:
        MyMIDI2.writeFile(output_file)

    pass


def process(data):
    idx = data['data']['idx']
    requests.post(API_URL + 'exhibit_2202_process', json={'idx': idx, 'process': 1})
    os.system('del ' + os.path.join(CURRENT_PATH, 'midis', '*.mid'))
    os.system('del ' + os.path.join(CURRENT_PATH, 'midis', '*.wav'))
    os.system('del ' + os.path.join(CURRENT_PATH, 'midis', '*.asd'))
    download_melody(API_URL + data['data']['melody'], idx)
    make_chord(data['data']['chord'], idx)
    requests.post(API_URL + 'exhibit_2202_process', json={'idx': idx, 'process': 2})
    daw_rendering_automation(str(idx))
    requests.post(API_URL + 'exhibit_2202_process', json={'idx': idx, 'process': 3})


while True:
    try:
        res = requests.get(API_URL + 'exhibit_2202_list')
        data = res.json()
        if data['data'] == '':
            print('waiting...')
        else:
            process(data)

    except:
        pass

    time.sleep(1)