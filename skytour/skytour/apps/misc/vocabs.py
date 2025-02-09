
REFERENCE_MODEL_CHOICES = [
    ('Planet', 'Planet'),
    ('DSO', 'DSO'),
    ('Asteroid', 'Asteroid'),
    ('Moon', 'Moon'),
    ('Sun', 'Sun'),
    ('Comet', 'Comet'),
    ('Star', 'Star'),
]

TIME_ZONES = {
    '+00:00': {'zone_list': [
        ('UTC', 'Universal Coordinated Time'),
        ('GMT', 'Greenwich Mean Time')
    ], 'value':  0.0 },
    '+01:00': {'zone_list': [
        ('ETC', 'European Central Time')
    ], 'value':  1.0 },
    '+02:00': {'zone_list': [
        ('EET', 'Eastern European Time'),
        ('ART', '(Arabic) Egypt Standard Time')
    ], 'value':  2.0 },
    '+03:00': {'zone_list': [
        ('EAT', 'Eastern Arfican Time')
    ], 'value':  3.0 },
    '+03:30': {'zone_list': [
        ('MET', 'Middle East Time')
    ], 'value':  3.5 },
    '+04:00': {'zone_list': [
        ('NET', 'Near East Time')
    ], 'value':  4.0 },
    '+05:00': {'zone_list': [
        ('PLT', 'Pakistani Lahore Time')
    ], 'value':  5.0 },
    '+05:30': {'zone_list': [
        ('IST', 'India Standard Time')
    ], 'value':  5.5 },
    '+06:00': {'zone_list': [
        ('BST', 'Bangladesh Standard Time')
    ], 'value':  6.0 },
    '+07:00': {'zone_list': [
        ('VST', 'Vietnam Standard Time')
    ], 'value':  7.0 },
    '+08:00': {'zone_list': [
        ('CTT', 'China Taiwan Time')
    ], 'value':  8.0 },
    '+09:00': {'zone_list': [
        ('JST', 'Japan Standard Time')
    ], 'value':  9.0 },
    '+09:30': {'zone_list': [
        ('ACT', 'Australia Central Time')
    ], 'value':  9.5 },
    '+10:00': {'zone_list': [
        ('AET', 'Australia Eastern Time')
    ], 'value': 10.0 },
    '+11:00': {'zone_list': [
        ('SST', 'Solomon Standard Time')
    ], 'value': 11.0 },
    '+12:00': {'zone_list': [
        ('FST', 'Fiji Standard Time'),
        ('NST', 'New Zealand Standard Time')
    ], 'value': 12.0 },
    '-11:00': {'zone_list': [
        ('MIT', 'Midway Islands Time')
    ], 'value':-11.0 },
    '-10:00': {'zone_list': [
        ('HST', 'Hawaii Standard Time')
    ], 'value':-10.0 },
    '-09:00': {'zone_list': [
        ('AST', 'Alaska Standard Time')
    ], 'value': -9.0 },
    '-08:00': {'zone_list': [
        ('PST', 'Pacific Standard Time')
    ], 'value': -8.0 },
    '-07:00': {'zone_list': [
        ('MST', 'Mountain Standard Time'),
    ], 'value': -7.0 },
    '-06:00': {'zone_list': [
        ('CST', 'Central Standard Time')
    ], 'value': -6.0 },
    '-05:00': {'zone_list': [
        ('EST', 'Eastern Standard Time')
    ], 'value': -5.0 },
    '-04:00': {'zone_list': [
        ('PRT', 'Puerto Rico and US Virgin Islands Time')
    ], 'value': -4.0 },
    '-03:30': {'zone_list': [
        ('CNT', 'Canada Newfoundland Time')
    ], 'value': -3.5 },
    '-03:00': {'zone_list': [
        ('BET', 'Brazil Eastern Time'),
        ('AGT', 'Argentina Standard Time')
    ], 'value': -3.0 },
    '-02:00': {'zone_list': [
        ('MAT', 'Mid-Atlantic Standard Time')
    ], 'value': -2.0 },
    '-01:00': {'zone_list': [
        ('CAT', 'Central African Time')
    ], 'value': -1.0 },
}