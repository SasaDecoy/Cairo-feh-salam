"""
Inline coordinate constants. Used as a fallback when the CleanedData CSVs
are absent (e.g., running the app from a clone without the data folder).

Sourced from the team's React prototype. Coordinates are [lng, lat].
"""

# 24 post-2014 Metro Line 3 stations (selection — the story-critical ones)
METRO_POST_2014 = [
    {"name": "Adly Mansour",      "lng": 31.4213, "lat": 30.1460, "year": 2014, "mode": "metro"},
    {"name": "El Shams Club",     "lng": 31.3361, "lat": 30.1155, "year": 2014, "mode": "metro"},
    {"name": "Haroun",            "lng": 31.3272, "lat": 30.1117, "year": 2014, "mode": "metro"},
    {"name": "Hayy El-Zohour",    "lng": 31.3153, "lat": 30.1097, "year": 2014, "mode": "metro"},
    {"name": "Nadi El-Shams",     "lng": 31.3057, "lat": 30.1076, "year": 2014, "mode": "metro"},
    {"name": "Alf Maskan",        "lng": 31.2949, "lat": 30.1040, "year": 2014, "mode": "metro"},
    {"name": "Heliopolis Square", "lng": 31.2885, "lat": 30.0971, "year": 2019, "mode": "metro"},
    {"name": "Hisham Barakat",    "lng": 31.2828, "lat": 30.0920, "year": 2019, "mode": "metro"},
    {"name": "Al-Ahram",          "lng": 31.2783, "lat": 30.0882, "year": 2019, "mode": "metro"},
    {"name": "Koleyet El-Banat",  "lng": 31.2748, "lat": 30.0803, "year": 2020, "mode": "metro"},
    {"name": "Stadium",           "lng": 31.2718, "lat": 30.0713, "year": 2020, "mode": "metro"},
    {"name": "Fair Zone",         "lng": 31.2635, "lat": 30.0691, "year": 2020, "mode": "metro"},
    {"name": "Abbassia",          "lng": 31.2627, "lat": 30.0676, "year": 2020, "mode": "metro"},
    {"name": "Abdou Pasha",       "lng": 31.2558, "lat": 30.0583, "year": 2022, "mode": "metro"},
    {"name": "Bab El-Shaaria",    "lng": 31.2537, "lat": 30.0526, "year": 2022, "mode": "metro"},
    {"name": "Attaba",            "lng": 31.2468, "lat": 30.0527, "year": 2022, "mode": "metro"},
    {"name": "Nasser",            "lng": 31.2388, "lat": 30.0549, "year": 2022, "mode": "metro"},
    {"name": "Maspero",           "lng": 31.2338, "lat": 30.0530, "year": 2022, "mode": "metro"},
    {"name": "Zamalek",           "lng": 31.2218, "lat": 30.0588, "year": 2022, "mode": "metro"},
    {"name": "Kit Kat",           "lng": 31.2105, "lat": 30.0710, "year": 2022, "mode": "metro"},
    {"name": "Sudan Street",      "lng": 31.1988, "lat": 30.0735, "year": 2023, "mode": "metro"},
    {"name": "Imbaba (L3)",       "lng": 31.2060, "lat": 30.0900, "year": 2024, "mode": "metro"},
    {"name": "Bohouth",           "lng": 31.1993, "lat": 30.1010, "year": 2024, "mode": "metro"},
    {"name": "Rod El-Farag Axis", "lng": 31.2041, "lat": 30.1110, "year": 2024, "mode": "metro"},
]

# 7 operational LRT stations (of 20 total — 13 still planned)
LRT_STATIONS = [
    {"name": "Adly Mansour",          "lng": 31.4213, "lat": 30.1460, "mode": "lrt"},
    {"name": "Hykestep",              "lng": 31.5015, "lat": 30.1590, "mode": "lrt"},
    {"name": "Badr",                  "lng": 31.5608, "lat": 30.1492, "mode": "lrt"},
    {"name": "Shorouk",               "lng": 31.6166, "lat": 30.1220, "mode": "lrt"},
    {"name": "R5",                    "lng": 31.7218, "lat": 30.0785, "mode": "lrt"},
    {"name": "R3",                    "lng": 31.7687, "lat": 30.0425, "mode": "lrt"},
    {"name": "Capital Train Station", "lng": 31.8028, "lat": 30.0178, "mode": "lrt"},
]

# 10 confirmed BRT stations with daily informal boardings (demand feeding H3)
BRT_STATIONS = [
    {"name": "Al-Marg",              "lng": 31.3489, "lat": 30.1532, "demand": 14726, "mode": "brt"},
    {"name": "Al-Salam",             "lng": 31.3680, "lat": 30.1448, "demand": 9559,  "mode": "brt"},
    {"name": "Al-Khusus",            "lng": 31.3320, "lat": 30.1750, "demand": 7979,  "mode": "brt"},
    {"name": "Adly Mansour BRT",     "lng": 31.4180, "lat": 30.1440, "demand": 7483,  "mode": "brt"},
    {"name": "Shubra El-Kheima BRT", "lng": 31.2445, "lat": 30.1290, "demand": 5521,  "mode": "brt"},
    {"name": "Bahtim",               "lng": 31.2587, "lat": 30.1460, "demand": 2032,  "mode": "brt"},
    {"name": "Gardinia",             "lng": 31.3022, "lat": 30.1278, "demand": 1120,  "mode": "brt"},
    {"name": "Mostorod",             "lng": 31.2887, "lat": 30.1321, "demand": 453,   "mode": "brt"},
    {"name": "Al-Qaleg",             "lng": 31.3752, "lat": 30.1625, "demand": 340,   "mode": "brt"},
    {"name": "Moasasat El-Zakah",    "lng": 31.3098, "lat": 30.1158, "demand": 236,   "mode": "brt"},
]

# 50 informal terminal points (coral dots in the hero map)
INFORMAL_TERMINALS = [
    [31.2051, 30.0843], [31.2103, 30.0882], [31.2077, 30.0912], [31.2038, 30.0889],
    [31.2098, 30.0856], [31.2125, 30.0878], [31.2070, 30.0830], [31.2115, 30.0910],
    [31.2450, 30.1072], [31.2418, 30.1120], [31.2488, 30.1105], [31.2401, 30.1155],
    [31.2470, 30.1180], [31.2445, 30.1220], [31.2380, 30.1090], [31.2510, 30.1135],
    [31.1987, 30.0098], [31.2025, 30.0150], [31.1955, 30.0165], [31.2078, 30.0120],
    [31.1890, 30.0055], [31.2105, 30.0080], [31.1935, 30.0210], [31.2045, 30.0235],
    [31.2357, 30.0444], [31.2390, 30.0478], [31.2325, 30.0418], [31.2410, 30.0501],
    [31.3278, 30.0987], [31.3215, 30.1042], [31.3155, 30.1088], [31.3085, 30.1025],
    [31.2581, 29.9601], [31.2620, 29.9650], [31.2545, 29.9570], [31.2598, 29.9532],
    [31.2785, 30.0665], [31.2855, 30.0712], [31.2240, 30.0820], [31.2320, 30.0892],
    [31.1772, 30.0568], [31.1820, 30.0620], [31.1690, 30.0505], [31.1745, 30.0655],
    [31.3450, 30.1380], [31.3520, 30.1420], [31.3390, 30.1325], [31.3458, 30.1450],
    [31.2690, 30.0321], [31.2735, 30.0378],
]

# District approximations (coverage class: under | med | over)
DISTRICTS = [
    {"name": "Imbaba",       "lng": 31.2083, "lat": 30.0866, "pop": 63_000, "coverage": "under"},
    {"name": "Shubra",       "lng": 31.2445, "lat": 30.1090, "pop": 58_000, "coverage": "under"},
    {"name": "Al-Warraq",    "lng": 31.2018, "lat": 30.1035, "pop": 52_000, "coverage": "under"},
    {"name": "Al-Matariyya", "lng": 31.3170, "lat": 30.1263, "pop": 49_000, "coverage": "under"},
    {"name": "Ain Shams",    "lng": 31.3221, "lat": 30.1068, "pop": 46_000, "coverage": "under"},
    {"name": "Al-Haram",     "lng": 31.1650, "lat": 29.9890, "pop": 42_000, "coverage": "under"},
    {"name": "Al-Duqqi",     "lng": 31.2070, "lat": 30.0390, "pop": 40_000, "coverage": "under"},
    {"name": "Downtown",     "lng": 31.2357, "lat": 30.0444, "pop": 28_000, "coverage": "over"},
    {"name": "Zamalek",      "lng": 31.2218, "lat": 30.0588, "pop": 25_000, "coverage": "over"},
    {"name": "Garden City",  "lng": 31.2320, "lat": 30.0380, "pop": 22_000, "coverage": "over"},
    {"name": "Heliopolis",   "lng": 31.2954, "lat": 30.0908, "pop": 24_000, "coverage": "over"},
    {"name": "Maadi",        "lng": 31.2581, "lat": 29.9601, "pop": 18_000, "coverage": "over"},
    {"name": "New Cairo 1",  "lng": 31.4702, "lat": 30.0131, "pop": 3_000,  "coverage": "over"},
    {"name": "6th October",  "lng": 30.9680, "lat": 29.9697, "pop": 2_800,  "coverage": "over"},
    {"name": "Sheikh Zayed", "lng": 30.9758, "lat": 30.0490, "pop": 2_500,  "coverage": "over"},
    {"name": "Ash-Shorouk",  "lng": 31.6166, "lat": 30.1220, "pop": 1_800,  "coverage": "over"},
]

# 115 Phase 1 ghost terminals would ideally be loaded from merged_G_underused_terminals.csv.
# Inline fallback: a synthetic pattern of ghost positions near dense districts.
GHOST_TERMINALS_FALLBACK = INFORMAL_TERMINALS[:30]
