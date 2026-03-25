from fsb4_lib import FSB4Data

if __name__ == "__main__":
    from sys import argv

    fsb = FSB4Data("tests/a_fifth_of_beethoven.fsb") #Testing file


    fsb.extract_fsb4_header()
    fsb.extract_directory()
    fsb.extract_fsb4_syncpoints()