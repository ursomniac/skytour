PLANETS = ['Mercury', 'Venus', 'Mars', 'Jupiter','Saturn', 'Uranus', 'Neptune']
PLANETS_8 = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
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

STATUS_CHOICES = [
    (1, 'On'),
    (0, 'Off')
]

BACKGROUND_CHOICES = [
    ('wob', 'White on Black'),
    ('bow', 'Black on White')
]

ZODIAC = [
    ('Aries',        15, '\u2648'),
    ('Taurus',       45, '\u2649'),
    ('Gemini',       75, '\u264A'),
    ('Cancer',      105, '\u264B'),
    ('Leo',         135, '\u264C'),
    ('Virgo',       165, '\u264D'),
    ('Libra',       195, '\u264E'),
    ('Scorpius',    225, '\u264F'),
    ('Sagittarius', 255, '\u2650'),
    ('Capricornus', 285, '\u2651'),
    ('Aquarius',    315, '\u2652'),
    ('Pisces',      345, '\u2653')
]

PLANET_COLORS = {
    'Mercury': 'grey',
    'Venus': 'orange', 
    'Earth': 'blue', 
    'Mars': 'red', 
    'Jupiter': 'pink', 
    'Saturn': 'brown', 
    'Uranus': 'lime', 
    'Neptune': 'cyan'
}
