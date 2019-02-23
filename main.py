import time
import numpy as np
import pyaudio
import fluidsynth
import pymusician as pm

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
fl.program_select(0, sfid, 0, 25)

# takes PyMusician Note objects as args
# The Notes must have octave and rhythm
# uses the TEMPO constant and the first note's rhythm to generate the samples to play
def play_notes(*notes,velocity=100,last=False):
    samples = []

    rhythm_value = notes[0].rhythm.value
    notes_temp = []
    
    for note in notes:
        midi_num = note.hard_pitch + 12
        fl.noteon(0,midi_num,velocity)
        notes_temp.append(midi_num)

    samples = np.append(samples, fl.get_samples(round(SAMPLE_RATE * (60 / TEMPO) * (rhythm_value / 128))))
    
    for midi_val in notes_temp:
        fl.noteoff(0,midi_val)
    
    samples = np.append(samples,fl.get_samples(round(SAMPLE_RATE * (0.02 if not last else 2))))
    
    strm.write(fluidsynth.raw_audio_string(samples))

if __name__ == "__main__":

    play_notes(pm.Note('C',4,'3'),pm.Note('E',4,'3'))
    play_notes(pm.Note('D',4,'3'),pm.Note('F',4,'3'))
    play_notes(pm.Note('E',4,'3'),pm.Note('G',4,'3'))
    play_notes(pm.Note('G',4,'3'),pm.Note('C',5,'3'),last=True)

fl.delete()
strm.close()