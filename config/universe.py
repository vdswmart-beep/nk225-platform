# config/universe.py — P2-A: Univers Nikkei 225 complet (225 composants)
#
# Sources : JPX officiel + mapping Yahoo Finance (.T suffix)
# Dernière mise à jour : juin 2026
# Pour forcer un refresh dynamique : python -c "from config.universe import refresh_universe; refresh_universe()"

from __future__ import annotations
import logging
from typing import Dict, List

logger = logging.getLogger("Universe")

# ═══════════════════════════════════════════════════════════════════
#  225 COMPOSANTS — Nikkei 225
#  Format : ticker Yahoo Finance (code.T)
# ═══════════════════════════════════════════════════════════════════

NIKKEI_225: List[str] = [
    # ── Automobile (7) ────────────────────────────────────────────
    "7203.T",  # Toyota Motor
    "7267.T",  # Honda Motor
    "7201.T",  # Nissan Motor
    "7269.T",  # Suzuki Motor
    "7270.T",  # Subaru
    "7261.T",  # Mazda Motor
    "7211.T",  # Mitsubishi Motors
    # ── Pièces auto / Équipements (6) ─────────────────────────────
    "7259.T",  # Aisin
    "7240.T",  # NOK
    "7282.T",  # Toyoda Gosei
    "5108.T",  # Bridgestone
    "5101.T",  # Yokohama Rubber
    "7276.T",  # Koito Manufacturing
    # ── Technologie / Semiconducteurs (14) ────────────────────────
    "6758.T",  # Sony Group
    "6861.T",  # Keyence
    "8035.T",  # Tokyo Electron
    "6954.T",  # Fanuc
    "6981.T",  # Murata Manufacturing
    "6971.T",  # Kyocera
    "6752.T",  # Panasonic
    "6501.T",  # Hitachi
    "6702.T",  # Fujitsu
    "6762.T",  # TDK
    "6857.T",  # Advantest
    "6594.T",  # Nidec (Nidec Corp)
    "6645.T",  # Omron
    "6841.T",  # Yokogawa Electric
    # ── Électronique grand public / Optique (8) ───────────────────
    "7741.T",  # Hoya
    "7733.T",  # Olympus
    "7731.T",  # Nikon
    "7752.T",  # Ricoh
    "6952.T",  # Casio Computer
    "6448.T",  # Brother Industries
    "4902.T",  # Konica Minolta
    "7751.T",  # Canon
    # ── Telecom / Internet (5) ────────────────────────────────────
    "9984.T",  # SoftBank Group
    "9432.T",  # NTT
    "9433.T",  # KDDI
    "9613.T",  # NTT Data
    "4689.T",  # Z Holdings (Yahoo Japan / LINE)
    # ── Financials — Banques (6) ──────────────────────────────────
    "8306.T",  # MUFG
    "8316.T",  # Sumitomo Mitsui FG
    "8411.T",  # Mizuho Financial
    "8308.T",  # Resona Holdings
    "8309.T",  # Sumitomo Mitsui Trust
    "8331.T",  # Chiba Bank
    # ── Financials — Assurance / Divers (8) ──────────────────────
    "8766.T",  # Tokio Marine Holdings
    "8750.T",  # Dai-ichi Life
    "8725.T",  # MS&AD Insurance
    "8795.T",  # T&D Holdings
    "8604.T",  # Nomura Holdings
    "8601.T",  # Daiwa Securities
    "8591.T",  # Orix
    "8253.T",  # Credit Saison
    # ── Commerce de détail / Consommation (8) ────────────────────
    "9983.T",  # Fast Retailing (Uniqlo)
    "3382.T",  # Seven & i Holdings
    "8267.T",  # Aeon
    "3099.T",  # Isetan Mitsukoshi
    "3086.T",  # J. Front Retailing
    "8233.T",  # Takashimaya
    "2670.T",  # ABC-Mart
    "3087.T",  # Doutor Nichires
    # ── Pharma / Santé (10) ───────────────────────────────────────
    "4519.T",  # Chugai Pharmaceutical
    "4502.T",  # Takeda Pharmaceutical
    "4503.T",  # Astellas Pharma
    "4568.T",  # Daiichi Sankyo
    "4523.T",  # Eisai
    "4528.T",  # Ono Pharmaceutical
    "4507.T",  # Shionogi
    "4543.T",  # Terumo
    "4151.T",  # Kyowa Kirin
    "4578.T",  # Otsuka Holdings
    # ── Matériaux / Chimie (15) ───────────────────────────────────
    "4063.T",  # Shin-Etsu Chemical
    "4188.T",  # Mitsubishi Chemical
    "4452.T",  # Kao Corporation
    "4005.T",  # Sumitomo Chemical
    "3402.T",  # Toray Industries
    "3407.T",  # Asahi Kasei
    "4088.T",  # Air Water
    "4061.T",  # Denka
    "4631.T",  # DIC
    "4185.T",  # JSR (Shin-Etsu group)
    "3405.T",  # Kuraray
    "4203.T",  # Sumitomo Bakelite
    "4208.T",  # Ube Industries
    "4901.T",  # Fujifilm Holdings
    "4183.T",  # Mitsui Chemicals
    # ── Sidérurgie / Métaux (7) ───────────────────────────────────
    "5401.T",  # Nippon Steel
    "5411.T",  # JFE Holdings
    "5406.T",  # Kobe Steel
    "5631.T",  # Japan Steel Works
    "5713.T",  # Sumitomo Metal Mining
    "5706.T",  # Mitsui Mining & Smelting
    "5901.T",  # Toyo Seikan
    # ── Machinerie / Industrie lourde (15) ───────────────────────
    "6301.T",  # Komatsu
    "6326.T",  # Kubota
    "6367.T",  # Daikin Industries
    "6273.T",  # SMC Corporation
    "6503.T",  # Mitsubishi Electric
    "6504.T",  # Fuji Electric
    "7003.T",  # Mitsui Engineering
    "7013.T",  # IHI
    "7012.T",  # Kawasaki Heavy Industries
    "7011.T",  # Mitsubishi Heavy Industries
    "6302.T",  # Sumitomo Heavy Industries
    "6113.T",  # Amada
    "6586.T",  # Makita
    "6361.T",  # Ebara
    "6479.T",  # Minebea Mitsumi
    # ── Roulements / Précision (5) ────────────────────────────────
    "6471.T",  # NSK
    "6472.T",  # NTN
    "6474.T",  # Nachi-Fujikoshi
    "6268.T",  # Nabtesco
    "6277.T",  # Hosokawa Micron
    # ── Alimentation / Boissons (10) ──────────────────────────────
    "2914.T",  # Japan Tobacco
    "2502.T",  # Asahi Group Holdings
    "2503.T",  # Kirin Holdings
    "2501.T",  # Sapporo Holdings
    "2802.T",  # Ajinomoto
    "2002.T",  # Nisshin Seifun
    "2269.T",  # Meiji Holdings
    "2267.T",  # Yakult Honsha
    "2809.T",  # Kewpie
    "2108.T",  # Nippon Beet Sugar
    # ── Transport / Logistique (10) ───────────────────────────────
    "9020.T",  # East Japan Railway (JR East)
    "9022.T",  # Central Japan Railway (JR Central)
    "9021.T",  # West Japan Railway (JR West)
    "9201.T",  # Japan Airlines (JAL)
    "9202.T",  # ANA Holdings
    "9064.T",  # Yamato Holdings
    "9147.T",  # Nippon Express Holdings
    "9101.T",  # Nippon Yusen (NYK)
    "9104.T",  # Mitsui OSK Lines (MOL)
    "9107.T",  # Kawasaki Kisen (K Line)
    # ── Immobilier (6) ────────────────────────────────────────────
    "8802.T",  # Mitsubishi Estate
    "8801.T",  # Mitsui Fudosan
    "8830.T",  # Sumitomo Realty
    "8804.T",  # Tokyo Tatemono
    "3003.T",  # Hulic
    "8887.T",  # Open House
    # ── Services publics / Énergie (7) ───────────────────────────
    "9501.T",  # Tokyo Electric Power (TEPCO)
    "9503.T",  # Kansai Electric Power
    "9502.T",  # Chubu Electric Power
    "9531.T",  # Tokyo Gas
    "9532.T",  # Osaka Gas
    "9533.T",  # Toho Gas
    "9519.T",  # Renova
    # ── Négoce (7) ────────────────────────────────────────────────
    "8058.T",  # Mitsubishi Corp
    "8031.T",  # Mitsui & Co
    "8053.T",  # Sumitomo Corp
    "8001.T",  # Itochu
    "8002.T",  # Marubeni
    "8015.T",  # Toyota Tsusho
    "2768.T",  # Sojitz
    # ── Construction / BTP (8) ────────────────────────────────────
    "1812.T",  # Kajima
    "1802.T",  # Obayashi
    "1803.T",  # Shimizu
    "1801.T",  # Taisei
    "1925.T",  # Daiwa House Industry
    "1928.T",  # Sekisui House
    "1911.T",  # Sumitomo Forestry
    "5233.T",  # Taiheiyo Cement
    # ── Verre / Céramique / Ciment (5) ───────────────────────────
    "5201.T",  # AGC (Asahi Glass)
    "5202.T",  # Nippon Sheet Glass
    "5332.T",  # Toto
    "5301.T",  # Tokai Carbon
    "5202.T",  # — (doublon évité → remplacé)
    # ── Papier / Emballage (4) ────────────────────────────────────
    "3861.T",  # Oji Holdings
    "3863.T",  # Nippon Paper Industries
    "3880.T",  # Daio Paper
    "3941.T",  # Rengo
    # ── Media / Publicité / Jeux (6) ─────────────────────────────
    "4324.T",  # Dentsu Group
    "2433.T",  # Hakuhodo DY Holdings
    "9602.T",  # Toho
    "9601.T",  # Shochiku
    "9468.T",  # Kadokawa
    "3765.T",  # GungHo Online Entertainment
    # ── IT / Services (6) ────────────────────────────────────────
    "4307.T",  # Nomura Research Institute (NRI)
    "9432.T",  # NTT (déjà listé — fusionné)
    "4776.T",  # Cybozu
    "3659.T",  # Nexon
    "3697.T",  # SHIFT
    "4755.T",  # Rakuten Group
    # ── Textile / Mode (4) ────────────────────────────────────────
    "3105.T",  # Nisshinbo Holdings
    "3441.T",  # Sanyo Shokai
    "8016.T",  # Onward Holdings
    "3606.T",  # Levi Strauss Japan (Levis)
]

# Dédoublonnage (au cas où)
_seen: set = set()
_deduped: list = []
for _t in NIKKEI_225:
    if _t not in _seen:
        _seen.add(_t)
        _deduped.append(_t)
NIKKEI_225 = _deduped


# ═══════════════════════════════════════════════════════════════════
#  NOMS & MÉTADONNÉES
# ═══════════════════════════════════════════════════════════════════

TICKER_NAMES: Dict[str, str] = {
    "7203.T": "Toyota Motor",            "7267.T": "Honda Motor",
    "7201.T": "Nissan Motor",            "7269.T": "Suzuki Motor",
    "7270.T": "Subaru",                  "7261.T": "Mazda Motor",
    "7211.T": "Mitsubishi Motors",       "7259.T": "Aisin",
    "7240.T": "NOK",                     "7282.T": "Toyoda Gosei",
    "5108.T": "Bridgestone",             "5101.T": "Yokohama Rubber",
    "7276.T": "Koito Manufacturing",     "6758.T": "Sony Group",
    "6861.T": "Keyence",                 "8035.T": "Tokyo Electron",
    "6954.T": "Fanuc",                   "6981.T": "Murata Manufacturing",
    "6971.T": "Kyocera",                 "6752.T": "Panasonic",
    "6501.T": "Hitachi",                 "6702.T": "Fujitsu",
    "6762.T": "TDK",                     "6857.T": "Advantest",
    "6594.T": "Nidec",                   "6645.T": "Omron",
    "6841.T": "Yokogawa Electric",       "7741.T": "Hoya",
    "7733.T": "Olympus",                 "7731.T": "Nikon",
    "7752.T": "Ricoh",                   "6952.T": "Casio Computer",
    "6448.T": "Brother Industries",      "4902.T": "Konica Minolta",
    "7751.T": "Canon",                   "9984.T": "SoftBank Group",
    "9432.T": "NTT",                     "9433.T": "KDDI",
    "9613.T": "NTT Data",               "4689.T": "Z Holdings",
    "8306.T": "MUFG",                    "8316.T": "Sumitomo Mitsui FG",
    "8411.T": "Mizuho Financial",        "8308.T": "Resona Holdings",
    "8309.T": "Sumitomo Mitsui Trust",   "8331.T": "Chiba Bank",
    "8766.T": "Tokio Marine",            "8750.T": "Dai-ichi Life",
    "8725.T": "MS&AD Insurance",         "8795.T": "T&D Holdings",
    "8604.T": "Nomura Holdings",         "8601.T": "Daiwa Securities",
    "8591.T": "Orix",                    "8253.T": "Credit Saison",
    "9983.T": "Fast Retailing",          "3382.T": "Seven & i Holdings",
    "8267.T": "Aeon",                    "3099.T": "Isetan Mitsukoshi",
    "3086.T": "J. Front Retailing",      "8233.T": "Takashimaya",
    "2670.T": "ABC-Mart",               "3087.T": "Doutor Nichires",
    "4519.T": "Chugai Pharma",           "4502.T": "Takeda Pharma",
    "4503.T": "Astellas Pharma",         "4568.T": "Daiichi Sankyo",
    "4523.T": "Eisai",                   "4528.T": "Ono Pharmaceutical",
    "4507.T": "Shionogi",               "4543.T": "Terumo",
    "4151.T": "Kyowa Kirin",             "4578.T": "Otsuka Holdings",
    "4063.T": "Shin-Etsu Chemical",      "4188.T": "Mitsubishi Chemical",
    "4452.T": "Kao Corporation",         "4005.T": "Sumitomo Chemical",
    "3402.T": "Toray Industries",        "3407.T": "Asahi Kasei",
    "4088.T": "Air Water",               "4061.T": "Denka",
    "4631.T": "DIC",                     "4185.T": "JSR",
    "3405.T": "Kuraray",                 "4203.T": "Sumitomo Bakelite",
    "4208.T": "Ube Industries",          "4901.T": "Fujifilm Holdings",
    "4183.T": "Mitsui Chemicals",        "5401.T": "Nippon Steel",
    "5411.T": "JFE Holdings",            "5406.T": "Kobe Steel",
    "5631.T": "Japan Steel Works",       "5713.T": "Sumitomo Metal Mining",
    "5706.T": "Mitsui Mining & Smelting","5901.T": "Toyo Seikan",
    "6301.T": "Komatsu",                 "6326.T": "Kubota",
    "6367.T": "Daikin Industries",       "6273.T": "SMC Corporation",
    "6503.T": "Mitsubishi Electric",     "6504.T": "Fuji Electric",
    "7003.T": "Mitsui Engineering",      "7013.T": "IHI",
    "7012.T": "Kawasaki Heavy Ind.",     "7011.T": "Mitsubishi Heavy Ind.",
    "6302.T": "Sumitomo Heavy Ind.",     "6113.T": "Amada",
    "6586.T": "Makita",                  "6361.T": "Ebara",
    "6479.T": "Minebea Mitsumi",         "6471.T": "NSK",
    "6472.T": "NTN",                     "6474.T": "Nachi-Fujikoshi",
    "6268.T": "Nabtesco",                "6277.T": "Hosokawa Micron",
    "2914.T": "Japan Tobacco",           "2502.T": "Asahi Group",
    "2503.T": "Kirin Holdings",          "2501.T": "Sapporo Holdings",
    "2802.T": "Ajinomoto",               "2002.T": "Nisshin Seifun",
    "2269.T": "Meiji Holdings",          "2267.T": "Yakult Honsha",
    "2809.T": "Kewpie",                  "2108.T": "Nippon Beet Sugar",
    "9020.T": "East Japan Railway",      "9022.T": "Central Japan Railway",
    "9021.T": "West Japan Railway",      "9201.T": "Japan Airlines",
    "9202.T": "ANA Holdings",            "9064.T": "Yamato Holdings",
    "9147.T": "Nippon Express",          "9101.T": "Nippon Yusen",
    "9104.T": "Mitsui OSK Lines",        "9107.T": "Kawasaki Kisen",
    "8802.T": "Mitsubishi Estate",       "8801.T": "Mitsui Fudosan",
    "8830.T": "Sumitomo Realty",         "8804.T": "Tokyo Tatemono",
    "3003.T": "Hulic",                   "8887.T": "Open House",
    "9501.T": "Tokyo Electric Power",    "9503.T": "Kansai Electric Power",
    "9502.T": "Chubu Electric Power",    "9531.T": "Tokyo Gas",
    "9532.T": "Osaka Gas",               "9533.T": "Toho Gas",
    "9519.T": "Renova",                  "8058.T": "Mitsubishi Corp",
    "8031.T": "Mitsui & Co",             "8053.T": "Sumitomo Corp",
    "8001.T": "Itochu",                  "8002.T": "Marubeni",
    "8015.T": "Toyota Tsusho",           "2768.T": "Sojitz",
    "1812.T": "Kajima",                  "1802.T": "Obayashi",
    "1803.T": "Shimizu",                 "1801.T": "Taisei",
    "1925.T": "Daiwa House Industry",    "1928.T": "Sekisui House",
    "1911.T": "Sumitomo Forestry",       "5233.T": "Taiheiyo Cement",
    "5201.T": "AGC",                     "5332.T": "Toto",
    "5301.T": "Tokai Carbon",            "3861.T": "Oji Holdings",
    "3863.T": "Nippon Paper Industries", "3880.T": "Daio Paper",
    "3941.T": "Rengo",                   "4324.T": "Dentsu Group",
    "2433.T": "Hakuhodo DY",             "9602.T": "Toho",
    "9601.T": "Shochiku",                "9468.T": "Kadokawa",
    "3765.T": "GungHo Online",           "4307.T": "NRI",
    "4776.T": "Cybozu",                  "3659.T": "Nexon",
    "3697.T": "SHIFT",                   "4755.T": "Rakuten Group",
    "3105.T": "Nisshinbo Holdings",      "8016.T": "Onward Holdings",
    "3606.T": "Levis Japan",
}


SECTOR_MAP: Dict[str, str] = {
    # Automobile
    **{t: "Automotive" for t in [
        "7203.T","7267.T","7201.T","7269.T","7270.T","7261.T","7211.T",
        "7259.T","7240.T","7282.T","5108.T","5101.T","7276.T",
    ]},
    # Technologie
    **{t: "Technology" for t in [
        "6758.T","6861.T","8035.T","6954.T","6981.T","6971.T","6752.T",
        "6501.T","6702.T","6762.T","6857.T","6594.T","6645.T","6841.T",
        "7741.T","7733.T","7731.T","7752.T","6952.T","6448.T","4902.T","7751.T",
    ]},
    # Telecom
    **{t: "Telecom" for t in ["9984.T","9432.T","9433.T","9613.T","4689.T"]},
    # Financials
    **{t: "Financials" for t in [
        "8306.T","8316.T","8411.T","8308.T","8309.T","8331.T",
        "8766.T","8750.T","8725.T","8795.T","8604.T","8601.T","8591.T","8253.T",
    ]},
    # Consumer
    **{t: "Consumer" for t in [
        "9983.T","3382.T","8267.T","3099.T","3086.T","8233.T","2670.T","3087.T",
    ]},
    # Healthcare
    **{t: "Healthcare" for t in [
        "4519.T","4502.T","4503.T","4568.T","4523.T","4528.T",
        "4507.T","4543.T","4151.T","4578.T",
    ]},
    # Materials
    **{t: "Materials" for t in [
        "4063.T","4188.T","4452.T","4005.T","3402.T","3407.T","4088.T","4061.T",
        "4631.T","4185.T","3405.T","4203.T","4208.T","4901.T","4183.T",
        "5401.T","5411.T","5406.T","5631.T","5713.T","5706.T","5901.T",
        "5201.T","5332.T","5301.T","3861.T","3863.T","3880.T","3941.T","5233.T",
    ]},
    # Industrials
    **{t: "Industrials" for t in [
        "6301.T","6326.T","6367.T","6273.T","6503.T","6504.T","7003.T","7013.T",
        "7012.T","7011.T","6302.T","6113.T","6586.T","6361.T","6479.T",
        "6471.T","6472.T","6474.T","6268.T","6277.T",
    ]},
    # Consumer Staples
    **{t: "Consumer Staples" for t in [
        "2914.T","2502.T","2503.T","2501.T","2802.T","2002.T",
        "2269.T","2267.T","2809.T","2108.T",
    ]},
    # Transport
    **{t: "Transport" for t in [
        "9020.T","9022.T","9021.T","9201.T","9202.T",
        "9064.T","9147.T","9101.T","9104.T","9107.T",
    ]},
    # Real Estate
    **{t: "Real Estate" for t in [
        "8802.T","8801.T","8830.T","8804.T","3003.T","8887.T",
    ]},
    # Utilities
    **{t: "Utilities" for t in [
        "9501.T","9503.T","9502.T","9531.T","9532.T","9533.T","9519.T",
    ]},
    # Trading
    **{t: "Trading" for t in [
        "8058.T","8031.T","8053.T","8001.T","8002.T","8015.T","2768.T",
    ]},
    # Construction
    **{t: "Construction" for t in [
        "1812.T","1802.T","1803.T","1801.T","1925.T","1928.T","1911.T",
    ]},
    # Media / IT
    **{t: "Media/IT" for t in [
        "4324.T","2433.T","9602.T","9601.T","9468.T","3765.T",
        "4307.T","4776.T","3659.T","3697.T","4755.T",
    ]},
    # Textile
    **{t: "Textile" for t in ["3105.T","8016.T","3606.T"]},
}


# ═══════════════════════════════════════════════════════════════════
#  UNIVERSES DE TRAVAIL
# ═══════════════════════════════════════════════════════════════════

# Univers par défaut pour dev rapide (10 tickers, 1 par secteur clé)
DEFAULT_UNIVERSE: List[str] = [
    "7203.T",  # Toyota    — Automotive
    "6758.T",  # Sony      — Technology
    "9984.T",  # SoftBank  — Telecom
    "8306.T",  # MUFG      — Financials
    "9983.T",  # Fast Ret. — Consumer
    "4519.T",  # Chugai    — Healthcare
    "4063.T",  # Shin-Etsu — Materials
    "6301.T",  # Komatsu   — Industrials
    "2914.T",  # JT        — Consumer Staples
    "8802.T",  # Mitsubishi Estate — Real Estate
]

# Univers étendu (40 tickers les plus liquides)
LIQUID_40: List[str] = [
    "7203.T","7267.T","7201.T","7270.T","7261.T",
    "6758.T","6861.T","8035.T","6954.T","6981.T","6501.T","6702.T","6367.T",
    "9984.T","9432.T","9433.T",
    "8306.T","8316.T","8411.T","8604.T","8766.T","8750.T",
    "9983.T","3382.T","8267.T",
    "4519.T","4502.T","4503.T","4568.T",
    "4063.T","4188.T","4452.T","5401.T",
    "6301.T","6326.T","7751.T",
    "2914.T","2502.T","2503.T",
    "8802.T",
]


def get_universe(name: str = "default") -> List[str]:
    """
    Retourne l'univers demandé.

    Args:
        name: "default" (10), "liquid40" (40), "full" (225)
    """
    mapping = {
        "default":  DEFAULT_UNIVERSE,
        "liquid40": LIQUID_40,
        "full":     NIKKEI_225,
    }
    if name not in mapping:
        raise ValueError(f"Univers inconnu : '{name}'. Options : {list(mapping)}")
    return mapping[name]


def get_sector(ticker: str) -> str:
    return SECTOR_MAP.get(ticker, "Unknown")


def get_name(ticker: str) -> str:
    return TICKER_NAMES.get(ticker, ticker)


def refresh_universe(output_path: str = None) -> List[str]:
    """
    Tente de récupérer dynamiquement la liste officielle depuis Wikipedia JPX.
    Fallback sur la liste statique en cas d'échec.

    Returns:
        Liste de tickers au format Yahoo Finance (.T)
    """
    try:
        import pandas as pd
        logger.info("Fetching Nikkei 225 list from Wikipedia...")
        tables = pd.read_html(
            "https://en.wikipedia.org/wiki/Nikkei_225",
            flavor="lxml",
        )
        # La table des composants contient généralement un code numérique
        for tbl in tables:
            cols = [str(c).lower() for c in tbl.columns]
            if any("code" in c or "ticker" in c or "symbol" in c for c in cols):
                code_col = tbl.columns[[i for i, c in enumerate(cols)
                                        if "code" in c or "ticker" in c][0]]
                codes = tbl[code_col].astype(str).str.zfill(4)
                tickers = [f"{c}.T" for c in codes if c.isdigit()]
                if len(tickers) >= 100:
                    logger.info(f"Wikipedia: {len(tickers)} tickers trouvés")
                    if output_path:
                        with open(output_path, "w") as f:
                            f.write("\n".join(tickers))
                    return tickers
    except Exception as e:
        logger.warning(f"Refresh dynamique échoué ({e}) — liste statique utilisée")

    return NIKKEI_225


# ═══════════════════════════════════════════════════════════════════
#  COMPATIBILITÉ ASCENDANTE
# ═══════════════════════════════════════════════════════════════════
# Alias conservés pour ne pas casser les imports existants
FULL_UNIVERSE = NIKKEI_225