
PLANET_DICT  = {
    'Mercury': {
        'target': 'Mercury Barycenter', 
        'load': None,
        'moon_list': None,
        'diameter': 4_879,
        'mag_au': -0.42
    },
    'Venus': {
        'target': 'Venus Barycenter', 
        'load': None,
        'moon_list': None,
        'diameter': 12_104,
        'mag_au': -4.40,
    },
    'Mars': {
        'target': 'Mars Barycenter', 
        'load': 'mar_excerpt.bsp',
        'moon_list': ['Phobos', 'Deimos'],
        'diameter': 6_792,
        'mag_au': -1.52,
    },
    'Jupiter': {
        'target': 'Jupiter Barycenter', 
        'load': 'jup_excerpt.bsp',
        'moon_list': ['Io', 'Europa', 'Ganymede', 'Callisto'],
        'diameter': 142_984,
        'mag_au': -9.40,
    },
    'Saturn': {
        'target': 'Saturn Barycenter', 
        'load': 'sat_excerpt.bsp',
        'moon_list': ['Mimas', 'Enceladus', 'Tethys', 'Dione', 'Rhea', 'Titan', 'Iapetus'],
        'diameter': 120_536,
        'mag_au': -8.88
    },
    'Uranus': {
        'target': 'Uranus Barycenter',
        'load': 'ura_excerpt.bsp',
        'moon_list': ['Oberon', 'Titania'],
        'diameter': 51_118,
        'mag_au': -7.19
    },
    'Neptune': {
        'target': 'Neptune Barycenter',
        'load': 'nep_excerpt.bsp',
        'moon_list': ['Triton'],
        'diameter': 49_526,
        'mag_au': -6.87
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