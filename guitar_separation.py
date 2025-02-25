import demucs.separate

# Runs the HT Demucs 6 stem model to perform guitar separation from audio file
def separate_guitar(audio):
        separation_args = [
            "--two-stems", "guitar", # Specify two-stem separation (guitar and no guitar)
            "-n", "htdemucs_6s", # Model to use (6s features guitar separation)
            "-o", "./separated_tracks", # Output folder for separated files
            "-d", "cuda", # Specifies to use CUDA instead of CPU
            "--float32", # Saves the wav file as a float32 instead of int24
            audio.path # Input file path
        ]
        demucs.separate.main(separation_args)