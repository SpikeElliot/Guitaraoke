import demucs.separate

class GuitarSeparator():

    def __init__(self):
        pass

    def separate(self, audio):
        try:
            separation_args = [
                "--two-stems", "guitar", # Specify two-stem separation (guitar and no guitar)
                "-n", "htdemucs_6s", # Model to use (6s features guitar separation)
                "-o", "separated_tracks", # Output folder of separated audio files
                "-d", "cuda", # Specifies to use CUDA instead of CPU
                "--float32", # Saves the wav file as a float32 instead of int24
                f"./assets/{audio.filename}.{audio.filetype}" # Input file
            ]
            demucs.separate.main(separation_args)
        except:
            print("Error: unsupported file type or file name not found")