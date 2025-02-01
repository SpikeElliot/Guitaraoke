import librosa
import crepe


class NotePredictor():

    def __init__(self, confidence_threshold=0, step_size=20, model_cap="full"):
        self.confidence_threshold = confidence_threshold
        self.step_size = step_size
        self.model_cap= model_cap
    

    def predict(self, audio):
        # Use crepe model to get pitch estimations from audio frames
        times, frequencies, confidences, activations = crepe.predict(
            audio.frames, 
            audio.RATE, 
            step_size=self.step_size,
            model_capacity="full",
            verbose=1
        )
        notes = librosa.hz_to_note(frequencies) # Convert freqs to note names

        # Put prediction data into a list of dictionaries
        self.predictions = []
        for i in range(len(times)):
            self.predictions.append(
                {
                    "time": times[i], 
                    "note": notes[i],
                    "frequency": frequencies[i],
                    "confidence": confidences[i]
                }
            )

        # Ignore any pitch estimations below set confidence threshold
        if self.confidence_threshold > 0:
            self.predictions = filter(
                lambda x: x["confidence"] >= self.confidence_threshold, 
                self.predictions
            )

        # Temporary way to check note predictions
        for pred in self.predictions:
            print(f"Time: {pred['time']:.2f} | Note: {pred['note']} | Freq: {pred['frequency']:.2f} | Conf: {pred['confidence']:.2f}")