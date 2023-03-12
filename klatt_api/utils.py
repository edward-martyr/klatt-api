import io

import numpy as np
import numpy.typing as npt
from parselmouth import Data as PraatData, Sound
from parselmouth.praat import call as praat_call  # type: ignore
from scipy.io.wavfile import write

Real = float | int


class KlattGrid(PraatData):
    ...


def create_klattgrid(
    vowel_name: str = "V",
    duration: Real | None = None,
    pitch: Real | None = None,
    f1: Real | None = None,
    b1: Real | None = None,
    f2: Real | None = None,
    b2: Real | None = None,
    f3: Real | None = None,
    b3: Real | None = None,
    f4: Real | None = None,
    bandwidth_fraction: Real | None = None,
    formant_frequency_interval: Real | None = None,
) -> KlattGrid:
    """
    Creates a Praat KlattGrid from a vowel.
    """

    vowel_name = vowel_name if vowel_name is not None else "V"
    duration = duration if duration is not None else 0.5
    pitch = pitch if pitch is not None else 120
    f1 = f1 if f1 is not None else 800
    b1 = b1 if b1 is not None else 50
    f2 = f2 if f2 is not None else 1200
    b2 = b2 if b2 is not None else 50
    f3 = f3 if f3 is not None else 2300
    b3 = b3 if b3 is not None else 100
    f4 = f4 if f4 is not None else 3000
    bandwidth_fraction = bandwidth_fraction if bandwidth_fraction is not None else 0.05
    formant_frequency_interval = (
        formant_frequency_interval if formant_frequency_interval is not None else 1000
    )

    klatt_grid = praat_call(
        "Create KlattGrid from vowel",
        vowel_name,
        duration,
        pitch,
        f1,
        b1,
        f2,
        b2,
        f3,
        b3,
        f4,
        bandwidth_fraction,
        formant_frequency_interval,
    )
    return klatt_grid


def klattgrid_to_sound(klatt_grid: KlattGrid) -> Sound:
    """
    Creates a Praat Sound from a Praat KlattGrid.
    """

    sound = praat_call(klatt_grid, "To Sound")
    return sound


def sound_to_array(sound: Sound) -> npt.NDArray[np.float64]:
    """
    Creates a list of floats from a Praat Sound.
    """

    sound_matrix = praat_call(sound, "Down to Matrix")
    return sound_matrix.as_array()[0]


def array_to_wav(array: npt.NDArray[np.float64], sample_rate: int = 44100) -> bytes:
    """
    Creates a WAV file from a list of floats.
    """

    scaled = np.int16(array / np.max(np.abs(array)) * 32768)

    wav_bytes = io.BytesIO()
    write(wav_bytes, sample_rate, scaled)
    wav_bytes.seek(0)
    return wav_bytes.read()
