import midiutil
import pyautogui
import time
import cv2
import numpy as np
import os
import glob
import random
import win32gui
import pyperclip
import util
import win32com.client
import mido
from pprint import pprint
from music21 import *

# pyautogui.PAUSE = 0.5
PRECISION = 0.80
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
SHELL = None

def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def bring_top_window(window_name):
    global SHELL
    if SHELL is None:
        SHELL = win32com.client.Dispatch("WScript.Shell")
    results = []
    top_windows = []
    win32gui.EnumWindows(windowEnumerationHandler, top_windows)

    for i in top_windows:
        # print('top_windows', i)
        if window_name.lower() in i[1].lower():
            print(i)
            win32gui.ShowWindow(i[0], 5)
            SHELL.SendKeys('%')
            win32gui.SetForegroundWindow(i[0])
            break
# bring_top_window('ableton project piano')
# bring_top_window('ableton project trap')
# exit()
# pyautogui.click(pause=0.5)


def imagesearch_gray(image, precision=PRECISION):
    im = pyautogui.screenshot()
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc, (template.shape[1], template.shape[0])


def imagesearch_color(image, precision=PRECISION):
    im = pyautogui.screenshot()
    img_rgb = np.array(im)
    # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc, (template.shape[1], template.shape[0])


imagesearch = imagesearch_gray


def imagesearch_multiple(image, precision=PRECISION):
    im = pyautogui.screenshot()
    # im.save('testarea.png')
    # im.save('testarea.png') useful for debugging purposes, this will save the captured region as "testarea.png"
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    # template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= PRECISION)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return loc, (template.shape[1], template.shape[0])


def imagesearch_loop_multi(image, timesample=1.0, precision=PRECISION, false_time=10.0):
    pos = imagesearch_multiple(image, precision)
    total_time = 0.
    while pos[0] == -1:
        if total_time > false_time:
            return (False, False), (False, False)
        print(image + " not found, waiting")
        time.sleep(timesample)
        pos = imagesearch_multiple(image, precision)
        total_time += timesample
    return pos

# print(imagesearch_loop_multi('ableton_melody_track.png'))
# exit()

# def there_is_no_image(image, precision=0.8):
#     rst = imagesearch(image, 0.8)
#     if rst == [-1, -1]:
#         return True
#     else:
#         return False


def imagesearch_loop(image, timesample=0.1, precision=PRECISION, false_time=10.):
    pos = imagesearch(image, precision)
    total_time = 0
    while pos[0] == -1:
        if total_time > false_time:
            return (False, False), (False, False)
        print(image + " not found, waiting")
        time.sleep(timesample)
        pos = imagesearch(image, precision)
        total_time += timesample
    return pos


def imagesearch_loop_2(images, precision=PRECISION):
    while True:
        for image in images:
            pos = imagesearch(image, precision)
            if pos[0] != -1:
                # print('pos', pos)
                return pos
            print(image + " not found, waiting")



def midifile_to_daw_track(prj_name, target_midi_path, target_daw_track_png, refresh=False, false_time=10.0, check_png=None):
    pyautogui.hotkey('alt', 'tab')
    # copy 미디파일 to 클립보드
    util.clip_files([target_midi_path])   # 프로젝트에 맞게 파일이름 변경
    pyautogui.hotkey('alt', 'tab')
    time.sleep(0.5)
    bring_top_window(prj_name)
    # bring_top_window(prj_name[1])
    # 기다려
    (x, y), (w, h) = imagesearch_loop(r'automation_png\ableton_wait.png', false_time=false_time)
    # time.sleep(0.1)
    # 에이블톤 트랙에 붙혀넣기
    locs, (w, h) = imagesearch_loop_multi(target_daw_track_png, false_time=false_time)
    time.sleep(0.1)
    if locs[0] is False:
        return False
    inst_choice = random.randint(0, len(locs[0]) - 1)
    x, y = locs[1][inst_choice], locs[0][inst_choice]
    pyautogui.click(x - 100, y + int(h / 2))
    # 홈 키가 안먹혀서 오토핫키로 다시 맵핑함
    pyautogui.keyDown('alt')
    pyautogui.press('h')
    pyautogui.keyUp('alt')
    # pyautogui.hotkey('alt', 'h')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    # 기다려
    # if check_png is not None:
    #     (x, y), (w, h) = imagesearch_loop(check_png, false_time=false_time)
    return True


def fx_track_activate(prj_name, target_daw_track_png, refresh=False, false_time=10.0, check_png=None):
    # (x, y), (w, h) = imagesearch_loop(r'automation_png\ableton_wait.png', false_time=false_time)
    # time.sleep(0.2)
    locs, (w, h) = imagesearch_loop_multi(target_daw_track_png, false_time=false_time)
    time.sleep(0.1)
    if locs[0] is False:
        return False
    inst_choice = random.randint(0, len(locs[0]) - 1)
    x, y = locs[1][inst_choice], locs[0][inst_choice]
    pyautogui.click(x + int(w / 2), y + int(h / 2))
    pyautogui.press('0')
    return True


def ableton_midi_track_del(time_sleep=0.5):
    # 에이블톤 프로젝트 활성화
    pyautogui.keyDown('alt')
    pyautogui.press('a')
    pyautogui.keyUp('alt')
    time.sleep(time_sleep)
    # 트랙 삭제하기
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(time_sleep)
    pyautogui.keyDown('alt')
    pyautogui.press('d')
    pyautogui.keyUp('alt')
    time.sleep(time_sleep)


# def daw_automatiKKKKKKKKKKKKon(gen_folder_path, style_params):
#     # file2Clipboard = os.path.join(CURRENT_PATH, 'fileToClipboard.exe')
#     prj_name1 = 'ableton project ' + style_params['genre']
#     prj_name2 = 'ableton project ' + style_params['genre'] + ' ' + style_params['sub-genre']
#     prj_name = [prj_name1, prj_name2]
#     while True:
#         if len(glob.glob(os.path.join(gen_folder_path, '*.mid*'))) >= 2:
#             break
#     while True:
#         if os.path.exists(os.path.join(gen_folder_path, '1_melody.mid')):
#             break
#         print('미디 파일 없음...')
#     time.sleep(1)
#
#     while True:
#         if midifile_to_daw_track(prj_name, r'automation_png\midi_melody.png', r'automation_png\ableton_melody_track.png', refresh=True, false_time=10.0, check_png=r'automation_png\ableton_check_melody.png') is False:
#             ableton_midi_track_del(time_sleep=0.5)
#             continue
#         if midifile_to_daw_track(prj_name, r'automation_png\midi_acc.png', r'automation_png\ableton_acc_track.png', false_time=10.0) is False:
#             ableton_midi_track_del(time_sleep=0.5)
#             continue
#         if midifile_to_daw_track(prj_name, r'automation_png\midi_bass.png', r'automation_png\ableton_bass_track.png', false_time=10.0) is False:
#             ableton_midi_track_del(time_sleep=0.5)
#             continue
#         # 장르별로 테스트하면서 수정해야함
#
#
#         if style_params['genre'] in ['ambient']:
#             if midifile_to_daw_track(prj_name, r'automation_png\midi_pad.png', r'automation_png\ableton_pad_track.png', false_time=10.0) is False:
#                 ableton_midi_track_del(time_sleep=0.5)
#                 continue
#         if style_params['genre'] in ['hiphop', 'trot']:
#             if midifile_to_daw_track(prj_name, r'automation_png\midi_drum.png', r'automation_png\ableton_drum_track.png', false_time=10.0) is False:
#                 ableton_midi_track_del(time_sleep=0.5)
#                 continue
#             if midifile_to_daw_track(prj_name, r'automation_png\midi_pad.png', r'automation_png\ableton_pad_track.png', false_time=10.0) is False:
#                 ableton_midi_track_del(time_sleep=0.5)
#                 continue
#             if midifile_to_daw_track(prj_name, r'automation_png\midi_bass.png', r'automation_png\ableton_bass_track.png', false_time=10.0) is False:
#                 ableton_midi_track_del(time_sleep=0.5)
#                 continue
#         if style_params['genre'] == 'edm':
#             # if midifile_to_daw_track(prj_name, r'automation_png\midi_bass.png', r'automation_png\ableton_bass_track.png', false_time=10.0) is False:
#             #     ableton_midi_track_del(time_sleep=0.5)
#             #     continue
#             if midifile_to_daw_track(prj_name, r'automation_png\midi_drum.png', r'automation_png\ableton_drum_track.png', false_time=10.0) is False:
#                 ableton_midi_track_del(time_sleep=0.5)
#                 continue
#             if midifile_to_daw_track(prj_name, r'automation_png\midi_pad.png', r'automation_png\ableton_pad_track.png', false_time=10.0) is False:
#                 ableton_midi_track_del(time_sleep=0.5)
#                 continue
#             if midifile_to_daw_track(prj_name, r'automation_png\midi_percussion.png', r'automation_png\ableton_percussion_track.png', false_time=10.0) is False:
#                 ableton_midi_track_del(time_sleep=0.5)
#                 continue
#
#             # FX 트랙 활성화
#             if fx_track_activate(prj_name, r'automation_png\ableton_buildup_track.png', false_time=10.0) is False:
#                 exit()
#             if fx_track_activate(prj_name, r'automation_png\ableton_upsweep_track.png', false_time=10.0) is False:
#                 exit()
#             if fx_track_activate(prj_name, r'automation_png\ableton_impact_track.png', false_time=10.0) is False:
#                 exit()
#             if fx_track_activate(prj_name, r'automation_png\ableton_boom_track.png', false_time=10.0) is False:
#                 exit()
#             if fx_track_activate(prj_name, r'automation_png\ableton_downsweep_track.png', false_time=10.0) is False:
#                 exit()
#
#         # # 뉴에이지 장르에서는 템포 트랙을 임포트함.
#         # if style_params['genre'] == 'new-age':
#         #     if midifile_to_daw_track(prj_name, r'automation_png\midi_tempo.png', r'automation_png\ableton_tempo_track.png', false_time=10.0) is False:
#         #         ableton_midi_track_del(time_sleep=0.5)
#         #         continue
#         # 엠비언트 장르에서는 패드 트랙을 임포트함.
#         # if style_params['genre'] == 'ambient':
#         #     if midifile_to_daw_track(prj_name, r'automation_png\midi_pad.png', r'automation_png\ableton_pad_track.png', false_time=10.0) is False:
#         #         ableton_midi_track_del(time_sleep=0.5)
#         #         continue
#         break
#
#     # print('멜로디 트랙 위치 ', imagesearch(r'automation_png\ableton_check_melody.png'))
#     # print('반주 트랙 위치 ', imagesearch(r'automation_png\ableton_check_acc.png'))
#     # print('베이스 트랙 위치 ', imagesearch(r'automation_png\ableton_check_bass.png'))
#     # mp3 생성
#     pyautogui.press('w')
#     pyautogui.hotkey('ctrl', 'shift', 'r')
#     pyautogui.press('enter', interval=1.0, presses=2)
#     time.sleep(1)
#
#     while True:
#         if len(glob.glob(os.path.join(gen_folder_path, '*.mp3'))) > 0 or len(glob.glob(os.path.join(gen_folder_path, '*.wav'))) > 0:
#             break
#
#     # ableton_midi_track_del(time_sleep=0.5)
#     # 샘플이랑 같이 있는 프로젝트는 이렇게 삭제하면 샘플도 같이 지워져서 안됨
#     for _ in range(11):
#         pyautogui.hotkey('ctrl', 'z')
#         time.sleep(0.5)
#
#     # pyautogui.keyDown('alt')
#     # pyautogui.press('p')
#     # pyautogui.keyUp('alt')
#     bring_top_window('evom [')
#     time.sleep(0.5)
#     # (x, y), (w, h) = imagesearch_loop('abletone_melody_track.png')
#     # pyautogui.rightClick(x - 100, y + int(h / 2), pause=0.1)
#     # (x, y), (w, h) = imagesearch_loop('del.png')
#     # pyautogui.click(x + int(w/2), y + int(h / 2), duration=0.1, pause=0.5)
#
#     return glob.glob(os.path.join(gen_folder_path, '*.wav'))[0]


def midi_to_analog_midi(path):
    # 아날로그미디 변환 프로그램 실행
    # bring_top_window('MID2PIanoCD')
    # os.startfile(r'C:\Program Files (x86)\MID2PianoCD\mid2pianocd.exe')
    time.sleep(1)

    # 미디파일 불러오기
    pyautogui.press('a')
    time.sleep(0.5)
    # pyperclip.copy(idx + '_melody.mid')  # 멜로디 미디파일
    pyperclip.copy(path)  # 멜로디 미디파일
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(0.5)

    # 변환시작
    pyautogui.press('s')
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(0.5)

    # # 초기화
    # # pyautogui.press('r')  # start convert를 하고 나서는 한번 단축키가 먹통이 됨
    # (x, y), (w, h) = imagesearch_loop(os.path.join(CURRENT_PATH, 'automation_png', 'mid2pianoCD_removeall.PNG'), false_time=10)
    # time.sleep(0.1)
    # if x is False:
    #     return False
    # pyautogui.click(x + int(w / 2), y + int(h / 2))
    pyautogui.hotkey('alt', 'f4')
    time.sleep(0.1)


def read_midi_file(midi_file_path, ticks_per_beat=960, multi_track=False):
    mid = mido.MidiFile(midi_file_path, ticks_per_beat=ticks_per_beat)
    note_temp = []
    note_import_list = []
    tick = 0
    for i, track in enumerate(mid.tracks):
        if i == 0:
            note_import_list.append([])
        elif multi_track:
            tick = 0
            note_import_list.append([])

        for msg in track:
            tick += msg.time
            if msg.type == 'note_on' or msg.type == 'note_off':
                if msg.type == 'note_on':
                    pitch = msg.note
                    start = tick / float(mid.ticks_per_beat)
                    # velocity = 80 if msg.velocity > 80 else msg.velocity
                    velocity = msg.velocity
                    # note_temp.append([pitch, start, -1, velocity])
                    note_info = {
                        'pitch': pitch,
                        'start_time': start,
                        'duration_time': None,
                        'velocity': velocity,
                        'function': None,
                    }
                    note_temp.append(note_info)
                elif msg.type == 'note_off':
                    for j in range(len(note_temp)):
                        if note_temp[j]['pitch'] == msg.note:
                            end = tick / float(mid.ticks_per_beat)
                            note_temp[j]['duration_time'] = end - note_temp[j]['start_time']
                            note_import_list[-1].append(note_temp[j])
                            del note_temp[j]
                            break

    # note_import = sorted(note_import_list[-1], key=lambda k: k['start_time'])
    return note_import_list


def daw_rendering_automation(idx):

    # tempo = random.randint(60, 80)
    tempo = 120
    # todo: 멜로디 미디와 코드, 베이스 미디를 1개의 파일에 1개의 트랙으로 합침 (피아노 용)
    multi_tracks = read_midi_file(os.path.join(CURRENT_PATH, 'midis', str(idx)+'_melody.mid'), multi_track=True)
    tempo_notes = multi_tracks[0]
    melody_notes = multi_tracks[1]
    acc_notes = multi_tracks[2]
    chord_notes = read_midi_file(os.path.join(CURRENT_PATH, 'midis', str(idx)+'_chord.mid'))[0]
    bass_notes = read_midi_file(os.path.join(CURRENT_PATH, 'midis', str(idx)+'_bass.mid'))[0]
    all_notes = melody_notes + chord_notes + bass_notes
    all_notes = sorted(all_notes, key=lambda k: k['start_time'])
    # # 길이를 2배씩 늘리기
    # for n in all_notes:
    #     n['start_time'] *= 2.
    #     n['duration_time'] *= 2.

    # 겹쳐지는 노트 보정해주기 (길이 끊어주기)

    # 1. 시작위치와 음이 같은 노트는 긴노트만 살려둠.
    _all_note = []
    for i in range(len(all_notes)):
        is_survive = True
        for j in range(len(all_notes)):
            if i != j:
                if all_notes[i]['start_time'] == all_notes[j]['start_time'] and \
                        all_notes[i]['pitch'] == all_notes[j]['pitch']:
                    if all_notes[i]['duration_time'] < all_notes[j]['duration_time']:
                        is_survive = False
                        break
        if is_survive:
            _all_note.append(all_notes[i].copy())
    all_notes = _all_note
    # 2. 중간에 다른 음이 시작되면 그 앞에서 끊어주기
    for i in range(len(all_notes)):
        for j in range(len(all_notes)):
            if i != j and all_notes[i]['pitch'] == all_notes[j]['pitch']:
                if all_notes[i]['start_time'] < all_notes[j]['start_time'] < all_notes[i]['start_time'] + all_notes[i]['duration_time']:
                    new_dur = all_notes[j]['start_time'] - all_notes[i]['start_time']
                    if new_dur < all_notes[i]['duration_time']:
                        all_notes[i]['duration_time'] = new_dur

    single_track_midi = midiutil.MIDIFile(1, ticks_per_quarternote=int(960/2))
    single_track_midi.addTempo(0, 0, tempo)
    for note in all_notes:
        single_track_midi.addNote(0, 0, note['pitch'], note['start_time'], note['duration_time'], note['velocity'])

    with open(os.path.join(CURRENT_PATH, 'midis', 'single_track.mid'), 'wb') as output_file:
        single_track_midi.writeFile(output_file)

    # todo : 멜로디, 코드, 베이스 트랙을 하나의 파이에 개별 트랙으로 넣음
    multi_tracks = read_midi_file(os.path.join(CURRENT_PATH, 'midis', str(idx) + '_melody.mid'), multi_track=True)
    tempo_notes = multi_tracks[0]
    melody_notes = multi_tracks[1]
    acc_notes = multi_tracks[2]
    chord_notes = read_midi_file(os.path.join(CURRENT_PATH, 'midis', str(idx) + '_chord.mid'))[0]
    bass_notes = read_midi_file(os.path.join(CURRENT_PATH, 'midis', str(idx) + '_bass.mid'))[0]
    all_notes = melody_notes + chord_notes + bass_notes
    all_notes = sorted(all_notes, key=lambda k: k['start_time'])
    # # 길이를 2배씩 늘리기
    # for n in all_notes:
    #     n['start_time'] *= 2.
    #     n['duration_time'] *= 2.

    multi_track_midi = midiutil.MIDIFile(4)
    multi_track_midi.addTempo(0, 0, tempo)
    for note in melody_notes:
        multi_track_midi.addNote(0, 0, note['pitch'], note['start_time'], note['duration_time'], note['velocity'])

    multi_track_midi.addTempo(1, 0, tempo)
    for note in acc_notes:
        multi_track_midi.addNote(1, 0, note['pitch'], note['start_time'], note['duration_time'], note['velocity'])

    multi_track_midi.addTempo(2, 0, tempo)
    for note in chord_notes:
        multi_track_midi.addNote(2, 0, note['pitch'], note['start_time'], note['duration_time'], note['velocity'])

    multi_track_midi.addTempo(3, 0, tempo)
    for note in bass_notes:
        multi_track_midi.addNote(3, 0, note['pitch'], note['start_time'], note['duration_time'], note['velocity'])

    with open(os.path.join(CURRENT_PATH, 'midis', 'multi_tracks.mid'), 'wb') as output_file:
        multi_track_midi.writeFile(output_file)

    # exit()

    # 멜로디 미디 --> 아날로그 미디 wav 파일로 변환
    # midi_to_analog_midi(os.path.join(CURRENT_PATH, 'midis', 'single_track.mid'))

    # 에이블톤 템플릿 프로젝트 트랙에 파일들 배치하기
    # if midifile_to_daw_track('biennale_prj', os.path.join(CURRENT_PATH, 'automation_png', 'ableton_all_track_analog_midi.png'), os.path.join(CURRENT_PATH, 'automation_png', 'ableton_analog_midi_track.png'), false_time=10.0) is False:
    #     exit()
    if midifile_to_daw_track(
            'ableton_prj',
            os.path.join(CURRENT_PATH, 'automation_png', 'ableton_multi_tracks_midifile.PNG'),
            os.path.join(CURRENT_PATH, 'automation_png', 'ableton_melody_track.png'),
            false_time=10.0) is False:
        exit()
    # if midifile_to_daw_track('biennale_prj', os.path.join(CURRENT_PATH, 'automation_png', 'midi_chord_file.png'), os.path.join(CURRENT_PATH, 'automation_png', 'ableton_acc_track.png'), false_time=10.0) is False:
    #     exit()
    # if midifile_to_daw_track('biennale_prj', os.path.join(CURRENT_PATH, 'automation_png', 'midi_bass_file.png'), os.path.join(CURRENT_PATH, 'automation_png', 'ableton_bass_track.png'), false_time=10.0) is False:
    #     exit()

    # 에이블톤 프로젝트 재생
    pyautogui.keyDown('alt')
    pyautogui.keyDown('h')
    pyautogui.keyUp('alt')
    time.sleep(0.5)
    pyautogui.press('space')

    # 30초 가량 재생 후 정지 및 초기화
    beat_time = 60. / tempo
    bar_tiem = beat_time * 4.
    time.sleep(bar_tiem * 8 + 1.0)
    pyautogui.press('space')
    time.sleep(0.5)
    # pyautogui.hotkey('ctrl', 'a')
    # time.sleep(0.5)
    # pyautogui.keyDown('alt')
    # pyautogui.press('d')
    # pyautogui.keyUp('alt')
    for _ in range(1):
        pyautogui.hotkey('ctrl', 'z')
    time.sleep(0.5)
    # 끝나고 신호 보내기
    print('생성 및 재생 완료')


def daw_midi_play_automation(category):

    midi_path_list = glob.glob(os.path.join(CURRENT_PATH, 'midis', '2022-04-13', category, '*.mid'))
    midi_path = random.choice(midi_path_list)
    print('midi_path', midi_path)
    if midifile_to_daw_track(
            'biennale_prj',
            target_midi_path=midi_path,
            target_daw_track_png=os.path.join(CURRENT_PATH, 'automation_png', 'ableton_melody_track.png'),
            false_time=10.0) is False:
        exit()

    # 에이블톤 프로젝트 재생
    pyautogui.keyDown('alt')
    pyautogui.keyDown('h')
    pyautogui.keyUp('alt')
    time.sleep(0.5)
    pyautogui.press('space')

    # midi_path 미디파일 불러와서 총 길이 계산필요. Tempo?
    # midi_seq = util.read_midi_file(midi_path)
    # pprint(midi_seq)

    midi_file = converter.parse(midi_path)
    notes = midi_file.flat.notes
    last_time = 0
    for note in notes:
        start_time = note.offset
        end_time = start_time + note.duration.quarterLength
        last_time = end_time if end_time > last_time else last_time
    print('노트정보 불러오기 완료', last_time)

    # BPM 추출
    bpm = None
    for event in midi_file.flat:
        if 'MetronomeMark' in event.classes:
            bpm = event.getQuarterBPM()
            break

    print('bpm', bpm)


    # tempo = 0
    # with mido.MidiFile(midi_path) as mid:
    #     for i, track in enumerate(mid.tracks):
    #         for msg in track:
    #             if msg.type == 'set_tempo':
    #                 tempo = mido.tempo2bpm(msg.tempo)
    #                 print(f'Tempo: {tempo} bpm')
    # assert tempo > 0
    #
    # last_time = 0
    # for n in midi_seq:
    #     if n['start_time'] + n['duration_time'] > last_time:
    #         last_time = n['start_time'] + n['duration_time']
    # assert last_time > 0
    # print('last_time', last_time)
    play_time = 60. / bpm * last_time
    print('waiting start...', play_time)
    time.sleep(play_time)
    print('waiting end...')




def daw_stop_and_clean(prj_name, precision=0.8):
    #pyautogui.press('alt')
    bring_top_window(prj_name)
    time.sleep(0.1)
    # 플레이 정지
    (x, y), (w, h) = imagesearch_loop_2(
        [r'automation_png\ableton_wait.png', r'automation_png\ableton_playing.png'],
        precision=precision
    )
    x = int(x + w/2)
    y = int(y + h/2)
    pyautogui.click(x, y)
    time.sleep(0.5)
    pyautogui.click(963, 414)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    # pyautogui.hotkey('alt', 'd')
    pyautogui.press('backspace')

