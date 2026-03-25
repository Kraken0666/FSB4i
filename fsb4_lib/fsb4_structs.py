from dataclasses import dataclass

@dataclass(frozen=True)
class FSB4Header:
    magic: str
    num_files: int
    dir_len: int
    dat_len: int
    version: int
    flags: int
    reserved: int
    bank_uuid: bytes

@dataclass(frozen=True)
class FSB4DirectoryEntry:
    entry_len: int 
    filename: str
    sample_len: int
    compressed_len: int
    loop_start: int
    loop_end: int
    play_mode: int
    sample_rate: int
    bank_volume: int
    pan: int
    playback_priority: int
    num_channels: int
    min_distance: int
    max_distance: int
    var_freq: int
    var_vol: int
    var_pan: int