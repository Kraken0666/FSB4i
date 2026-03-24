import struct
import uuid
from dataclasses import dataclass

''' More information on the format can be found at
https://wiki.imagisphere.me/Filetype:FMOD_Soundbank
'''

FSB4_HEADER_FORMAT = "<4s5IQ16s"
FSB4_HEADER_SIZE = struct.calcsize(FSB4_HEADER_FORMAT)

FMOD_PLAY_FLAGS = {
    0x00000001: "FMOD_LOOP_OFF",
    0x00000002: "FMOD_LOOP_NORMAL",
    0x00000004: "FMOD_LOOP_BIDI",
    0x00000008: "FMOD_2D",
    0x00000010: "FMOD_3D",
    0x00000080: "FMOD_CREATESTREAM",
    0x00000100: "FMOD_CREATESAMPLE",
    0x00000200: "FMOD_CREATECOMPRESSEDSAMPLE",
    0x00000400: "FMOD_OPENUSER",
    0x00000800: "FMOD_OPENMEMORY",
    0x00001000: "FMOD_OPENRAW",
    0x00002000: "FMOD_OPENONLY",
    0x00004000: "FMOD_ACCURATETIME",
    0x00008000: "FMOD_MPEGSEARCH",
    0x00010000: "FMOD_NONBLOCKING",
    0x00020000: "FMOD_UNIQUE",
    0x00040000: "FMOD_3D_HEADRELATIVE",
    0x00080000: "FMOD_3D_WORLDRELATIVE",
    0x00100000: "FMOD_3D_INVERSEROLLOFF",
    0x00200000: "FMOD_3D_LINEARROLLOFF",
    0x00400000: "FMOD_3D_LINEARSQUAREROLLOFF",
    0x00800000: "FMOD_3D_INVERSETAPEREDROLLOFF",
    0x02000000: "FMOD_IGNORETAGS",
    0x04000000: "FMOD_3D_CUSTOMROLLOFF",
    0x08000000: "FMOD_LOWMEM",
    0x10000000: "FMOD_OPENMEMORY_POINT",
    0x20000000: "FMOD_LOADSECONDARYRAM",
    0x40000000: "FMOD_3D_IGNOREGEOMETRY",
    0x80000000: "FMOD_VIRTUAL_PLAYFROMSTART",}


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

class FSB4Data(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.header: FSB4Header | None = None
        self.directory: list[FSB4DirectoryEntry] = []
    
    def decode_fmod_play_flags(self, value: int):
        return [name for bit, name in FMOD_PLAY_FLAGS.items() if value & bit]

    def extract_fsb4_header(self):
        print(f"[+] Opening file: {self.filename}")
        with open(self.filename, 'rb') as f:
            fsb4_header_bytes = f.read(FSB4_HEADER_SIZE)
            print(f"[+] Read {len(fsb4_header_bytes)} bytes (expected {FSB4_HEADER_SIZE})")

            if len(fsb4_header_bytes) != FSB4_HEADER_SIZE:
                raise EOFError("[!] Not a valid FSB4 file")

            unpacked = struct.unpack(FSB4_HEADER_FORMAT, fsb4_header_bytes)

            header = FSB4Header(
                magic=unpacked[0].decode('ascii'),
                num_files=unpacked[1],
                dir_len=unpacked[2],
                dat_len=unpacked[3],
                version=(unpacked[4] >> 16),
                flags=unpacked[5],
                reserved=unpacked[6],
                bank_uuid=unpacked[7],
                )

            print("[+] Parsed FSB4Header:")
            print(f"        Magic:       {header.magic}")
            print(f"        Num Files:   {header.num_files}")
            print(f"        Dir Length:  {header.dir_len}")
            print(f"        Data Length: {header.dat_len}")
            print(f"        Version:     {header.version}")
            print(f"        Flags:       0x{header.flags:08X}")
            print(f"        Bank UUID:   {uuid.UUID(bytes=header.bank_uuid)}")


            if header.magic != "FSB4":
                raise ValueError(f"[!] Not a valid FSB4 file, found magic: {header.magic}")

            self.header = header
            return header
    
    def extract_directory(self):
        if not self.header:
            raise ValueError("[!] Header not extracted yet.")

        print("[*] Extracting FSB4 directory entries...")
        self.directory = []

        with open(self.filename, 'rb') as f:
            f.seek(0x30)
            for i in range(self.header.num_files):
                entry_len_bytes = f.read(2)
                if len(entry_len_bytes) != 2:
                    raise EOFError(f"[!] Unexpected EOF reading entry length for entry {i}")

                entry_len = struct.unpack("<H", entry_len_bytes)[0]
                print(f"[>] Entry {i+1}/{self.header.num_files}: entry_len = {entry_len}")
                
                entry_bytes = f.read(entry_len - 2)
                if len(entry_bytes) != entry_len - 2:
                    raise EOFError(f"[!] Unexpected EOF reading entry {i}")

                entry_fmt = "<30sIIIIIIHHHHIIIHH"
                fixed_entry_bytes = entry_bytes[:78]
                unpacked = struct.unpack(entry_fmt, fixed_entry_bytes)

                filename = unpacked[0].split(b'\x00', 1)[0].decode('utf-8', errors='ignore')

                entry = FSB4DirectoryEntry(
                    entry_len=entry_len,
                    filename=filename,
                    sample_len=unpacked[1],
                    compressed_len=unpacked[2],
                    loop_start=unpacked[3],
                    loop_end=unpacked[4],
                    play_mode=unpacked[5],
                    sample_rate=unpacked[6],
                    bank_volume=unpacked[7],
                    pan=unpacked[8],
                    playback_priority=unpacked[9],
                    num_channels=unpacked[10],
                    min_distance=unpacked[11],
                    max_distance=unpacked[12],
                    var_freq=unpacked[13],
                    var_vol=unpacked[14],
                    var_pan=unpacked[15],
                )

                self.directory.append(entry)

                flags = self.decode_fmod_play_flags(entry.play_mode)
                print(f"        Filename: {entry.filename}")
                print(f"        Sample length: {entry.sample_len}")
                print(f"        Compressed length: {entry.compressed_len}")
                print(f"        Loop start: {entry.loop_start}")
                print(f"        Loop end: {entry.loop_end}")
                print(f"        Play mode (Bitmask): 0x{entry.play_mode:08X}")
                print(f"        Play mode (Readable): {flags}")
                print(f"        Sample rate: {entry.sample_rate}")
                print(f"        Bank volume: {entry.bank_volume}")
                print(f"        Pan: {entry.pan}")
                print(f"        Playback priority: {entry.playback_priority}")
                print(f"        Num channels: {entry.num_channels}")

        print("[*] Directory extraction complete. Total entries:", len(self.directory))
        return self.directory

    def extract_fsb4_syncpoints(self):
        print(f"[+] Extracting FSB4 syncpoints from: {self.filename}")

        with open(self.filename, 'rb') as f:
            f.seek(0x80)
            header_bytes = f.read(8)
            if len(header_bytes) != 8:
                raise EOFError("[!] Could not read Startpoint header")

            magic, num_startpoint = struct.unpack("<4sI", header_bytes)
            magic = magic.decode("ascii")
            print(f"[+] SYNC Magic: {magic}")
            print(f"[+] Number of Startpoints: {num_startpoint}")

            if magic != "SYNC":
                raise ValueError(f"[!] Unexpected syncpoint magic: {magic}")

            sample_rate = 44100.0

            startpoints = []
            for i in range(num_startpoint):
                entry_bytes = f.read(260)
                if len(entry_bytes) != 260:
                    raise EOFError(f"[!] Could not read startpoint {i} entry")

                startpoint_samples, label_bytes, _padding = struct.unpack("<I10s246s", entry_bytes)
                label = label_bytes.decode("ascii").rstrip("\x00")

                # Convert samples to seconds
                time_sec = startpoint_samples / sample_rate
                minutes = int(time_sec // 60)
                seconds = int(time_sec % 60)
                millis = int((time_sec - int(time_sec)) * 1000)

                print(f"[+] Startpoint {i}: {label}")
                print(f"        Sample Position: {startpoint_samples}")
                print(f"        Time: {minutes}:{seconds:02d}.{millis:03d}")

                startpoints.append({
                    "label": label,
                    "samples": startpoint_samples,
                    "time_seconds": time_sec
                })

        return startpoints
if __name__ == "__main__":
    from sys import argv

    fsb = FSB4Data("a_fifth_of_beethoven.fsb") #Testing file


    fsb.extract_fsb4_header()
    fsb.extract_directory()
    fsb.extract_fsb4_syncpoints()
