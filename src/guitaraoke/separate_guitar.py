"""
Module providing a function to perform guitar separation using the 6-stem
HT Demucs MSS model.
"""

from pathlib import Path
import demucs.separate
from config import SEP_TRACKS_DIR


def separate_guitar(path: str) -> tuple[str, str]:
    """
    Uses the HT Demucs 6-stem model to perform guitar separation from a given
    audio file, saving "guitar" and "no_guitar" tracks as WAV files.

    Parameters
    ----------
    path : str
        The path of the audio file to separate.

    Returns
    -------
    tuple[Path, Path]
        The paths to the separated guitar [0] and no_guitar tracks [1].
    """
    path = Path(path)
    assert path.exists(), "File does not exist"

    # Check tracks not already separated
    filename = path.stem
    if not (SEP_TRACKS_DIR / filename).exists():
        separation_args = [
            "--two-stems", "guitar", # Specify two-stem separation (guitar)
            "-n", "htdemucs_6s", # Model to use (6s features guitar separation)
            "-o", str(SEP_TRACKS_DIR.parent), # Output folder for separated files
            "-d", "cuda", # Specifies to use CUDA instead of CPU
            "--float32", # Saves the wav file as a float32 instead of int24
            str(path) # Input file path
        ]
        demucs.separate.main(separation_args)

    return (SEP_TRACKS_DIR / filename / "guitar.wav",
            SEP_TRACKS_DIR / filename / "no_guitar.wav")
