from skytour.apps.stars.models import BrightStar

def tr(line, col, length, type):
    start = col-1
    end = col-1+length
    str = line[start:end]
    if str.isspace() or str == '':
        return None
    if type == 'int':
        return int(str)
    elif type == 'float':
        str.replace('+', ' ')
        return float(str)
    return str.strip()

def load_bsc():
    with open('seed_data/BSC/bsc5.dat') as f:
        lines = [line.rstrip() for line in f]
    f.close()
    return lines

def process():
    lines = load_bsc()
    for line in lines:
        hr_id = tr(line, 1, 4, 'int')
        star = BrightStar.objects.filter(hr_id=hr_id).first()
        if star is None:
            continue
        comp = tr(line, 50, 2, 'str')
        star.ads_components = comp
        star.save()