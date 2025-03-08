import os
import pandas as pd
import matplotlib.pyplot as plt
import librosa
from guitar_separation import separate_guitar
from pitch_detection import save_pitches


class AudioLoadHandler():
    """
    Handles loading the audio time series and other relevant data from an
    given audio file path, as well as automatically performing the necessary
    processing by calling the separate_guitar and save_pitches functions.

    Attributes
    ----------
    path : str
        The file path of the audio file to load.
    CHANNELS : int
        Specifies whether the audio channel is mono (1) or stereo (2).
    RATE : int
        The sample rate of the audio.
    metronome_data : ndarray
        The loaded metronome sound's audio time series.
    guitar_data : ndarray
        The song's separated guitar audio time series.
    no_guitar_data : ndarray
        The song's separated no_guitar audio time series.
    guitar_pitch_path : str
        The path of the separated guitar track's pitch predictions MIDI file.
    duration : float
        The length of the loaded song in seconds.
    bpm : float
        The estimated tempo of the song found using Librosa's beat_track.
    first_beat : float
        The first detected beat of the song found using Librosa's beat_track.
    """
    def __init__(self, path):
        """
        The constructor for the AudioLoadHandler class.

        Parameters
        ----------
        path : str
            The file path of the audio file to load.
        """
        self.path = path
        self.CHANNELS = 1
        self.RATE = 44100
        self.DTYPE = "float32"
        
        # Load metronome sound effect
        self.metronome_data = librosa.load( 
            path="./assets/Perc_MetronomeQuartz_lo.wav",
            sr=self.RATE
        )[0]

        self.filename = path.split(".")[1].split("/")[-1]
        separated_tracks_dir = f"./separated_tracks/htdemucs_6s/{self.filename}/"
        guitar_pitches_path = ""

        # If song has not been processed, perform guitar separation and pitch detection
        if not os.path.isdir(separated_tracks_dir):
            guitar_track_path, no_guitar_track_path = separate_guitar(self.path)
            guitar_pitches_path = save_pitches(guitar_track_path)
        else:
            guitar_track_path = separated_tracks_dir + "guitar.wav"
            no_guitar_track_path = separated_tracks_dir + "no_guitar.wav"
            guitar_pitches_path = f"./pitch_predictions/songs/{self.filename}/guitar_basic_pitch.csv"

        # Convert pitches CSV to a pandas DataFrame
        self.pitches = pd.read_csv(
            guitar_pitches_path, 
            sep=None,
            engine="python",
            index_col=False
        ).drop(columns=["end_time_s", "velocity", "pitch_bend"]).sort_values("start_time_s")
        
        # print(self.pitches.head())
        # plt.scatter(self.pitches.start_time_s, self.pitches.pitch_midi)
        # plt.show()
        
        # Get guitar and no_guitar separated tracks' audio time series
        self.guitar_data = librosa.load(
            guitar_track_path,
            sr=self.RATE
        )[0]
        self.no_guitar_data = librosa.load(
            no_guitar_track_path,
            sr=self.RATE
        )[0]
        
        self.duration = len(self.guitar_data) / float(self.RATE) # In seconds

        # Get song tempo and position of first detected beat
        tempo, beats = librosa.beat.beat_track(
            y=self.guitar_data + self.no_guitar_data, # Full mix
            sr=self.RATE
        )
        self.bpm = tempo[0]
        self.first_beat = librosa.frames_to_time(beats[0]) * 1000 # In ms