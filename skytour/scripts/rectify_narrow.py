import os
GOOD_NAMES = '../IMG_NARROW.txt'
MEDIA_DIR = '../media/dso_finder_narrow'

def do_dsos(lines):
    fns = []
    for l in lines:
        pk, fnraw = l.split('\t')
        fn = fnraw.split('/')[-1]
        fns.append(fn)
    return fns

def filter_files(dso_lines, all_files, debug=False):
    n_start = len(all_files)
    if debug:
        print(f"Starting with {n_start} files")
    for l in dso_lines:
        pk, fnraw = l.split('\t')
        fn = fnraw.split('/')[-1]
        if fn in all_files:
            all_files.remove(fn)
    n_finish = len(all_files)
    if debug:
        print(f"Now I have {n_finish} files")
    diff = n_start - n_finish
    if debug:
        print(f"Removed {diff} files for {len(dso_lines)} DSOs")
    return all_files

def create_remove_list(file_list):
    for f in file_list:
        print(f"rm {MEDIA_DIR}/{f}")

if __name__ == '__main__':
    debug = False
    all_files = os.listdir(MEDIA_DIR)
    with open(GOOD_NAMES, 'r') as f:
        lines = [line.rstrip() for line in f]
    new = filter_files(lines, all_files, debug=debug)
    if not debug:
        create_remove_list(new)
