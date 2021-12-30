DIAMETERS = {
    'Mercury':   4_879,
    'Venus':    12_104,
    'Mars':      6_792,
    'Jupiter': 142_984,
    'Saturn':  120_536,
    'Uranus':   51_118,
    'Neptune':  49_526,
    'Moon':      3_476
}


EPHEMERIS  = {
    'Mercury': {
        'p': 'Mercury Barycenter', 
        'l': None,
        's': None
    },
    'Venus': {
        'p': 'Venus Barycenter', 
        'l': None,
        's': None
    },
    'Mars': {
        'p': 'Mars Barycenter', 
        'l': 'mar_excerpt.bsp',
        's': ['Phobos', 'Deimos']
    },
    'Jupiter': {
        'p': 'Jupiter Barycenter', 
        'l': 'jup_excerpt.bsp',
        's': ['Io', 'Europa', 'Ganymede', 'Callisto']
    },
    'Saturn': {
        'p': 'Saturn Barycenter', 
        'l': 'sat_excerpt.bsp',
        's': ['Mimas', 'Enceladus', 'Tethys', 'Dione', 'Rhea', 'Titan', 'Iapetus']
    },
    'Uranus': {
        'p': 'Uranus Barycenter',
        'l': 'ura_excerpt.bsp',
        's': ['Oberon', 'Titania']
    },
    'Neptune': {
        'p': 'Neptune Barycenter',
        'l': 'nep_excerpt.bsp',
        's': ['Triton'] 
    }
}

UNICODE = {
    'Mercury': '\u263F', 'Venus': '\u2640', 'Earth': '\U0001F728', 'Mars': '\u2642', 
    'Jupiter': '\u2643','Saturn': '\u2644', 'Uranus': '\u26E2', 'Neptune': '\u2646', 
    'Pluto': '\u2647', 'Ceres': '\u26B3', 'Pallas': '\u26B4', 'Juno': '\u26B5',
    'Vesta': '\u26B6', 

    'Aries': '\u2648', 'Taurus': '\u2649', 'Gemini': '\u264A', 'Cancer': '\u264B',
    'Leo': '\u264C', 'Virgo': '\u264D', 'Libra': '\u264E', 'Scorpio': '\u264F',
    'Sagittarius': '\u2650', 'Capricorn': '\u2651', 'Aquarius': '\u2652', 'Pisces': '\u2653',
    'Ophiuchus': '\u26CE',
    'Sun': '\u2609', 'Moon': '\u263D'

}