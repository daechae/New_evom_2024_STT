import ctypes
from ctypes import wintypes
import pythoncom
import win32clipboard
import mido


def read_midi_file(midi_file_path, ticks_per_beat=960, multi_track=True):
    # print('midi_file_path', midi_file_path)
    mid = mido.MidiFile(midi_file_path, ticks_per_beat=ticks_per_beat)
    note_temp = []
    note_import = []
    tick = 0
    track_list = {}
    tick_list = {}
    # -- search track names
    for i, track in enumerate(mid.tracks):
        for msg in track:
            if msg.type == 'track_name':
                print(msg.name)
                track_list[msg.name] = []
                tick_list[msg.name] = []
    cur_track_name = None

    for i, track in enumerate(mid.tracks):
         for msg in track:
            if msg.type == 'track_name':
                track_name = msg.name
                cur_track_name = track_name
            tick += msg.time
            if msg.type == 'note_on' or msg.type == 'note_off':
                if msg.type == 'note_on':
                    pitch = msg.note
                    start = tick / float(mid.ticks_per_beat)
                    start = float("{:.4f}".format(start))  # 시간 퀀타이즈
                    velocity = msg.velocity
                    note_info = {
                        'pitch': pitch,
                        'start_time': round(start, 3),
                        'duration_time': None,
                        'velocity': velocity,
                        'function': None,
                    }
                    note_temp.append(note_info)
                elif msg.type == 'note_off':
                    for j in range(len(note_temp)):
                        if note_temp[j]['pitch'] == msg.note:
                            end = tick / float(mid.ticks_per_beat)
                            note_temp[j]['duration_time'] = round(end - note_temp[j]['start_time'], 3)
                            note_import.append(note_temp[j])
                            del note_temp[j]
                            break
    exit()
    note_import = sorted(note_import, key=lambda k: k['start_time'])
    return note_import


class DROPFILES(ctypes.Structure):
    _fields_ = (('pFiles', wintypes.DWORD),
                ('pt', wintypes.POINT),
                ('fNC', wintypes.BOOL),
                ('fWide', wintypes.BOOL))


def clip_files(file_list):
    offset = ctypes.sizeof(DROPFILES)
    length = sum(len(p) + 1 for p in file_list) + 1
    size = offset + length * ctypes.sizeof(ctypes.c_wchar)
    buf = (ctypes.c_char * size)()
    df = DROPFILES.from_buffer(buf)
    df.pFiles, df.fWide = offset, True
    for path in file_list:
        print("copying to clipboard, filename = " + path)
        array_t = ctypes.c_wchar * (len(path) + 1)
        path_buf = array_t.from_buffer(buf, offset)
        path_buf.value = path
        offset += ctypes.sizeof(path_buf)
    stg = pythoncom.STGMEDIUM()
    stg.set(pythoncom.TYMED_HGLOBAL, buf)
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    try:
        # print(stg)
        # print(stg.data)
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP, stg.data)
        print("clip_files() succeed")
    finally:
        win32clipboard.CloseClipboard()