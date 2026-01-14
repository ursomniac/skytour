from ..models import BrightStar
NOTES_FILE = 'seed_data/BSC/bsc5.notes'

# 0. get data
def import_notes_file():
    with open(NOTES_FILE, 'r') as f:
        lines = [line.rstrip() for line in f]
    f.close()
    return lines

# 1. structure data
def create_hash(lines):
    d = {} # key = HR, val = [ note = { category, text }]
    for line in lines:
        hr, seq, category, remark = decrypt_note(line)
        if hr not in d.keys():
            d[hr] = {}
        if category not in d[hr].keys():
            d[hr][category] = [] # list of records
        d[hr][category].append(remark)
    return d

# 2. decrypt record
def decrypt_note(line):
    hr_id = line[1:5]
    seq = line[5:7]
    craw = line[7:11]
    category = craw.replace(':','').rstrip()
    remark = line[12:]
    return (int(hr_id), int(seq), category, remark)


def process(debug=False):
    stars = BrightStar.objects.all()
    note_lines = import_notes_file()
    data = create_hash(note_lines)

    for hr in data.keys():
        star = stars.filter(hr_id=hr).first()
        if star is None: # these are the supernovae and DSOs like 47 Tuc listed as stars...
            continue
        star.texts.bsc_notes = data[hr]
        if debug:
            print(f"HR {hr}: Saving {str(data[hr].keys())}")
        star.texts.save()

