import librosa
import torchcrepe
import numpy as np
import csv
import torch


class NotePredictor():

    def __init__(self, fmin=41, fmax=2006, hop_length_in_ms=5,
                 model_capacity="full", device="cuda"):
        self.fmin = fmin
        self.fmax = fmax
        self.hop_length_in_ms = hop_length_in_ms
        self.model_capacity= model_capacity
        self.device = device
    

    def predict(self, song, save_data=False):
        # Convert hop length from ms to number of frames for torchcrepe predict
        hop_length = int(song.RATE / (1000/self.hop_length_in_ms))

        # Create a PyTorch tensor from the audio's frames ndarray and
        # reshape it to the format torchcrepe expects for input tensors
        audio = torch.from_numpy(song.frames)
        audio = torch.reshape(audio, (1, -1))

        # Use torchcrepe model to get pitch estimations from audio frames
        predictions = torchcrepe.predict(
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

        times = np.arange(0, predictions[0].size(dim=1), dtype="float32")
        times *= self.hop_length_in_ms

        pitches = torch.Tensor.numpy(
            torch.reshape(
                predictions[0], (-1,)
            )
        )

        periodicities = torch.Tensor.numpy(
            torch.reshape(
                predictions[1], (-1,)
            )
        )

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