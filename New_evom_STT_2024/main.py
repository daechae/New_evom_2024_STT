import requests, json
import time
from midiutil import MIDIFile
import os
from automation import daw_midi_play_automation, daw_stop_and_clean
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

    # 일단 요청이 들어오면 현재 플레이중일 수 있으니 정지 모션 한번하고 다음으로 넘어감
    #daw_stop_and_clean('biennale_prj', precision=0.7)

    idx = data['data']['idx']
    requests.post(API_URL + 'evom_midi_process', json={'idx': idx, 'process': 1})
    os.system('del ' + os.path.join(CURRENT_PATH, 'midis', '*.mid'))
    os.system('del ' + os.path.join(CURRENT_PATH, 'midis', '*.wav'))
    os.system('del ' + os.path.join(CURRENT_PATH, 'midis', '*.asd'))
    # download_melody(API_URL + data['data']['melody'], idx)
    # 여기서 자동피아노 작동하고
    # make_chord(data['data']['chord'], idx)
    print('처리1')
    requests.post(API_URL + 'evom_midi_process', json={'idx': idx, 'process': 2})

    expression = data['data']['expression']
    if expression in ['neutral']:
        category = 'new-age_maj'
    elif expression in ['sad', 'fearful', 'angry', 'disgust']:
        category = 'new-age_min'
    elif expression in ['surprised', 'happy']:
        category = 'pop-piano'
    else:
        print('expression', expression)
        exit()
    daw_midi_play_automation(category)
    print('처리2')
    requests.post(API_URL + 'evom_midi_process', json={'idx': idx, 'process': 3})
    print('처리완료')

    daw_stop_and_clean('biennale_prj', precision=0.7)


if __name__ == '__main__':

    data = {'error': 0, 'data': {'idx': 1219, 'expression': 'neutral', 'process': 0}}
    process(data)

    import util
    # util.read_midi_file(os.path.join('midis', '2022-04-13', 'new-age_maj', 'total_20220413101257.mid'))
    # exit()
    while True:
        try:
            res = requests.get(API_URL + 'evom_midi_list')
            data = res.json()
            print(data)
            if data['data'] == '':
                print('waiting...')
            else:
                process(data)
        except:
            pass

        time.sleep(1)