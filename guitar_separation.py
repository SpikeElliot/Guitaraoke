import demucs.separate


def separate_guitar(audio):
    """
    Uses the HT Demucs 6-stem model to perform guitar separation from a given
    audio file, saving "guitar" and "no_guitar" tracks as WAV files.

    Parameters
    ----------
    audio : AudioLoadHandler
        The AudioLoadHandler object whose path property will be used to
        access the audio file.

    Returns
    -------
    guitar_track_path : str
        The file path to the separated guitar track.
    """
    separation_args = [
        "--two-stems", "guitar", # Specify two-stem separation (guitar and no guitar)
        "-n", "htdemucs_6s", # Model to use (6s features guitar separation)
        "-o", "./separated_tracks", # Output folder for separated files
        "-d", "cuda", # Specifies to use CUDA instead of CPU
        "--float32", # Saves the wav file as a float32 instead of int24
        audio.path # Input file path
    ]
    demucs.separate.main(separation_args)
    return f"./separated_tracks/htdemucs_6s/{audio.filename}/guitar.wav"