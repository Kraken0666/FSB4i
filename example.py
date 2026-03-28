from fsb4_lib import FSB4Data, decode_flags, format_time

# Load an FSB4 soundbank
bank = FSB4Data("tests/a_fifth_of_beethoven.fsb")

# Extract header
header = bank.get_header()
print("\nFSB4 Header:")
print(f"Magic: {header.magic}")
print(f"Number of samples: {header.num_files}")
print(f"Version: {header.version}")
print(f"Flags: {decode_flags(header.flags, "header")}")
print(f"Bank UUID: {header.bank_uuid.hex()}")

# Extract samples / directory
samples = bank.get_samples()
print("\nSamples:")
for s in samples:
    print(
        f"{s.filename} | Sample rate: {s.sample_rate} Hz | Channels: {s.num_channels} | Length: {format_time(s.sample_len, s.sample_rate)}"
    )

# Extract syncpoints
syncpoints = bank.get_syncpoints()
print("\nSyncpoints:")
for sp in syncpoints:
    print(f"{sp['label']} @ {sp['time_formatted']} (Sample: {sp['sample_offset']})"
          )
