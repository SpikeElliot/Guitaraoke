import demucs.separate


def separate_guitar(path):
    """
    Uses the HT Demucs 6-stem model to perform guitar separation from a given
    audio file, saving "guitar" and "no_guitar" tracks as WAV files.

    Parameters
    ----------
    path : str
        The path of the audio file to separate.

    Returns
    -------
    separated_track_paths : tuple of str
        The paths to the separated guitar and no_guitar tracks.
    """
    filename = path.split(".")[1].split("/")[-1]

    separation_args = [
        "--two-stems", "guitar", # Specify two-stem separation (guitar and no guitar)
        "-n", "htdemucs_6s", # Model to use (6s features guitar separation)
        "-o", "./separated_tracks", # Output folder for separated files
        "-d", "cuda", # Specifies to use CUDA instead of CPU
        "--float32", # Saves the wav file as a float32 instead of int24
        path # Input file path
    ]
    demucs.separate.main(separation_args)

    return (f"./separated_tracks/htdemucs_6s/{filename}/guitar.wav",
            f"./separated_tracks/htdemucs_6s/{filename}/no_guitar.wav")