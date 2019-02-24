import time
import numpy as np
import pyaudio
import fluidsynth
from threading import Thread

SAMPLE_RATE = 44100
TEMPO = 120
SOUNDFONT_FILE = "niceKeys23.sf2"

pa = pyaudio.PyAudio()
strm = pa.open(
    format = pyaudio.paInt16,
    channels = 2, 
    rate = SAMPLE_RATE, 
    output = True)

fl = fluidsynth.Synth()
sfid = fl.sfload(SOUNDFONT_FILE)

fl.program_select(0, sfid, 0, 24)

class TurnOffLater(Thread):

    def __init__(self,midi_num,wait_time):
        super().__init__()
        self.midi_num = midi_num
        self.wait_time = wait_time
    
    def run(self):
        time.sleep(self.wait_time)
        fl.noteoff(0,self.midi_num)


# takes PyMusician Note objects as args
# The Notes must have octave and rhythm
# uses the TEMPO constant and the first note's rhythm to generate the samples to play
def play_notes(*notes,velocity=100,last=False):
    samples = []

    notes_temp = []

    notes = list(notes)
    notes.sort(key=lambda n: n.rhythm.value)

    for note in notes:
        midi_num = note.hard_pitch + 12
        fl.noteon(0,midi_num,velocity)
        notes_temp.append((midi_num,note.rhythm.value))

    frames = round(SAMPLE_RATE * (60 / TEMPO) * (notes[0].rhythm.value / 128))

    samples = np.append(samples,fl.get_samples(frames))
    
    previous = None
    for midi_val,rhythm_val in notes_temp:
        if previous:
            if previous < rhythm_val:
                rhythm_len = (60 / TEMPO) * (note.rhythm.value / 128) 
                proportion_to_prev = (rhythm_len - ((60 / TEMPO) * (previous / 128))) / rhythm_len
                TurnOffLater(midi_val,(60 / TEMPO) * (note.rhythm.value / 128) * 0.9).start()
            else:
                fl.noteoff(0,midi_val)
        else:
            fl.noteoff(0,midi_val)
        previous = rhythm_val

    samples = np.append(samples,fl.get_samples(round(SAMPLE_RATE * (0.02 if not last else 1))))

    strm.write(fluidsynth.raw_audio_string(samples))

if __name__ == "__main__":
    import pymusician as pm
    import bach_prelude_bb_minor as song

    note_groups = [[pm.Note(*note_deets) for note_deets in note_data] for note_data in song.notes]
    ng_len = len(note_groups)

    _last = False
    for i in range(ng_len):
        if i == ng_len - 1:
            _last = True
        play_notes(*note_groups[i],velocity=70,last=_last)

fl.delete()
strm.close()
