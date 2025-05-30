<a>
  <img alt="An image of Guitaraoke's splash screen" src="https://github.com/user-attachments/assets/7500b7d1-11be-461e-9f11-5392d8e55ec8" width=100%">
</a>

# Guitaraoke

Guitaraoke is a novel, standalone Windows application that leverages pre-trained machine learning models to provide guitarists learning a song “by ear”
immediate automatic performance feedback against the song’s guitar track through a karaoke-style scoring system.

## Features

- An music source separation model ([6-stem HT Demucs model](https://github.com/adefossez/demucs)) is used to separate the guitar source from an audio
file into an isolated track.

- An automatic music transcription model ([Spotify's Basic Pitch](https://github.com/spotify/basic-pitch)) is used to extract note pitch and timings from both the
separated guitar track to generate note references; the model is then used on recorded chunks of the user’s guitar signal to estimate played notes.

- A scoring algorithm was developed to evaluate the user’s musical performance by comparing their guitar notes to the reference notes from the separated guitar track.

- An audio I/O library ([sounddevice](https://python-sounddevice.readthedocs.io/en/0.5.1/)) is used to perform song playback and recording of a user’s guitar input.
  
- A GUI framework ([PyQt6](https://pypi.org/project/PyQt6/)) is used to provide audio playback controls, user performance display, and navigable screens for the application.

## Setup Screen

The application's first screen, allowing the user to select their audio input device from a drop-down list and providing a
**Select Song** button that opens the system's file browser for the user to select a WAV file to practice.

<a>
  <img alt="An annotated screenshot of Guitaraoke's setup screen" src="https://github.com/user-attachments/assets/fc070682-cc5d-4aa1-b3c6-424fb3167a66" width=100%">
</a>

A popup screen is shown after the user selects a new song from their local files, providing a form for the user to submit the selected song's title and artist, displayed
in practice mode (and in the future will be shown in a song selection menu alongside other metadata and high scores).

## Practice Mode Screen

The main screen of the application, featuring song playback controls (play/pause, looping, skipping, etc.) and the full
implementation of the user performance scoring system.

<a>
  <img alt="An annotated screenshot of Guitaraoke's practice mode screen (1/2)" src="https://github.com/user-attachments/assets/41ce7b03-c578-4a9c-bb9b-c607b554006e" width=100%">
</a>

When the user plays the correct notes to a song, a swing display is shown that indicates the degree to which their performance is rushing or dragging when more than 10ms off.

<a>
  <img alt="An annotated screenshot of Guitaraoke's practice mode screen (2/2)" src="https://github.com/user-attachments/assets/d60db3aa-1fae-4b7c-8bc2-e3957c81e011" width=100%">
</a>

## Try it out!

**Guitaraoke v.0.3.0-alpha** can be downloaded and played with from the [Public Google Drive Folder](https://drive.google.com/drive/folders/1JbStcbCxSVMlb2Nbo6wPuVP3v3a18yvH?usp=sharing).

### System Requirements

- Windows OS (Tested on 10 and 11)

- Nvidia GPU with CUDA support (Tested on 10, 20, 30, and 40 series)

- Min. Quad-core CPU (Tested on Intel Core i7 and AMD Ryzen 5)

- Min. 8GB of RAM

- Min. 6GB of storage space

### Use Instructions

1. Launch the application.

2. Select your input device from the drop-down list.

3. Press the "Select Song" button to pick a WAV file from your local
   files (the file browser defaults to a "songs" folder created in the same directory as the executable at run-time, where you can store songs for convenience).

4. Wait for the application to finish guitar separation and note event
   prediction.

5. Start the song and play along with your guitar, and the scoring
   system will estimate your accuracy score and swing in real time.

6. Play around with the playback controls such as the loop section markers and guitar track volume slider!

7. If you would like to practice a different song, click the back button at the top right to go back to the
setup screen.

### Important Note

Keep the executable (Guitaraoke.exe) in a directory at the same level
as the "_internal" and "data" folders to allow the application to find
them at run-time.

## Reproducibility

1. Clone the repository.

2. [Follow the instructions for installation of Demucs on Windows](https://github.com/facebookresearch/demucs/blob/main/docs/windows.md), making sure the Python version of the created Anaconda environment is 3.11.12.

3. Run `pip install -e .` in the terminal to install all modules and dependencies required in editable mode.

## Future Improvements

### Planned

- A song speed slider

- Volume sliders for other instruments (drums, vocals, bass)

- A metronome during song playback

- Full playthrough mode with saved high scores

- Make loop markers draggable and looping behaviour clearer

### Potentially

- A pitch shift or transposition slider

- Generated note annotations or tabs display

## Known Issues

- Due to the limitations of the pre-trained models used, the scoring system performs better on certain songs over others (songs with guitar tunings outside of the range of E-standard e.g. drop-tunings and 7-string guitars have a much lower separation quality and capture of note events).

- There are limitations with the accuracy of the current scoring system due to issues such as a chunk cutoff problem (where, due to performing scoring on discrete 1 second chunks of audio, user-played notes that should count as hits can be missed if they occur at the edges of these chunks).
This will be addressed in a future update.

- There is also currently an issue regarding the looping, whereif the loop size falls short of a whole second, any notes played after the final cutoff are discarded and therefore not scored; for example, when the end of a looping section from **2s** to **4.9s** is reached,
the current chunk will contain **0.9s** of input, which is not scored before the loop resets: this means any notes played after the chunk cutoff at **3s** will not have contributed to their score.

- There is currently a visual bug with the count-in toggle and looping toggle buttons' tooltips.

## Attributions

<a href="https://www.flaticon.com/uicons">Uicons by Flaticon</a>

<a href="https://www.flaticon.com/free-icons/play" title="play icons">Play icons created by Freepik - Flaticon</a>

<a href="https://www.flaticon.com/free-icons/pause" title="pause icons">Pause icons created by inkubators - Flaticon</a>

<a href="https://www.flaticon.com/free-icons/countdown" title="countdown icons">Countdown icons created by Freepik - Flaticon</a>

<a href="https://www.flaticon.com/free-icons/refresh" title="refresh icons">Refresh icons created by Freepik - Flaticon</a>

<a href="https://www.flaticon.com/free-icons/skip-button" title="skip button icons">Skip button icons created by Anggara - Flaticon</a>

<a href="https://www.flaticon.com/free-icons/previous" title="previous icons">Previous icons created by Anggara - Flaticon</a>

<a href="https://www.flaticon.com/free-icons/arrow" title="arrow icons">Arrow icons created by Kirill Kazachek - Flaticon</a>
