from .fsb4_flags import FSOUND_FLAGS

def decode_FSOUND_FLAGS(value: int):
    flags_set = FSOUND_FLAGS(value)
    return [flag.name for flag in FSOUND_FLAGS if flag in flags_set]


def format_time(samples: int, sample_rate: float = 44100.0):
    """Convert samples to minutes, seconds, milliseconds."""
    time_sec = samples / sample_rate
    minutes = int(time_sec // 60)
    seconds = int(time_sec % 60)
    millis = int((time_sec - int(time_sec)) * 1000)
    return minutes, seconds, millis, time_sec