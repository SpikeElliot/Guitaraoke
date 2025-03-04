import librosa
from tinytag import TinyTag
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
    title : str
        The title found in metadata from a loaded audio file.
    artist : str
        The artist found in metadata from a loaded audio file.
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
        
        # Load metronome sound effect
        self.metronome_data = librosa.load( 
            path="./assets/Perc_MetronomeQuartz_lo.wav",
            sr=self.RATE
        )[0]

        # Get song metadata
        metadata = TinyTag.get(self.path)
        self.title = metadata.title or "Unknown"
        self.artist = metadata.artist or "Unknown"
        fn_split = metadata.filename.split(".")
        self.filename, self.filetype = fn_split[1].split("/")[-1], fn_split[2]
        self.filedir = fn_split[1].split("/")[-2]

        # TODO Check if song has already been separated. If so, load in guitar
        # and no_guitar files to play concurrently. Otherwise, run the
        # separate_guitar function on the file first.

        # Get audio frames from guitar no_guitar separated tracks
        self.guitar_data = librosa.load(
            f"./separated_tracks/htdemucs_6s/{self.filename}/guitar.wav",
            sr=self.RATE
        )[0]
        self.no_guitar_data = librosa.load(
            f"./separated_tracks/htdemucs_6s/{self.filename}/no_guitar.wav",
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