import os
import sys
import getopt
import threading
import subprocess

def usage():
    usage_documentation = """
    File Verification and Modfication Tool
    Usage: file_mod.py 

    -i --input=input_directory          -   input directory path
    -t --target=target_directory        -   target directory path
    -m --md5                            -   verify md5 checksums
    -n --dry-run                        -   dry run, no actual changes
    """

    print(usage_documentation)
    sys.exit(0)
