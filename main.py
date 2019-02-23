import time
import numpy as np
import pyaudio
import fluidsynth
import pymusician as pm
from threading import Thread

SAMPLE_RATE = 44100
TEMPO = 120
SOUNDFONT_FILE = "niceKeys23.sf2"
PARTS = 3

pa = pyaudio.PyAudio()
strm = pa.open(
    format = pyaudio.paInt16,
    channels = 2, 
    rate = SAMPLE_RATE, 
    output = True)

fl = fluidsynth.Synth()
sfid = fl.sfload(SOUNDFONT_FILE)

for ch in range(PARTS):
    fl.program_select(ch, sfid, 0, 25)

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
                TurnOffLater(midi_val,(60 / TEMPO) * (note.rhythm.value / 128) * proportion_to_prev).start()
            else:
                fl.noteoff(0,midi_val)
        else:
            fl.noteoff(0,midi_val)
        previous = rhythm_val

    samples = np.append(samples,fl.get_samples(round(SAMPLE_RATE * (0.02 if not last else 2))))

    strm.write(fluidsynth.raw_audio_string(samples))

if __name__ == "__main__":

    play_notes(pm.Note('C',4,'2'),pm.Note('E',4,'3'))
    play_notes(pm.Note('D',4,'3'),pm.Note('F',4,'3'))
    play_notes(pm.Note('E',4,'3'),pm.Note('G',4,'3'))
    play_notes(pm.Note('F',4,'3'),pm.Note('B',4,'3'))
    play_notes(pm.Note('E',4,'3'),pm.Note('C',5,'3'),last=True)

fl.delete()
strm.close()