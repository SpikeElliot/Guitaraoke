import librosa
import crepe
import numpy as np


class NotePredictor():

    def __init__(self, confidence_threshold=0.7, step_size=20, model_capacity="full"):
        self.confidence_threshold = confidence_threshold
        self.step_size = step_size
        self.model_capacity= model_capacity
    

    def predict(self, audio):
        # Use crepe model to get pitch estimations from audio frames
        times, frequencies, confidences, activations = crepe.predict(
            audio.frames, 
            audio.RATE, 
            step_size=self.step_size,
            model_capacity=self.model_capacity,
            verbose=1
        )

        # Put prediction data into a list of dictionaries
        unfiltered_preds = []
        for i in range(len(times)):
            unfiltered_preds.append(
                {
                    "time": times[i], 
                    "frequency": frequencies[i],
                    "confidence": confidences[i]
                }
            )

        # Ignore any pitch estimations below set confidence threshold
        if self.confidence_threshold > 0:
            unfiltered_preds = list(filter(
                lambda x: x["confidence"] >= self.confidence_threshold, 
                unfiltered_preds
            ))

        # Locate note onsets from audio
        note_onsets = librosa.onset.onset_detect(
            y=audio.frames,
            sr=audio.RATE,
            units='time'
        ).tolist()
        # Append last timestep from predictions to prevent index error
        note_onsets.append(unfiltered_preds[-1]["time"])

        # Shorten list of predictions to only consider note onsets: take median
        # frequency and mean confidence of all timesteps between each onset
        note_predictions = []
        for i in range(len(note_onsets)-1):
            preds = []
            preds = list(filter(
                lambda x: x["time"] >= note_onsets[i] and x["time"] < note_onsets[i+1],
                unfiltered_preds
            ))
                
            # Case: no predictions above confidence threshold are present
            if len(preds) == 0:
                continue

            freqs = []
            confs = []
            for pred in preds:
                freqs.append(pred["frequency"])
                confs.append(pred["confidence"])

            median_freq = np.median(freqs)
            mean_conf = np.mean(confs)

            preds[0]["frequency"] = median_freq
            preds[0]["confidence"] = mean_conf
            # Convert frequency to nearest musical note
            preds[0]["note"] = librosa.hz_to_note(median_freq)

            note_predictions.append(preds[0])
        
        return note_predictions