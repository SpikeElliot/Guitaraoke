import librosa
import torchcrepe
import numpy as np
import csv
import torch

class NotePredictor():

    def __init__(self, fmin=41, fmax=2006, hop_length_in_ms=5,
                 model_capacity="full", device="cuda:0"):
        self.fmin = fmin
        self.fmax = fmax
        self.hop_length_in_ms = hop_length_in_ms
        self.model_capacity = model_capacity
        self.device = device
    

    def predict(self, song, threshold=.21, drop_nan=False, save_data=False):
        # Convert hop length from ms to number of frames for torchcrepe predict
        hop_length = int(song.RATE / (1000/self.hop_length_in_ms))

        # Create a PyTorch tensor from the audio's frames ndarray and
        # reshape it to the format torchcrepe expects for input tensors
        audio = torch.reshape(torch.from_numpy(song.frames), (1, -1))

        # Use torchcrepe model to get pitch estimations from audio frames
        pitches, periodicities = torchcrepe.predict(
            audio,
            song.RATE, 
            hop_length=hop_length,
            fmin=self.fmin,
            fmax=self.fmax,
            model=self.model_capacity,
            batch_size=song.CHUNK,
            device=self.device,
            return_periodicity=True
        )

        # An ndarray containing all times a prediction was made in seconds
        times = np.arange(0, pitches.size(dim=1), dtype="float32")
        times *= self.hop_length_in_ms / 1000

        # Window of 3 * hop length (15ms by default)
        win_length = 3 

        # Filtering out less reliable pitch estimations by periodicity
        periodicities = torchcrepe.filter.median(periodicities, win_length)
        periodicities = torchcrepe.threshold.Silence(-60)(
            periodicities,
            audio,
            song.RATE,
            hop_length
        )
        pitches = torchcrepe.threshold.At(threshold)(pitches, periodicities)

        # Flatten predictions into rank 1 tensors then convert to ndarrays
        pitches = torch.Tensor.numpy(torch.flatten(pitches))
        periodicities = torch.Tensor.numpy(torch.flatten(periodicities))

        # Drop all predictions where pitch is nan
        if drop_nan:
            filtered_preds = list(zip(pitches, periodicities, times))
            filtered_preds = list(
                filter(lambda pred: not np.isnan(pred[0]), filtered_preds)
            )
            pitches, periodicities, times = zip(*filtered_preds)

        # Convert all pitches to their nearest musical note
        notes = librosa.hz_to_note(pitches)

        # Put prediction data into a list of dictionaries
        preds = []
        for i in range(len(times)):
            preds.append(
                {
                    "time": times[i], 
                    "pitch": pitches[i],
                    "note": notes[i],
                    "periodicity": periodicities[i]
                }
            )

        # Save loaded audio file's prediction data as a CSV file
        if save_data:
                try:
                    csvfile = f"{song.filename}_PREDS.csv"
                    keys = preds[0].keys()
                    with open(csvfile, "w", encoding="utf8", newline="") as output_file:
                        dict_writer = csv.DictWriter(output_file, keys)
                        dict_writer.writeheader()
                        dict_writer.writerows(preds)
                except: # Case: attempting to save pitch data of audio stream buffer
                    print("Error: Audio input stream has no filename.")
        
        return preds