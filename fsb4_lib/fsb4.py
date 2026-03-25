import struct
import uuid
from structs.fsb4 import FSB4Header, FSB4DirectoryEntry
from config.constants import FSB4_HEADER_FORMAT, FSB4_HEADER_SIZE
from config.flags import FSOUND_FLAGS, FMOD_FSB_HEADER

''' More information on the format can be found at
https://wiki.imagisphere.me/Filetype:FMOD_Soundbank
'''

class FSB4Data(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.header: FSB4Header | None = None
        self.directory: list[FSB4DirectoryEntry] = []
    
    def decode_FSOUND_FLAGS(self, value: int):
        flags_set = FSOUND_FLAGS(value)
        return [flag.name for flag in FSOUND_FLAGS if flag in flags_set]

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

 
            flags_set = FMOD_FSB_HEADER(header.flags)
            readable_flags = [flag.name for flag in FMOD_FSB_HEADER if flag in flags_set]

            print("[+] Parsed FSB4Header:")
            print(f"        Magic:       {header.magic}")
            print(f"        Num Files:   {header.num_files}")
            print(f"        Dir Length:  {header.dir_len}")
            print(f"        Data Length: {header.dat_len}")
            print(f"        Version:     {header.version}")
            print(f"        Flags (RAW): 0x{header.flags:08X}")
            print(f"        Flags (Readable): {readable_flags}")
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

                flags = self.decode_FSOUND_FLAGS(entry.play_mode)
                print(f"        Filename: {entry.filename}")
                print(f"        Sample length: {entry.sample_len}")
                print(f"        Compressed length: {entry.compressed_len}")
                print(f"        Loop start: {entry.loop_start}")
                print(f"        Loop end: {entry.loop_end}")
                print(f"        Play mode (RAW): 0x{entry.play_mode:08X}")
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

                
                print(f"[{i}]   Frame: {startpoint_samples} ({minutes}:{seconds:02d}.{millis:03d})")

                startpoints.append({
                    "label": label,
                    "samples": startpoint_samples,
                    "time_seconds": time_sec
                })

        return startpoints
        
