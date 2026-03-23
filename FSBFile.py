import struct
import uuid
from dataclasses import dataclass

''' More information on the format can be found at
https://wiki.imagisphere.me/Filetype:FMOD_Soundbank
'''

FSB4_HEADER_FORMAT = "<4s5IQ16s"
FSB4_HEADER_SIZE = struct.calcsize(FSB4_HEADER_FORMAT)

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

class FSB4Data(object):
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.header: FSB4Header | None = None

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
                version=unpacked[4],
                flags=unpacked[5],
                reserved=unpacked[6],
                bank_uuid=unpacked[7],
            )

            print(f"[+] Parsed FSB4Header: {header}")

            if header.magic != "FSB4":
                raise ValueError(f"[!] Not a valid FSB4 file, found magic: {header.magic}")

            self.header = header
            return header


    def extract_sample_info(self):
        return None

    def extract_fsb4_syncpoints(self):
        return None


if __name__ == "__main__":
    from sys import argv

    fsb = FSB4Data("a_fifth_of_beethoven.fsb") #Testing file


    fsb.extract_fsb4_header()
