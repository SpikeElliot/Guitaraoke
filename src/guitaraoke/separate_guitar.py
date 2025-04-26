"""
Provides a function that abstracts guitar separation from an audio 
file.
"""

from pathlib import Path
import demucs.separate
from guitaraoke.utils import read_config

config = read_config("Audio")

def separate_guitar(path: str | Path) -> tuple[Path, Path]:
    """
    Uses the HT Demucs 6-stem model to perform guitar separation from
    a given audio file, saving "guitar" and "no_guitar" tracks as WAV
    files.

    Parameters
    ----------
    path : str | Path
        The path of the audio file to separate.

    Returns
    -------
    tuple[Path, Path]
        The paths to the separated guitar [0] and no_guitar tracks [1].
    """
    assert isinstance(path, (Path, str)), "File path should be a string or pathlib Path"
    path = Path(path)
    assert path.exists(), "File does not exist"

    # Check tracks not already separated
    filename = path.stem
    if not (Path(config["sep_tracks_dir"]) / filename).exists():
        separation_args = [
            "--two-stems", "guitar", # Specify two-stem separation (guitar)
            "-n", "htdemucs_6s", # Model to use (6s features guitar separation)
            "-o", str(Path(config["sep_tracks_dir"]).parent), # Output folder for separated files
            "-d", "cuda", # Specifies to use CUDA instead of CPU
            "--float32", # Saves the wav file as a float32 instead of int24
            str(path) # Input file path
        ]
        demucs.separate.main(separation_args)

    return (Path(config["sep_tracks_dir"]) / filename / "guitar.wav",
            Path(config["sep_tracks_dir"]) / filename / "no_guitar.wav")
