from skytour.apps.dso.models import DSO
from skytour.apps.dso.search import find_cat_id_in_string, search_dso_name

# This isn't expected to be used anymore.

TARGET_OBJECTS = {
    # Block 1
    'AND': [('M 31', 'N'),('C 28', 'B'), ('IC 239', 'I'), ('NGC 7640', 'I'),
            ('NGC 404', 'I'), ('C 22', 'S'), ('C 23', 'S')
            ], 
    'ANT': [('NGC 2997', 'I'), ('NGC 3223', 'I'), ('NGC 3268', 'I'), ('NGC 3175', 'I'),
            ('NGC 3095', 'M'), ('NGC 3137', 'I'), ('NGC 3001', 'M'), 
            ],
    'APS': [('IC 4499', 'S'), ('C 107', 'S'), ('IC 4633', 'I') ],
    'AQR': [('M 2', 'S'), ('M 72', 'M'), ('C 63', 'I'), ('C 55', 'M'), ('NGC 7184', 'M'),
            ('NGC 7721', 'I'), ('NGC 7492', 'M'), ('NGC 7309', 'I'), ('NGC 7284', 'I'),
            ('NGC 6962', 'I'), ('NGC 7727', 'M'), 
            ],
    'AQL': [('NGC 6781', 'M'), ('NGC 6755', 'S'), ('NGC 6751', 'M'), ('NGC 6709', 'S'),
            ('B 143', 'I'), ('NGC 6756', 'M'), ('NGC 7606', 'I'), ('M 73', 'S'),
            ('NGC 7723', 'I'), 
            ],
    'ARA': [('C 86', 'M'), ('C 82', 'I'), ('NGC 6326', 'M'), ('NGC 6215', 'I'),
            ('NGC 6253', 'M'), ('C 81', 'S'), ('NGC 6362', 'S'), ('NGC 6204', 'S'),
            ('NGC 6200', 'S'), ('NGC 6208', 'S'), ('IC 4651', 'S'), ('NGC 6164', 'S'),
            ('NGC 6250', 'B'), ('NGC 1156', 'M')
            ],
    'ARI': [('NGC 772', 'M'), ('NGC 935', 'I'), ('NGC 877', 'I'), ('NGC 697', 'I'),
            ('NGC 691', 'I'),
            ],
    'AUR': [('M 36', 'B'), ('M 37', 'B'), ('M 38', 'B'), ('NGC 1893', 'I'),
            ('C 31', 'I'), ('NGC 1931', 'I'), ('NGC 2281', 'S'), ('NGC 1664', 'B'),
            ('NGC 2192', 'M'),  ('NGC 1778', 'S'), ('IC 417', 'I'), ('IC 2149', 'M'),
            ('Sh2 235', 'I'), ('Sh2 226', 'I'), ('NGC 2126', 'M'), ('NGC 1907', 'S'),
            ('NGC 1857', 'S'), 
            ],
    # Block 2
    'BOO': [('C 45', 'I'), ('NGC 5529', 'M'), ('NGC 4731', 'I'), ('NGC 5466', 'S'),
            ('NGC 5859', 'I'), ('NGC 5676', 'I'), ('NGC 5660', 'I'), ('IC 1029', 'I'),
            ('NGC 5689', 'I'), 
            ],
    'CAE': [('NGC 1679', 'I')],
    'CAM': [('C 7', 'M'), ('C 5', 'I'), ('NGC 1502', 'B'), ('NGC 1501', 'M'),
            ('NGC 2146', 'M'), ('NGC 2336', 'I'), ('IC 3568', 'S'), ('NGC 1560', 'I'),
            ('NGC 1961', 'M'), ('NGC 2366', 'M'), ('NGC 2655', 'M'), ('NGC 2715', 'M'),
            ('UGC 3697', 'I'), ('NGC 2268', 'I'), ('IC 529', 'I'), ('IC 334', 'M'),
            ('NGC 2748', 'M'), ('NGC 2441', 'I'), ('IC 361', 'M')
            ],
    'CNC': [('M 44', 'B'), ('M 67', 'S'), ('C 48', 'M'), ('NGC 2563', 'I'),
            ('NGC 2535', 'I'),
            ],
    'CVN': [('M 106', 'S'), ('M 3', 'S'), ('M 51', 'S'), ('M 63', 'S'),
            ('M 94', 'S'), ('C 21', 'M'), ('C 26', 'S'), ('C 32', 'S'),
            ('NGC 4490', 'M'), ('NGC 4618', 'M'), ('NGC 4656', 'M'), ('NGC 5033', 'I'),
            ('NGC 5395', 'I'), ('C 29', 'I'), ('NGC 4111', 'M'), ('NGC 4145', 'I'),
            ('NGC 4151', 'I'), ('NGC 4217', 'I'), ('NGC 4228', 'M'), ('NGC 4242', 'I'),
            ('NGC 4395', 'M'), ('NGC 5353', 'M'), ('NGC 5371', 'I'), ('NGC 5383', 'I'),
            ('NGC 5396', 'I'), ('NGC 5378', 'I'), ('NGC 5377', 'M'), ('NGC 5297', 'I'),
            ('NGC 5112', 'I'), ('NGC 4389', 'I'), ('NGC 4369', 'M'), ('NGC 4346', 'M'),
            ],
    'CMA': [('M 41', 'B'), ('NGC 2207', 'M'), ('NGC 2359', 'I'), ('C 64', 'S'),
            ('Sh2 297', 'I'), ('C 58', 'S'), ('Cr 121', 'I'), ('NGC 2204', 'S'),
            ('NGC 2223', 'M'), ('NGC 2280', 'M'), ('NGC 2367', 'S'), ('NGC 2383', 'S'),
            ('Sh2 296', 'I'), ('NGC 2217', 'M'), ('NGC 2327', 'I'), ('NGC 2345', 'S'),
            ('NGC 2293', 'M'), ('NGC 2283', 'I'), ('Cr 140', 'B'), ('NGC 2243', 'S')
            ],
    'CMI': [],
    'CAP': [('NGC 6907', 'M'), ('M 30', 'M')],
    # Block 3
    'CAR': [('NGC 3576', 'I'), ('C 92', 'B'), ('C 102', 'B'), ('C 91', 'B'), 
            ('C 96', 'B'), ('NGC 3293', 'S'), ('NGC 3324', 'S'), ('NGC 3247', 'S'), 
            ('Cr 245', 'S'), ('C 90', 'M'), ('NGC 3059', 'M'), ('NGC 3211', 'M'),
            ('IC 2501', 'M'), ('IC 2448', 'M'), ('IC 2553', 'M'), ('NGC 3603', 'I'),
            ('NGC 3496', 'S'), ('Cr 227', 'S'), ('NGC 3519', 'S'), ('Cr 241', 'S'),
            ('NGC 3572', 'S'), ('NGC 2808', 'B'), ('Tr 14', 'S'), ('IC 2581', 'B'),
            ('NGC 3114', 'B')
            ],
    'CAS': [('NGC 129', 'S'), ('NGC 133', 'S'), ('NGC 7790', 'S'), ('NGC 7789', 'B'),
            ('NGC 659', 'S'), ('NGC 654', 'B'), ('M 103', 'B'), ('C 8', 'S'),
            ('C 11', 'I'), ('Sh2 157', 'I'), ('NGC 281', 'I'), ('NGC 225', 'B'),
            ('NGC 1027', 'B'), ('M 52', 'B'),  ('IC 63', 'I'), ('IC 1848', 'I'),
            ('IC 10', 'M'), ('C 18', 'M'), ('C 17', 'I'), ('C 13', 'B'),
            ('C 10', 'B'), ('IC 1805', 'I'), ('NGC 609', 'M'), ('NGC 189', 'S'),
            ('NGC 103', 'S'), ('Dwi 1', 'I'), ('Cr 463', 'B'), ('NGC 637', 'S'),
            ('NGC 436', 'S'), ('IC 1871', 'I'), 
            ],
    'CEN': [('NGC 5307', 'M'), ('ESO 172-7', 'M'), ('NGC 3918', 'M'), ('C 77', 'S'),
             ('NGC 5617', 'B'), ('NGC 5281', 'S'), ('NGC 5662', 'S'), ('C 80', 'N'),
            ('C 97', 'S'), ('C 100', 'S'), ('NGC 5298', 'I'), ('IC 4386', 'I'),
            ('NGC 4622', 'I'), ('NGC 5495', 'I'), ('NGC 5494', 'I'), ('NGC 4930', 'I'),
            ('NGC 4650', 'I'), ('NGC 4947', 'I'), ('NGC 4835', 'I'), ('IC 3253', 'M'),
            ('NGC 5090', 'M'), ('NGC 5419', 'M'), ('NGC 4219', 'M'), ('NGC 4603', 'M'),
            ('NGC 3699', 'M'), ('NGC 5161', 'M'), ('NGC 5253', 'M'), ('NGC 5460', 'B'), 
            ('NGC 4976', 'S'), ('C 83', 'S'), ('NGC 4852', 'S'), ('C 84', 'S'),
            ('NGC 5606', 'S'), ('NGC 5138', 'S'), ('NGC 3680', 'S'), ('NGC 5316', 'S'),
            ],
    'CEP': [('NGC 7160', 'S'), ('NGC 6939', 'S'), ('Sh2 132', 'I'), ('NGC 7538', 'I'),
            ('NGC 6951', 'M'), ('NGC 2276', 'I'), ('C 9', 'I'), ('C 2', 'S'),
            ('C 1', 'I'), ('Sh2 136', 'I'), ('NGC 7822', 'I'), ('NGC 7510', 'S'),
            ('NGC 7380', 'I'), ('NGC 7129', 'I'), ('IC 1396', 'I'), ('C 4', 'M'),
            ('NGC 7762', 'S'), ('NGC 7419', 'I'), ('NGC 7261', 'S'), ('NGC 7226', 'S'),
            ('NGC 1184', 'I'), ('IC 1470', 'M'), ('Sh2 140', 'I'), ('NGC 7142', 'S'), 
            ('Sh2 129', 'I'), 
            ],
    'CET': [('NGC 864', 'I'), ('WLM', '?'), ('NGC 578', 'M'), ('NGC 275', 'M'),
            ('C 51', 'I'), ('NGC 945', 'I'), ('NGC 936', 'I'), ('NGC 908', 'M'),
            ('NGC 45', 'M'), ('NGC 157', 'M'), ('NGC 1073', 'M'), ('NGC 1042', 'M'),
            ('M 77', 'M'), ('C 56', 'M'), ('NGC 1055', 'M'), ('C 62', 'M'),
            ('NGC 988', 'I'), ('NGC 955', 'I'), ('NGC 942', 'M'), ('NGC 894', 'M'),
            ('NGC 881', 'I'), ('NGC 720', 'M'), ('NGC 615', 'M'), ('NGC 596', 'M'),
            ('NGC 584', 'M'), ('NGC 541', 'I'), ('NGC 521', 'I'), ('NGC 337', 'M'),
            ('NGC 192', 'I'), ('NGC 1087', 'M'), ('NGC 1032', 'I'), ('NGC 1022', 'M'),
            ('NGC 779', 'M'), ('NGC 428', 'M'), ('NGC 210', 'M'), ('IC 127', 'S')
            ],
    'CHA': [('C 109', 'M'), ('IC 3104', 'I')],
    'CIR': [('C 88', 'S')],
    'COL': [('C 73', 'M'), ('NGC 1808', 'S'), ('NGC 1792', 'M'), ('NGC 2090', 'M')
            ],
    # Block 4
    'COM': [('C 35', 'I'), ('C 36', 'S'), ('C 38', 'S'), ('M 53', 'S'), 
            ('M 64', 'S'), ('M 85', 'S'), ('M 88', 'M'), ('M 91', 'M'),
            ('M 98', 'S'), ('M 99', 'S'), ('M 100', 'S'), ('Mel 111', 'N'), 
            ('NGC 4055', 'I'), ('NGC 4095', 'I'), ('NGC 4147', 'M'), ('NGC 4169', 'I'), 
            ('NGC 4185', 'I'), ('NGC 4189', 'M'), ('NGC 4237', 'I'), ('NGC 4274', 'M'), 
            ('NGC 4278', 'M'), ('NGC 4293', 'M'), ('NGC 4298', 'M'), ('NGC 4314', 'M'), 
            ('NGC 4350', 'M'), ('NGC 4414', 'M'), ('NGC 4419', 'M'), ('NGC 4450', 'M'), 
            ('NGC 4459', 'M'), ('NGC 4477', 'M'), ('NGC 4540', 'I'), ('NGC 4571', 'I'), 
            ('NGC 4634', 'I'), ('NGC 4651', 'M'), ('NGC 4689', 'M'), ('NGC 4710', 'M'), 
            ('NGC 4725', 'M'), ('NGC 4793', 'M'), ('NGC 4921', 'I'), ('NGC 5053', 'S'),
	        ],
    'CRA': [('C 68', 'I'), ('C 78', 'S')],
    'CRB': [],
    'CRV': [('C 60', 'M'), ('NGC 4027', 'M'), ('NGC 4050', 'M'), ('NGC 4094', 'I'),
            ('NGC 4361', 'M'),('NGC 4462', 'M'), ('NGC 4782', 'M'), 
            ],
    'CRT': [('NGC 3887', 'M'), ('NGC 3831', 'I'), ('NGC 3672', 'M'), ('NGC 3511', 'M'),
            ('NGC 3981', 'M'), ('NGC 3544', 'I'), ('NGC 3892', 'I'), ('IC 2627', 'I')
            ],
    'CRU': [('C 99', 'B'), ('C 94', 'B'), ('C 98', 'B'), ('NGC 4103', 'S'), 
            ('NGC 4349', 'S'), ('NGC 4439', 'S'), ('NGC 4052', 'S'), ('NGC 4337', 'S'),
            ('Cr 262', 'M')
            ],
    'CYG': [('NGC 6834', 'S'), ('Sh2 101', 'I'), ('NGC 7044', 'I'), ('NGC 7026', 'M'),
            ('NGC 7008', 'M'), ('NGC 6910', 'S'), ('NGC 6894', 'M'), ('NGC 6866', 'S'),
            ('NGC 6819', 'S'), ('NGC 6811', 'S'), ('M 39', 'B'), ('M 29', 'B'),
            ('NGC 6979', 'I'), ('C 33', 'I'), ('C 34', 'I'), ('IC 1318', 'I'),
            ('C 27', 'I'), ('C 19', 'I'), ('C 15', 'M'), ('C 20', 'I'),
            ('IC 1311', 'M'), ('NGC 7086', 'S'), ('NGC 7062', 'S'), ('NGC 7048', 'M'),
            ('NGC 7039', 'S'), ('NGC 6996', 'S'), ('NGC 6871', 'B'), ('C 12', 'S'),
            ('Cr 428', 'S'), ('Sh2 99', 'I'), ('Sh2 114', 'I'), ('Sh2 106', 'I'),
            ('NGC 7063', 'S'),('NGC 7027', 'M'), ('IC 5076', 'I'), 
            ],
    'DEL': [('NGC 7006', 'M'), ('C 47', 'M'), ('NGC 6891', 'M'), ('NGC 6905', 'M'),
            ('C 42','M')
            ],
    # Block 5
    'DOR': [('C 103', 'B'), ('NGC 1566', 'S'), ('NGC 1761', 'I')],
    'DRA': [('C 6', 'M'), ('NGC 5982', 'M'), (('NGC 5906', 'M')), ('M 102', 'M'),
            ('NGC 6503', 'M'), ('C 3', 'M'), ('NGC 5678', 'M'), ('NGC 5879', 'M'),
            ('NGC 3147', 'M'), ('NGC 6340', 'I'), ('NGC 6015', 'M'), ('NGC 6643', 'M'),
            ('NGC 6412', 'I'), ('NGC 3735', 'M'), ('NGC 5965', 'M'), ('NGC 6140', 'I'),
            ('PG 1634+706', 'I'), ('Arp 188', 'I'), ('NGC 6654', 'I'), ('NGC 3183', 'I'),
            ('NGC 5905', 'I'), ('NGC 4750', 'M'), ('NGC 4210', 'I'),  
            ],
    'EQU': [],
    'ERI': [('NGC 1232', 'M'), ('NGC 1300', 'M'), ('NGC 1187', 'M'), ('NGC 1535', 'M'),
            ('NGC 1084', 'M'), ('NGC 1253', 'I'), ('NGC 1337', 'I'), ('NGC 1353', 'I'),
            ('NGC 1452', 'I'), ('NGC 1179', 'I'), ('NGC 1325', 'I'), ('NGC 1376', 'I'),
            ('NGC 1532', 'S'), ('NGC 1909', 'I'), ('NGC 1269', 'S'), ('NGC 1637', 'M'),
            ('NGC 782', 'I'), ('NGC 685', 'I'), ('NGC 1487', 'M'), ('NGC 1620', 'I'),
            ('NGC 1600', 'S'), ('NGC 1518', 'M'), ('NGC 1507', 'I'), ('NGC 1421', 'I'),
            ('NGC 1415', 'I'), ('NGC 1400', 'S'), ('NGC 1359', 'I'), ('NGC 1357', 'I'),
            ('NGC 1332', 'S'), ('NGC 1324', 'I'), ('NGC 1241', 'I'), ('IC 1953', 'I'),
            ('NGC 1640', 'M'),  
            ],
    'FOR': [('NGC 1049', 'I'), ('NGC 1317', 'S'), ('NGC 1360', 'S'), ('NGC 1365', 'S'),
            ('NGC 1380', 'S'), ('C 67', 'S'), ('NGC 1398', 'M'), ('NGC 1350', 'M'),
            ('NGC 1255', 'M'), ('NGC 1385', 'M'), ('NGC 1302', 'M'), ('NGC 1425', 'M'),
            ('NGC 1406', 'M'), ('NGC 986', 'M'), ('NGC 1399', 'S'), ('NGC 1340', 'M'),
            ('NGC 1326', 'M'), ('NGC 1367', 'M'), ('NGC 1292', 'I'), ('NGC 1201', 'M'),
            ('NGC 1079', 'M'), ('IC 335', 'I'), ('IC 1993', 'I'), 
            ],
    'GEM': [('Sh2 274', 'I'), ('NGC 2355', 'M'), ('IC 2157', 'S'), ('NGC 2420', 'S'),
            ('NGC 2304', 'M'), ('NGC 2129', 'S'), ('IC 444', 'I'), ('IC 443', 'I'),
            ('NGC 2371', 'M'), ('NGC 2266', 'S'), ('NGC 2158', 'S'), ('M 35', 'S'),
            ('C 39', 'S'), ('Cr 89', 'B'), ('NGC 2395', 'S'), ('NGC 2331', 'S')
            ],
    'GRU': [('NGC 7424', 'M'), ('IC 5267', 'M'), ('NGC 7582', 'S'), ('IC 5148', 'M'),
            ('NGC 7418', 'M'), ('NGC 7410', 'M'), ('NGC 7456', 'M'), ('NGC 7307', 'I'),
            ('NGC 7213', 'I'), ('NGC 7462', 'M'), ('NGC 7421', 'M'), ('IC 5179', 'I'),
            ('IC 1459', 'M'), ('NGC 7232', 'M'), ('IC 5273', 'M'), ('IC 5201', 'M'),
            ('NGC 7412', 'M'), ('IC 5240', 'M'), ('NGC 7531', 'M'),
            ('NGC 7145', 'M'), ('NGC 7144', 'M'), ('NGC 7552', 'M')
            ],
    'HER': [('NGC 6229', 'S'), ('NGC 6210', 'S'), ('NGC 6241', 'I'), ('NGC 6047', 'I'),
            ('IC 4593', 'M'), ('NGC 6207', 'M'), ('M 92', 'S'), ('M 13', 'N')],
    # Block 6
    # up to here
    'HOR': [('IC 2000', 'I'), ('NGC 1484', 'I'), ('NGC 1448', 'I'), ('NGC 1512', 'S'),
            ('NGC 1433', 'S'), ('C 87', 'S'), ('NGC 1249', 'I'), ('IC 1954', 'I'),
            ('NGC 1493', 'I'), ('NGC 1527', 'M')
            ],
    'HYA': [('NGC 5042', 'I'), ('NGC 3200', 'I'), ('NGC 3124', 'I'), ('NGC 5556', 'I'),
            ('NGC 5101', 'M'), ('NGC 5085', 'M'), ('NGC 4304', 'I'), ('NGC 3673', 'I'),
            ('NGC 3621', 'S'), ('NGC 3450', 'M'), ('NGC 3311', 'M'), ('NGC 3109', 'M'),
            ('NGC 3054', 'I'), ('NGC 2935', 'M'), ('NGC 2835', 'M'), ('M 48', 'B'),
            ('C 66', 'S'), ('NGC 5078', 'M'), ('M 68', 'S'), ('C 59', 'S'),
            ('M 83', 'S'), ('NGC 5264', 'I'), ('NGC 5061', 'I'), ('NGC 4965', 'I'),
            ('NGC 4106', 'M'), ('NGC 3923', 'S'), ('NGC 3717', 'I'), ('NGC 3585', 'M'),
            ('NGC 3336', 'I'), ('NGC 3285', 'I'), ('NGC 2962', 'I'), ('NGC 2889', 'I'),
            ('NGC 2855', 'I'), ('NGC 2848', 'I'), ('NGC 2815', 'M'), ('NGC 2784', 'S'),
            ('NGC 2713', 'I'), ('NGC 2708', 'I'), ('NGC 2618', 'I'), ('IC 4351', 'I'),
            ],
    'HYI': [('NGC 1466', 'M'), ('NGC 1511', 'M'), ('NGC 1629', 'M')],
    'IND': [('NGC 7064', 'M'), ('NGC 7205', 'M'), ('IC 5152', 'M'), ('NGC 7090', 'M'),
            ('NGC 7038', 'M'), ('NGC 7125', 'I'), ('NGC 7124', 'I'), ('NGC 7041', 'M'),
            ('NGC 7083', 'M'), ('NGC 7049', 'M'), 
            ],
    'LAC': [('C 16', 'S'), ('NGC 7245', 'S'), ('NGC 7209', 'S'), ('NGC 7296', 'S'),
            ('IC 1442', 'S'), ('IC 1434', 'S'), 
            ],
    'LEO': [('NGC 4005', 'I'), ('NGC 3860', 'I'), ('NGC 3801', 'I'), ('NGC 3753', 'I'),
            ('NGC 3646', 'M'), ('NGC 3495', 'I'), ('NGC 3485', 'I'), ('NGC 3162', 'I'),
            ('NGC 2872', 'I'), ('UGC 5470', 'I'), ('NGC 3810', 'M'), ('NGC 3705', 'M'),
            ('NGC 3681', 'I'), ('NGC 3607', 'M'), ('NGC 3596', 'I'), ('NGC 3593', 'I'),
            ('NGC 3507', 'M'), ('NGC 3367', 'I'), ('NGC 3338', 'I'), ('M 105', 'S'),
            ('IRAS 09371+1212', 'M'), ('C 40', 'M'), ('NGC 3521', 'M'), ('NGC 3189', 'M'), 
            ('NGC 2964', 'M'), ('M 96', 'S'), ('M 95', 'S'), ('M 66', 'S'),
            ('M 65', 'S'), ('NGC 3628', 'S'), ('NGC 3226', 'M'), ('NGC 2903', 'S'),
            ('NGC 3370', 'I'), ('NGC 3666', 'I'), ('NGC 3412', 'S'), ('NGC 2916', 'I'),
            ('NGC 3640', 'S'), ('NGC 3377', 'S'), 
            ],
    'LMI': [('NGC 3504', 'M'), ('NGC 3430', 'I'), ('NGC 3003', 'I'), ('NGC 3486', 'S'),
            ('NGC 3254', 'M'), ('NGC 3294', 'M'), ('NGC 3395', 'I'), ('NGC 3432', 'M'),
            ('NGC 3344', 'S'), ('NGC 3381', 'I'),
            ],
    'LEP': [('NGC 1784', 'I'), ('NGC 1744', 'I'), ('IC 438', 'I'), ('IC 418', 'M'),
            ('NGC 1964', 'M'), ('NGC 1954', 'I'), ('M 79', 'S'), ('NGC 2196', 'I'),
             ('NGC 2139', 'I')
            ], 
    # Block 7
    'LIB': [('NGC 5878', 'I'), ('NGC 5861', 'I'), ('IC 4538', 'I'), ('NGC 5897', 'S'),
            ('NGC 5885', 'M'), ('NGC 5792', 'I'), ('NGC 5595', 'I'), ('NGC 5898', 'M'),
            ('NGC 5892', 'I')
            ],
    'LUP': [('IC 4402', 'I'), ('NGC 5688', 'I'), ('NGC 5530', 'M'), ('IC 4406', 'S'),
            ('NGC 5882', 'S'), ('NGC 5824', 'M'), ('NGC 5927', 'S'), ('NGC 5749', 'S'),
            ('NGC 5986', 'S'), ('NGC 5822', 'B'), ('IC 4444', 'M')
            ],
    'LYN': [('NGC 2782', 'I'), ('NGC 2776', 'M'), ('NGC 2552', 'I'), ('NGC 2543', 'I'),
            ('NGC 2541', 'I'), ('NGC 2770', 'I'), ('NGC 2683', 'S'), ('NGC 2537', 'I'),
            ('NGC 2500', 'M'), ('C 25', 'S'), ('NGC 2549', 'I'), ('NGC 2474', 'I'),
            ('IC 2166', 'I')
            ],
    'LYR': [('NGC 6791', 'S'), ('M 56', 'S'), ('M 57', 'S')],
    'MEN': [('NGC 2203', 'M'), ('NGC 1711', 'M'), ('NGC 2018', 'I'), ('NGC 2103', 'S'),
            ('NGC 2122', 'M'), ('NGC 1845', 'S'), ('NGC 1777', 'I'), ('IC 2146', 'I'),
            ('NGC 2121', 'I'), ('IC 2051', 'I'), ('NGC 1651', 'I'), ('NGC 1848', 'M'),
            ('NGC 2134', 'M'), 
            ],
    'MIC': [('NGC 6925', 'M'),],
    'MON': [('NGC 2286', 'S'), ('NGC 2269', 'S'), ('NGC 2185', 'I'), ('NGC 2182', 'S'),
            ('NGC 2149', 'I'), ('IC 448', 'I'), ('Sh2 294', 'I'), ('NGC 2343', 'S'),
            ('NGC 2335', 'S'), ('NGC 2282', 'I'), ('NGC 2232', 'B'), ('NGC 2215', 'B'),
            ('M 50', 'B'), ('IC 2177', 'M'), ('IC 2169', 'I'), ('C 54', 'S'),
            ('C 46', 'M'), ('NGC 2353', 'S'), ('NGC 2346', 'M'), ('NGC 2301', 'B'),
            ('NGC 2264', 'B'), ('NGC 2251', 'S'), ('NGC 2170', 'I'), ('C 50', 'B'),
            ('C 49', 'S'), ('NGC 2302', 'S'), ('NGC 2311', 'S'), ('NGC 2254', 'M'),
            ('NGC 2252', 'S'), ('NGC 2250', 'S'), ('NGC 2245', 'M'), ('NGC 2236', 'S'),
            ('IC 2167', 'M'), ('Cr 91', 'B'), ('Cr 106', 'B'), ('NGC 2324', 'S')
            ],
    'MUS': [('Sandqvist 149', 'I'), ('NGC 4463', 'S'), ('C 105', 'S'), ('NGC 4815', 'S'),
            ('C 108', 'S'), ('NGC 5189', 'M'), ('IC 4191', 'M')],
    # Block 8
    # UP TO HERE

    'NOR': [('C 89', 'B'), ('NGC 6067', 'S'), ('NGC 6169', 'S'), ('NGC 6167', 'S'),
            ('Cr 299', 'B'), ('NGC 6134', 'S'), ('NGC 6152', 'S'), ('NGC 5925', 'S'),
            ('NGC 6005', 'M'), 
            ],
    'OCT': [('NGC 6438', 'M'), ('NGC 7095', 'I'), ('NGC 7098', 'M') ],
    'OPH': [('B 262', 'I'), ('NGC 6355', 'S'), ('NGC 6316', 'M'), ('NGC 6309', 'M'),
            ('NGC 6287', 'M'), ('IC 4634', 'M'), ('NGC 6633', 'S'), ('NGC 6572', 'S'),
            ('NGC 6384', 'I'), ('NGC 6366', 'S'), ('NGC 6356', 'S'), ('M 62', 'S'),
            ('M 19', 'S'), ('M 107', 'S'), ('IC 4665', 'B'), ('IC 4604', 'I'),
            ('NGC 6369', 'M'), ('M 9', 'S'), ('M 14', 'S'), ('M 12', 'S'),
            ('M 10', 'S'), ('B 68', 'I'), ('B 64', 'I'), ('B 59', 'M'),
            ('NGC 6401', 'S'), ('B 65', 'M'), ('Cr 350', 'B'), ('IC 4603', 'M'),
            ('NGC 6235', 'S'), ('NGC 6284', 'S'), ('NGC 6325', 'M'), ('NGC 6342', 'M'),

            ],
    # Up to here
    'ORI': [('NGC 2186', 'S'), ('NGC 2022', 'M'), ('NGC 1662', 'S'), ('IC 432', 'M'),
            ('IC 421', 'I'), ('Sh2 261', 'I'), ('NGC 2194', 'S'), ('NGC 2112', 'S'),
            ('NGC 1981', 'B'), ('NGC 1980', 'B'), ('NGC 2174', 'M'), ('NGC 2169', 'S'),
            ('NGC 2024', 'M'), ('NGC 1999', 'M'), ('NGC 1977', 'S'), ('NGC 1788', 'M'),
            ('M 78', 'S'), ('M 43', 'S'), ('IC 2162', 'I'), ('M 42', 'N'),
            ('B 33', 'M')
            ],
    'PAV': [('IC 4721', 'I'), ('IC 5052', 'M'), ('NGC 6943', 'M'), ('C 101', 'S'),
            ('C 93', 'B'), 
            ],
    'PEG': [('UGC 12914', 'I'), ('NGC 7817', 'I'), ('NGC 7769', 'I'), ('NGC 7678', 'I'),
            ('NGC 7619', 'I'), ('NGC 7385', 'I'), ('PGC 69457', 'M'), ('NGC 7742', 'M'),
            ('NGC 7741', 'M'), ('NGC 7448', 'M'), ('NGC 7320', 'M'), ('M 15', 'B'),
            ('C 43', 'M'), ('C 30', 'S'), ('C 44', 'M')
            ],
    'PER': [('NGC 1624', 'M'), ('NGC 1545', 'S'), ('NGC 1528', 'S'), ('NGC 1513', 'S'),
            ('NGC 1491', 'I'), ('NGC 1342', 'S'), ('NGC 1333', 'I'), ('NGC 1245', 'S'),
            ('NGC 1058', 'M'), ('IC 348', 'M'), ('C 24', 'I'), ('NGC 884', 'N'),
            ('NGC 869', 'N'), ('NGC 1579', 'M'), ('NGC 1499', 'I'), ('NGC 1023', 'S'),
            ('M 76', 'S'), ('M 34', 'B')
            ],
    'PHE': [('NGC 7689', 'I'), ('IC 5325', 'M')],
    # Block 9
    'PIC': [],
    'PSC': [('NGC 7782', 'I'), ('NGC 718', 'I'), ('NGC 503', 'I'), ('NGC 7541', 'I'),
            ('NGC 660', 'I'), ('NGC 520', 'M'), ('NGC 514', 'M'), ('NGC 488', 'M'),
            ('NGC 467', 'I'), ('NGC 266', 'I'), ('M 74', 'M'),
            ],
    'PSA': [('NGC 7173', 'I'), ('NGC 7361', 'I'), ('IC 5271', 'I')],
    'PUP': [('C 71', 'B'), ('NGC 2310', 'M'), ('NGC 2427', 'M'), ('NGC 2451', 'S'),
            ('NGC 2546', 'B'), ('NGC 2579', 'S'), ('NGC 2559', 'M'), ('NGC 2533', 'S'),
            ('NGC 2509', 'S'), ('NGC 2482', 'S'), ('Cr 155', 'S'), ('Sh2 302', 'I'),
            ('NGC 2571', 'S'), ('NGC 2567', 'S'), ('NGC 2539', 'S'), ('NGC 2525', 'M'),
            ('NGC 2467', 'S'), ('NGC 2439', 'S'), ('NGC 2423', 'S'), ('M 46', 'B'),
            ('Cr 468', 'S'), ('NGC 2440', 'S'), ('M 93', 'S'), ('M 47', 'B'),
            ],
    'PYX': [('NGC 2627', 'S'), ('NGC 2658', 'S'), ('NGC 2635', 'M'), ('NGC 2613', 'M'),
            ('NGC 2818', 'M'), ('IC 2469', 'I'),],
    'RET': [('NGC 1313', 'S'), ('NGC 1559', 'M'), ('NGC 1574', 'M'), ('NGC 1543', 'M')],
    'SGE': [('PK G054.2-03.4', 'M'), ('Sh2 84', 'I'), ('Sh2 82', 'I'), ('Sh2 80', 'M'),
            ('M 71', 'S')],
    'SGR': [('IC 4684', 'M'), ('NGC 6540', 'S'), ('NGC 6558', 'M'), ('NGC 6559', 'I'),
            ('NGC 6563', 'M'), ('NGC 6565', 'M'), ('NGC 6583', 'M'), ('NGC 6638', 'S'),
            ('NGC 6652', 'M'), ('NGC 6717', 'S'), ('NGC 6723', 'S'), ('NGC 6774', 'S'),
            ('NGC 6902', 'M'), ('M 17', 'B'), ('M 20', 'B'), ('M 22', 'B'),
            ('M 24', 'B'), ('M 55', 'S'), ('M 8', 'B'), ('C 57', 'I'),
            ('M 18', 'S'), ('M 21', 'S'), ('M 23', 'S'), ('M 28', 'S'),
            ('NGC 6445', 'M'), ('NGC 6629', 'M'), ('NGC 6818', 'M'), ('IC 4701', 'I'),
            ('M 25', 'B'), ('M 54', 'S'), ('M 69', 'S'), ('M 70', 'S'),
            ('M 75', 'S'), ('NGC 6440', 'M'), ('NGC 6520', 'S'), ('NGC 6522', 'S'),
            ('NGC 6537', 'M'), ('NGC 6544', 'S'), ('NGC 6553', 'S'), ('NGC 6603', 'M'),
            ('NGC 6624', 'S'), ('NGC 6642', 'M'), ('IC 1284', 'I'), 
            ],
    # Block 10
    'SCO': [('C 69', 'S'), ('C 75', 'S'), ('C 76', 'B'), ('IC 4628', 'M'), 
            ('NGC 6072', 'M'), ('NGC 6139', 'M'), ('NGC 6153', 'M'), ('NGC 6178', 'S'),
            ('NGC 6192', 'S'), ('NGC 6216', 'S'), ('NGC 6242', 'S'), ('NGC 6249', 'S'),
            ('NGC 6259', 'S'), ('NGC 6268', 'S'), ('NGC 6281', 'B'), ('NGC 6322', 'B'),
            ('NGC 6334', 'I'), ('NGC 6337', 'M'), ('NGC 6388', 'S'), ('NGC 6496', 'S'),
            ('Sh2 3', 'I'), ('NGC 6453', 'M'), ('NGC 6441', 'S'), ('NGC 6416', 'B'),
            ('NGC 6404', 'S'), ('NGC 6400', 'S'), ('NGC 6396', 'S'), ('NGC 6357', 'I'),
            ('IC 4605', 'I'), ('NGC 6451', 'S'), ('NGC 6144', 'S'), ('M 7', 'B'),
            ('M 6', 'B'), ('IC 4592', 'I'), ('M 80', 'S'), ('M 4', 'B')
            ],
    'SCL': [('C 72', 'S'), ('C 70', 'S'), ('PGC 3589', 'I'), ('NGC 150', 'M'),
            ('IC 1558', 'I'), ('NGC 134', 'M'), ('IC 5332', 'M'), ('NGC 7793', 'S'),
            ('NGC 613', 'S'), ('NGC 288', 'S'), ('C 65', 'S'), 
            ],
    'SCT': [('IC 1287', 'I'), ('B 104', 'I'), ('B 103', 'I'), ('Sh2 48', 'I'),
            ('NGC 6712', 'S'), ('NGC 6664', 'S'), ('NGC 6631', 'S'), ('M 26', 'S'),
            ('IC 1295', 'I'), ('M 11', 'B')
            ],
    'SER': [('Sh2 64', 'I'), ('Sh2 46', 'I'), ('NGC 6539', 'S'), ('NGC 6070', 'I'),
            ('NGC 6027', 'I'), ('NGC 6012', 'I'), ('NGC 5964', 'I'), ('NGC 6604', 'I'),
            ('NGC 5921', 'I'), ('IC 4756', 'B'), ('NGC 6118', 'I'), ('M 5', 'B'),
            ('M 16', 'B')
            ],
    'SEX': [('NGC 3044', 'I'), ('NGC 2974', 'M'), ('NGC 2967', 'I'), ('NGC 3423', 'I'),
            ('NGC 3169', 'M'), ('C 53', 'S')
            ],
    'TAU': [('NGC 1807', 'S'),  ('NGC 1555', 'M'), ('IC 2087', 'I'), ('Sh2 240', 'I'),
            ('Sh2 239', 'I'), ('NGC 1817', 'S'), ('NGC 1647', 'S'), ('NGC 1514', 'M'),
            ('C 41', 'N'), ('M 45', 'N'), ('M 1', 'S')
            ],
    'TEL': [('IC 4837', 'I'), ('NGC 6887', 'I'), ('NGC 6868', 'M'), ('NGC 6584', 'S') ],
    'TRI': [('NGC 969', 'I'), ('NGC 1060', 'I'), ('NGC 925', 'M'), ('NGC 784', 'I'),
            ('NGC 672', 'M'), ('M 33', 'B')],
    # Block 11
    'TRA': [('NGC 5938', 'I'), ('C 95', 'B'), ],
    'TUC': [('C 104', 'B'), ('C 106', 'N'), ('NGC 292', 'N'), ('NGC 371', 'S'),
            ('NGC 346', 'I'), ('NGC 267', 'I') ],
    'UMA': [('NGC 5430', 'I'), ('NGC 5389', 'I'), ('NGC 5322', 'M'), ('NGC 5128', 'I'),
            ('NGC 4157', 'M'), ('NGC 4096', 'M'), ('NGC 4062', 'M'), ('NGC 3994', 'I'),
            ('NGC 3949', 'M'), ('NGC 3921', 'I'), ('NGC 3917', 'M'), ('NGC 3788', 'I'),
            ('NGC 3769', 'M'), ('NGC 3690', 'M'), ('NGC 3652', 'I'), ('NGC 3614', 'I'),
            ('NGC 3549', 'I'), ('NGC 3448', 'I'), ('NGC 3310', 'M'), ('NGC 3027', 'I'),
            ('NGC 2768', 'M'), ('NGC 2742', 'M'), ('NGC 2685', 'I'), ('NGC 2681', 'M'),
            ('NGC 2654', 'I'), ('NGC 5585', 'M'), ('NGC 5308', 'I'), ('NGC 4605', 'M'),
            ('NGC 4102', 'M'), ('NGC 4100', 'M'), ('NGC 4041', 'M'), ('NGC 4026', 'M'),
            ('NGC 4013', 'I'), ('NGC 3945', 'M'), ('NGC 3780', 'I'), ('NGC 3756', 'M'),
            ('NGC 3718', 'M'), ('NGC 3319', 'M'), ('NGC 3077', 'M'), ('NGC 2985', 'M'),
            ('NGC 2857', 'I'), ('NGC 2841', 'S'), ('NGC 2805', 'I'), ('M 40', 'S'),
            ('IC 2574', 'M'), ('NGC 5474', 'M'), ('NGC 5204', 'I'), ('NGC 4088', 'I'),
            ('NGC 3953', 'M'), ('NGC 3938', 'M'), ('NGC 3893', 'S'), ('NGC 3877', 'I'),
            ('NGC 3726', 'S'), ('NGC 3675', 'S'), ('NGC 3631', 'S'), ('NGC 3359', 'M'),
            ('NGC 3198', 'S'), ('NGC 3079', 'M'), ('NGC 2976', 'M'), ('M 82', 'S'),
            ('NGC 4051', 'I'), ('NGC 3180', 'M'), ('M 97', 'S'), ('M 81', 'S'),
            ('M 109', 'S'), ('M 108', 'S'), ('M 101', 'S')
            ],
    'UMI': [('NGC 6217', 'M'), ('NGC 5832', 'I')],
    'VEL': [('NGC 2736', 'I'), ('NGC 2899', 'M'), ('NGC 2792', 'M'), ('NGC 3256', 'M'),
            ('NGC 2866', 'M'), ('C 74', 'S'), ('NGC 2659', 'S'), ('C 79', 'S'),
            ('NGC 2670', 'S'), ('IC 2488', 'S'), ('Cr 197', 'M'), ('NGC 2669', 'B'),
            ('NGC 3228', 'B'), ('Cr 203', 'B'), ('NGC 2547', 'B'), ('IC 2395', 'S'),
            ('C 85', 'N'),
            ],
    'VIR': [('NGC 5668', 'I'), ('NGC 5584', 'I'), ('NGC 5468', 'I'), ('NGC 5356', 'I'),
            ('NGC 5334', 'I'), ('NGC 5257', 'I'), ('NGC 5254', 'I'), ('NGC 5084', 'I'),
            ('NGC 5077', 'I'), ('NGC 4981', 'I'), ('NGC 4941', 'I'), ('NGC 4825', 'M'),
            ('NGC 4753', 'M'), ('NGC 4643', 'M'), ('NGC 4699', 'M'), ('NGC 4606', 'I'),
            ('NGC 4517', 'M'), ('NGC 4424', 'I'), ('NGC 4416', 'M'), ('NGC 4365', 'M'),
            ('NGC 5846', 'M'), ('NGC 5838', 'M'), ('NGC 5775', 'M'), ('NGC 5746', 'M'),
            ('NGC 5713', 'M'), ('NGC 5701', 'M'), ('NGC 5634', 'S'), ('NGC 5576', 'M'),
            ('NGC 5426', 'I'), ('NGC 5068', 'S'), ('NGC 5044', 'I'), ('NGC 4902', 'I'),
            ('NGC 4900', 'I'), ('NGC 4781', 'I'), ('NGC 4698', 'I'), ('NGC 4691', 'M'),
            ('NGC 4664', 'M'), ('NGC 4597', 'I'), ('NGC 4596', 'I'), ('NGC 4519', 'I'),
            ('NGC 4454', 'I'), ('NGC 4442', 'M'), ('NGC 4440', 'M'), ('NGC 4371', 'M'),
            ('NGC 4261', 'I'), ('NGC 4179', 'M'), ('NGC 4116', 'M'), ('M 89', 'S'),
            ('C 52', 'M'), ('NGC 5364', 'M'), ('NGC 5247', 'S'), ('NGC 5170', 'M'),
            ('NGC 5054', 'M'), ('NGC 4845', 'M'), ('NGC 4762', 'S'), ('NGC 4666', 'M'),
            ('NGC 4654', 'M'), ('NGC 4593', 'M'), ('NGC 4567', 'M'), ('NGC 4536', 'M'),
            ('NGC 4535', 'M'), ('NGC 4527', 'M'), ('NGC 4526', 'M'), ('NGC 4487', 'M'),
            ('NGC 4461', 'M'), ('NGC 4452', 'I'), ('NGC 4435', 'S'), ('NGC 4429', 'M'),
            ('NGC 4273', 'I'), ('NGC 4216', 'M'), ('M 90', 'S'), ('M 87', 'S'),
            ('M 86', 'S'), ('M 84', 'S'), ('M 60', 'S'), ('M 59', 'S'), 
            ('M 58', 'S'), ('M 49', 'S'), ('M 104', 'S'), ('NGC 5566', 'M'),
            ('NGC 4030', 'M'), ('M 61', 'S')
            ],
    'VOL': [('NGC 2442', 'S')],
    'VUL': [('NGC 6940', 'B'), ('NGC 6802', 'S'), ('C 37', 'S'), ('NGC 6830', 'S'),
            ('Cr 399', 'B'), ('NGC 6823', 'S'), ('M 27', 'S')
            ]
}

def count_targets():
    n = 0
    kk = TARGET_OBJECTS.keys()
    for k in kk:
        n += len(TARGET_OBJECTS[k])
    return n

def get_target_dist():
    d = {}
    kk = TARGET_OBJECTS.keys()
    for k in kk:
        objs = TARGET_OBJECTS[k]
        for o in objs:
            try:
                tag = o[1]
                if tag in d.keys():
                    d[tag] += 1
                else:
                    d[tag] = 1
            except:
                print(f"Problem with {o} in {k}")
    return d

def find_dupes():
    found = []
    dupes = 0
    for k in TARGET_OBJECTS.keys():
        objs = TARGET_OBJECTS[k]
        for o in objs:
            name = o[0]
            if name in found:
                print(f"DUPE: {name} in {k}")
                dupes += 1
            else:
                found.append(name)

    if dupes == 0:
        print("No dupes found.")

def by_catalog():
    d = {}
    for k in TARGET_OBJECTS.keys():
        objs = TARGET_OBJECTS[k]
        for o in objs:
            cat = o[0].split(' ')[0]
            if cat in d.keys():
                d[cat] += 1
            else:
                d[cat] = 1
    return d

def list_by_cat(s):
    objs = []
    for k in TARGET_OBJECTS.keys():
        con = TARGET_OBJECTS[k]
        for o in con:
            cat = o[0].split(' ')[0]
            if cat == s:
                objs.append(o)
    return sorted(objs)

def print_cat(s):
    objs = list_by_cat(s)
    for c in objs:
        print(f"\t{c}")

SPECIAL = {
    'UGC 3697':2838,  'Dwi 1': 2834, 'ESO 172-7': 2866, 'WLM': 2845, 
    'PG 1634+706': 2855, 'Arp 188': 2861, 'IRAS 09371+1212': 659,
    'UGC 5470': 2850, 'Sandqvist 149': 2853, 'UGC 12914': 2832, 'PGC 69457': 2865, 
    'PK G054.2-03.4': 2846, 'PGC 3589': 2857,
}
def generate_spreadsheet(fn="dso_book_objects.tsv"):
    rows = []
    for k in TARGET_OBJECTS.keys():
        objs = TARGET_OBJECTS[k]
        for o in objs:
            query, method = o[:2]
            words, name = find_cat_id_in_string(query)
            target = search_dso_name(words, name)
            if target is None:
                if query in SPECIAL.keys():
                    try:
                        target = DSO.objects.get(pk=SPECIAL[query])
                    except:
                        print("Lookup fail: ", query)
                        target = None
            if target is None:
                print(f"{k}: Problem with: {query}")
            row = print_row(target, k, method)
            rows.append(row)
    with open(fn, 'w+') as f:
        f.write(create_header())
        for row in rows:
            f.write(row)

def fix(x):
    if x is None:
        return ''
    return(f"{x}")

def create_header():
    c = [
        'PK', 'Name', 'Nickname', 'Const', 'SMeth', 
        'N', 'B', 'S', 'M', 'I',
        'Type', 'Morph', 'RA', 'Dec', 'Mag',
        'SB', 'CI', 'Ang.', 'VPri', 'IPri',
        '#inF', 'Aliases'
    ]
    return '\t'.join(c) + '\n'
    
def print_row(dso, const, method):
    fields = []
    name = dso.map_label if dso.map_label else dso.shown_name
    fields.append(f"{dso.pk}")
    fields.append(name)
    fields.append(fix(dso.nickname))
    fields.append(const)
    fields.append(method)

    fields.append('') # N qual+flags
    fields.append('') # B qual+flags
    fields.append('') # S qual+flags
    fields.append('') # M qual+flags
    fields.append('') # I qual+flags

    fields.append(dso.object_type.short_name)
    fields.append(fix(dso.morphological_type))
    fields.append(f"{dso.ra:07.4f}")
    fields.append(f"{dso.dec:+07.3f}")
    fields.append(fix(dso.magnitude))

    fields.append(fix(dso.surface_brightness))
    fields.append(fix(dso.contrast_index))
    fields.append(fix(dso.angular_size))
    fields.append(fix(dso.priority_value))
    fields.append(fix(dso.imaging_checklist_priority))

    fields.append(fix(dso.dsoinfield_set.count()))
    fields.append(fix(dso.alias_list))
    
    return '\t'.join(fields) + '\n'

def get_stats():
    z = '%'
    c = 0.
    cn = 0
    n = count_targets()
    print(f"# Targets: {n}")
    d = get_target_dist()
    print(f"DIST:")
    for k in 'NBSMI':
        p = (100. * d[k] / n)
        c += p
        cn += d[k]
        print(f"\t{k}: {d[k]:4d} = {p:5.2f}{z}\t{cn:4d} = {c:6.2f}{z}")
    find_dupes()
    cats = by_catalog()
    print("\nCAT:")
    for k in sorted(cats.keys()):
        print(f"\t{k:20s}: {cats[k]:5d}")

    #generate_spreadsheet()

def dso_in_target_list(dso):
    con = dso.constellation.abbreviation
    for item in TARGET_OBJECTS[con]:
        if item[0] == dso.shown_name:
            return True
    return False

def generate(constellation):
    dso_list = DSO.objects.filter(constellation__abbreviation=constellation)
    for dso in dso_list:
        target = dso.targetdso
        if target.ready_to_go:
            continue
        in_list = dso_in_target_list(dso)

if __name__ == '__main__':
    get_stats()