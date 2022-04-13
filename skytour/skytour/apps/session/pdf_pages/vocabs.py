from reportlab.rl_config import defaultPageSize

PLANET_LIST = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
P_START = [670, 580, 490, 400, 310, 220, 130, 40]

PDICT = {
    'Mercury': dict(y0=670, xp=240, yp=580),
    'Venus':   dict(y0=580, xp=420, yp=580),
    'Mars':    dict(y0=490, xp=240, yp=390),
    'Jupiter': dict(y0=400, xp=420, yp=390),
    'Saturn':  dict(y0=310, xp=240, yp=200),
    'Uranus':  dict(y0=220, xp=420, yp=200),
    'Neptune': dict(y0=130, xp=240, yp=20)
}

PAGE_WIDTH = defaultPageSize[0]
PAGE_HEIGHT = defaultPageSize[1]
