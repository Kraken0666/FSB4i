from .fsb4_flags import FSOUND_FLAGS, FMOD_FSB_HEADER


def decode_flags(value: int, flag_type: str = "sound"):
    if flag_type == "header":
        enum_cls = FMOD_FSB_HEADER
    elif flag_type == "sound":
        enum_cls = FSOUND_FLAGS
    else:
        raise ValueError(f"Unknown flag_type: {flag_type}")

    flags_set = enum_cls(value)
    return [flag.name for flag in enum_cls if flag in flags_set]


def format_time(samples: int, sample_rate: int, formatted: bool = True):
    """Convert samples to time. Returns formatted string or tuple."""
    time_sec = samples / sample_rate
    minutes = int(time_sec // 60)
    seconds = int(time_sec % 60)
    millis = int((time_sec - int(time_sec)) * 1000)
    if formatted:
        return f"{minutes}:{seconds:02d}.{millis:03d}"
    return minutes, seconds, millis, time_sec
