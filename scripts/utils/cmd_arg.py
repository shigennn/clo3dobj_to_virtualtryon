import sys
from argparse import ArgumentParser
from typing import Optional, List

ARGS = '--export_exts'
HELP = 'help'

def get_cmd_export_exts() -> Optional[List[str]]:
    parser = ArgumentParser()
    parser.add_argument(ARGS, default= None ,nargs="*", help=HELP, required= False)

    try:
        args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
        export_exts = args.export_exts

    except ValueError:
        export_exts = None

    return export_exts