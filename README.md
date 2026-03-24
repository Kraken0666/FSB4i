# FSB4inspector (FSB4i)
FSB4inspector is a Python utility library for inspecting, analyzing, and manipulating FMOD SoundBank V4 (FSB4) files. The library is designed to simplify common workflows with FSB4 files, reducing repetitive and time-consuming tasks for developers and audio engineers.
## Roadmap
### Parse FSB4
#### Information
- [x] Parse FSB4 header  
- [x] Parse directory entries
- [x] Parse multiple directory entries
- [x] Parse SYNC header
- [x] Extract syncpoints frame offset
#### Data
- [ ] Extract MPEG frames to valid MP3
- [ ] Extract multi-channel MPEG frames to valid MP3(s)

### Create FSB4
#### Information
- [ ] Create FSB4 header
- [ ] Create directory entry
- [ ] Create multiple directory entries
- [ ] Create SYNC header
- [ ] Create syncpoints
#### Data
- [ ] Import WAV/MP3
### Tested with:
- a_fifth_of_beethoven.fsb (LBP2)
- i_english_g.fsb (LBP1) (Non-standard syncpoints)
- i_english_s.fsb (LBP1)


### Note: This was designed for LittleBigPlanet, it should work with non-LittleBigPlanet FSB4 files, but YMMV.