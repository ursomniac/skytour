
OBSERVING_MODE_TYPES = [
    ('N', 'Naked Eye'),
    ('B', 'Binoculars'),
    ('S', 'Small Scope'),
    ('M', 'Medium Scope'),
    ('I', 'Imaging Scope')
]

STATUS_CHOICES = [
    (-9, 'Removed'),
    (0, 'Offline'),
    (1, 'Active')
]

MODE_VIABILITY_CHOICES = [
    (0, 'Not Viable'),          # typically set as a redetermination
    (1, 'Unlikely Viable'),     # experienced observers, great conditions, with luck
    (2, 'Extreme Difficulty'),  # experienced observers, great conditions
    (3, '(Very) Difficult'),    # experienced observers
    (4, 'Challenging'),         # generally requires great conditions
    (5, 'Requires Patience'),   # feasible but not particularly easy most of the time
    (6, 'Generally Visible'),   # feasible under decent conditions
    (7, 'Usually Easy'),        # feasible most of the time
    (8, 'Easy'),                # easy to find
    (9, 'Very Easy'),           # very easy to find
    (10, 'Extremely easy')      # even inexperienced observers have no problem
    # Typically the values will be 0, 2, 4/5, 8, 10
    # color scale:
    # 0 = black, 
    # 1-3: brown, red, orange
    # 4-6: yellow, chartreuse, green
    # 7-9: cyan, blue, purple
    # 10: white
]

VIABILITY_BACKGROUND_COLORS = [
    '#000', '#630', '#C00', '#F90', '#CC0', '#9C0', '#0A0', '#0CC', '#33C', '#90F', '#FFF'
]
VIABILITY_FOREGROUND_COLORS = [
    '#fff', '#fff', '#fff', '#000', '#000', '#000', '#000', '#000', '#fff', '#fff', '#000'
]

MODE_PRIORITY_CHOICES = [
    (0, 'Lowest'),
    (1, 'Low'),
    (2, 'Medium'),
    (3, 'High'),
    (4, 'Highest')
]

ISSUES_FLAGS = {
    # Not used in the model field, quick lookup
    'd': "Dim",
    's': "Small"
}