import streamlit as st
import re

# =========================
# CONSTANTS
# =========================
SIGNS = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
SIGN_TO_IDX = {s: i for i, s in enumerate(SIGNS)}
IDX_TO_SIGN = {i: s for i, s in enumerate(SIGNS)}

SIGN_ALIASES = {
    # EN
    "Aries": "Koç", "Taurus": "Boğa", "Gemini": "İkizler", "Cancer": "Yengeç",
    "Leo": "Aslan", "Virgo": "Başak", "Libra": "Terazi", "Scorpio": "Akrep",
    "Sagittarius": "Yay", "Capricorn": "Oğlak", "Aquarius": "Kova", "Pisces": "Balık",
    # TR
    "Koç": "Koç", "Koc": "Koç",
    "Boğa": "Boğa", "Boga": "Boğa",
    "İkizler": "İkizler", "Ikizler": "İkizler",
    "Yengeç": "Yengeç", "Yengec": "Yengeç",
    "Aslan": "Aslan",
    "Başak": "Başak", "Basak": "Başak",
    "Terazi": "Terazi",
    "Akrep": "Akrep",
    "Yay": "Yay",
    "Oğlak": "Oğlak", "Oglak": "Oğlak",
    "Kova": "Kova",
    "Balık": "Balık", "Balik": "Balık",
    # Symbols
    "♈": "Koç", "♉": "Boğa", "♊": "İkizler", "♋": "Yengeç",
    "♌": "Aslan", "♍": "Başak", "♎": "Terazi", "♏": "Akrep",
    "♐": "Yay", "♑": "Oğlak", "♒": "Kova", "♓": "Balık",
}

# Gezegenleri TÜRKÇE anahtara normalize edeceğiz
PLANET_ALIASES = {
    # EN -> TR
    "Sun": "Güneş",
    "Moon": "Ay",
    "Mercury": "Merkür",
    "Venus": "Venüs",
    "Mars": "Mars",
    "Jupiter": "Jüpiter",
    "Saturn": "Satürn",
    "Uranus": "Uranüs",
    "Neptune": "Neptün",
    "Pluto": "Plüton",
    # Astro-Seek extras
    "Node": "KuzeyAyDüğümü",
    "Lilith": "Lilith",
    "Chiron": "Chiron",
    "Fortune": "Fortuna",
    "Vertex": "Vertex",
    # TR passthrough
    "Güneş": "Güneş",
    "Ay": "Ay",
    "Merkür": "Merkür",
    "Venüs": "Venüs",
    "Mars": "Mars",
    "Jüpiter": "Jüpiter",
    "Satürn": "Satürn",
    "Uranüs": "Uranüs",
    "Neptün": "Neptün",
    "Plüton": "Plüton",
    "KuzeyAyDüğümü": "KuzeyAyDüğümü",
    "Fortuna": "Fortuna",
}

RULERS_MODERN = {
    "Koç": "Mars", "Boğa": "Venüs", "İkizler": "Merkür", "Yengeç": "Ay",
    "Aslan": "Güneş", "Başak": "Merkür", "Terazi": "Venüs", "Akrep": "Plüton",
    "Yay": "Jüpiter", "Oğlak": "Satürn", "Kova": "Uranüs", "Balık": "Neptün",
}
RULERS_TRAD = {
    "Koç": "Mars", "Boğa": "Venüs", "İkizler": "Merkür", "Yengeç": "Ay",
    "Aslan": "Güneş", "Başak": "Merkür", "Terazi": "Venüs", "Akrep": "Mars",
    "Yay": "Jüpiter", "Oğlak": "Satürn", "Kova": "Satürn", "Balık": "Jüpiter",
}

HOUSE_MEANINGS = {
    1: "Benlik, beden, yaklaşım",
    2: "Para, gelir, özdeğer",
    3: "İletişim, yakın çevre, kardeşler",
    4: "Ev, aile, kökler",
    5: "Aşk, çocuklar, yaratıcılık",
    6: "İş rutinleri, sağlık, hizmet",
    7: "Eş/ortak, ilişkiler",
    8: "Paylaşımlar, kriz/dönüşüm, miras",
    9: "Uzaklar, eğitim, inançlar, hukuk",
    10: "Kariyer, statü, hedefler",
    11: "Sosyal çevre, projeler, umutlar",
    12: "Bilinçdışı, kapanışlar, izolasyon",
}

TOPIC_TO_ROOT = {
    "Ben / Kimlik": 1,
    "Para / Gelir": 2,
    "Kardeşler / İletişim": 3,
    "Ev / Aile": 4,
    "Aşk / Çocuk": 5,
    "İş Rutini / Sağlık": 6,
    "Eş / Ortaklık": 7,
    "Kriz / Paylaşımlar": 8,
    "Uzaklar / Eğitim": 9,
    "Kariyer": 10,
    "Arkadaşlar / Projeler": 11,
    "Bilinçdışı / Kapanış": 12,
}

OPPOSITE = {
    "Koç": "Terazi", "Boğa": "Akrep", "İkizler": "Yay", "Yengeç": "Oğlak",
    "Aslan": "Kova", "Başak": "Balık", "Terazi": "Koç", "Akrep": "Boğa",
    "Yay": "İkizler", "Oğlak": "Yengeç", "Kova": "Aslan", "Balık": "Başak"
}

# =========================
# HELPERS
# =========================
def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def derived_house(root_house: int, n: int) -> int:
    return ((root_house - 1) + (n - 1)) % 12 + 1

def overlay_sign(root_sign: str, n: int) -> str:
    idx = SIGN_TO_IDX[root_sign]
    return IDX_TO_SIGN[(idx + (n - 1)) % 12]

def get_ruler(sign: str, system: str) -> str:
    return (RULERS_MODERN if system == "Modern" else RULERS_TRAD)[sign]

def normalize_sign(token: str):
    token = token.strip()
    if token in SIGN_ALIASES:
        return SIGN_ALIASES[token]
    for k, v in SIGN_ALIASES.items():
        if k.lower() == token.lower():
            return v
    return None

def normalize_planet(raw: str) -> str:
    """
    Normalize planet to TURKISH keys:
    Uranus -> Uranüs, Neptune -> Neptün, etc.
    Also handles "Node (M)" by mapping to Node.
    """
    raw = raw.strip().strip(":")
    raw = raw.replace("\t", " ").strip()

    # turn "Node (M)" or "Node(M)" into "Node"
    raw_nospace = raw.replace(" ", "")
    if raw_nospace.lower().startswith("node"):
        return PLANET_ALIASES.get("Node", "KuzeyAyDüğümü")
    if raw_nospace.lower().startswith("lilith"):
        return PLANET_ALIASES.get("Lilith", "Lilith")

    # Remove non letters for matching (safe fallback)
    raw_clean = re.sub(r"[^A-Za-zÇĞİÖŞÜçğıöşü]", "", raw)

    if raw in PLANET_ALIASES:
        return PLANET_ALIASES[raw]
    if raw_nospace in PLANET_ALIASES:
        return PLANET_ALIASES[raw_nospace]
    if raw_clean in PLANET_ALIASES:
        return PLANET_ALIASES[raw_clean]

    # Try to match English planet names inside raw
    for en in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto","Chiron","Fortune","Vertex","Node","Lilith"]:
        if en.lower() in raw_nospace.lower():
            return PLANET_ALIASES.get(en, en)

    return raw_clean or raw

# =========================
# PARSERS
# =========================

# 1) SPACE/colon format
# Examples:
# Sun: Sagittarius 4°26'10''  end of 7  Direct
# Moon: Leo 0°53'40''  4  Direct
# Node: Leo 14°23'28''  5  Retrograde
PLANET_LINE_RE = re.compile(
    r"""^\s*
    (?P<planet>[A-Za-zÇĞİÖŞÜçğıöşü]+(?:\s*\(M\))?)\s*:?\s*
    (?P<sign>[A-Za-zÇĞİÖŞÜçğıöşü♈♉♊♋♌♍♎♏♐♑♒♓]+)\s+
    (?P<deg>\d{1,2})\s*°\s*
    (?P<min>\d{1,2})\s*['’′]\s*
    (?:(?P<sec>\d{1,2})\s*(?:''|["”″]{1,2})\s*)?
    (?:(?:end\s+of\s+)?(?P<house>\d{1,2}))\s*
    (?P<motion>Direct|Retrograde|R)?\s*$
    """,
    re.IGNORECASE | re.VERBOSE
)

# 2) COMPACT format (no spaces)
# Examples:
# UranusScorpio26°23’7
# MarsCapricorn3°23’9
PLANET_COMPACT_RE = re.compile(
    r"""^\s*
    (?P<planet>[A-Za-zÇĞİÖŞÜçğıöşü]+)
    (?P<sign>[A-Za-zÇĞİÖŞÜçğıöşü♈♉♊♋♌♍♎♏♐♑♒♓]+)
    (?P<deg>\d{1,2})\s*°\s*
    (?P<min>\d{1,2})\s*[’'′]
    (?P<house>\d{1,2})
    \s*$""",
    re.VERBOSE | re.IGNORECASE
)

def parse_planets_from_text(text: str):
    planets = {}
    errors = []
    ignored = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        # ignore lunar phase/misc lines
        if "(" in line and "°" in line and ")" in line and any(w in line.lower() for w in ["disseminating", "balsamic", "gibbous", "crescent", "phase"]):
            ignored.append(line)
            continue

        m = PLANET_LINE_RE.match(line)

        # Try compact if not matched
        if not m:
            m = PLANET_COMPACT_RE.match(line)

        if not m:
            ignored.append(line)
            continue

        planet = normalize_planet(m.group("planet"))
        sign = normalize_sign(m.group("sign"))
        if sign not in SIGN_TO_IDX:
            errors.append(line)
            continue

        deg = int(m.group("deg"))
        minute = int(m.group("min"))
        sec = int(m.group("sec")) if m.groupdict().get("sec") else 0
        house = int(m.group("house"))

        # motion only exists in LINE_RE
        motion = (m.groupdict().get("motion") or "").strip().lower()
        retro = motion in ["retrograde", "r"]

        deg_float = deg + minute / 60.0 + sec / 3600.0
        lon = SIGN_TO_IDX[sign] * 30.0 + deg_float

        planets[planet] = {"sign": sign, "deg": deg_float, "house": house, "lon": lon, "retro": retro}

    return planets, errors, ignored

def parse_house_cusps_from_text(text: str):
    cusps = {}
    errors = []

    # Matches:
    # 1: Taurus (ASC) 2°50’49’’
    # 7: Scorpio (DESC) 2°50’49’’
    cusp_re = re.compile(
        r"^\s*(?P<h>[1-9]|1[0-2])\s*:\s*(?P<sign>[A-Za-zÇĞİÖŞÜçğıöşü♈♉♊♋♌♍♎♏♐♑♒♓]+)\b",
        re.IGNORECASE
    )

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = cusp_re.match(line)
        if not m:
            continue
        h = int(m.group("h"))
        sign = normalize_sign(m.group("sign"))
        if sign not in SIGN_TO_IDX:
            errors.append(line)
            continue
        cusps[h] = sign

    return cusps, errors

# =========================
# ASPECTS (auto from degrees)
# =========================
ASPECTS_DEF = [
    ("conjunction", 0, 6),
    ("sextile", 60, 4.5),
    ("square", 90, 6),
    ("trine", 120, 6),
    ("opposition", 180, 6),
]

def angle_diff(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)

def compute_aspects(planets: dict):
    keys = list(planets.keys())
    aspects = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            p1, p2 = keys[i], keys[j]
            lon1, lon2 = planets[p1]["lon"], planets[p2]["lon"]
            d = angle_diff(lon1, lon2)
            for name, exact, orbmax in ASPECTS_DEF:
                orb = abs(d - exact)
                if orb <= orbmax:
                    aspects.append({"p1": p1, "p2": p2, "type": name, "orb": round(orb, 2)})
                    break
    return aspects

# =========================
# SCORING
# =========================
ANGULAR = {1, 4, 7, 10}
SUCCEDENT = {2, 5, 8, 11}

def house_score(house: int) -> int:
    if house in ANGULAR:
        return 12
    if house in SUCCEDENT:
        return 6
    return 0

ASPECT_WEIGHTS = {"conjunction": 10, "sextile": 8, "trine": 12, "square": -12, "opposition": -14}

def rulership_score(planet: str, sign: str, rulers_map: dict) -> int:
    if rulers_map.get(sign) == planet:
        return 10
    ruled = [s for s, p in rulers_map.items() if p == planet]
    for s in ruled:
        if OPPOSITE.get(s) == sign:
            return -10
    return 0

def aspect_score_for(planet: str, aspects: list[dict]) -> float:
    score = 0.0
    for a in aspects:
        if a["p1"] != planet and a["p2"] != planet:
            continue
        t = a["type"]
        if t not in ASPECT_WEIGHTS:
            continue
        orb = float(a.get("orb", 6))
        w = max(0.0, 1.0 - orb / 6.0)
        score += ASPECT_WEIGHTS[t] * w
    return score

def compute_ruler_strength(ruler: str, planets: dict, aspects: list, rulers_map: dict) -> dict:
    pos = planets.get(ruler)
    if not pos:
        return {"score": None, "parts": {}, "pos": None}

    hs = house_score(int(pos["house"]))
    rs = rulership_score(ruler, pos["sign"], rulers_map)
    aps = aspect_score_for(ruler, aspects)

    raw = 50 + hs + rs + aps
    final = clamp(raw)
    return {
        "score": round(final, 1),
        "pos": pos,
        "parts": {"base": 50, "house": hs, "rulership": rs, "aspects": round(aps, 1)},
    }

def score_label(score):
    if score is None: return "bilinmiyor"
    if score >= 75: return "akıcı"
    if score >= 55: return "orta"
    if score >= 35: return "zorlayıcı"
    return "yoğun"

def make_paragraph(root_house, n, result_house, ov_sign, ruler, strength):
    s = strength["score"]
    pos = strength["pos"]
    parts = strength["parts"]
    lbl = score_label(s)

    if s is None:
        return (
            f"{root_house}. evi 1 kabul edip {n} saydığımızda konu **{result_house}. ev** alanına düşüyor "
            f"({HOUSE_MEANINGS[result_house]}). Burç bindirmesi **{ov_sign}** ve yöneticisi **{ruler}**. "
            f"Ancak {ruler} harita verisinde bulunamadığı için skor üretilemedi."
        )

    retro = " (R)" if pos.get("retro") else ""
    return (
        f"{root_house}. evi 1 kabul edip {n} saydığımızda konu **{result_house}. ev** alanına düşüyor "
        f"({HOUSE_MEANINGS[result_house]}). Burç bindirmesi **{ov_sign}**. "
        f"Yönetici **{ruler}** haritada **{pos['house']}. evde** ve **{pos['sign']}** burcunda{retro}. "
        f"Genel akış **{lbl}** (skor **{s}/100**). "
        f"Bileşenler: ev {parts['house']:+}, yöneticilik {parts['rulership']:+}, açılar {parts['aspects']:+}."
    )

def default_questions(root_house: int, n: int, result_house: int, ov_sign: str, ruler: str):
    return [
        f"{HOUSE_MEANINGS[root_house]} konusunun {n}. alt başlığı hangi koşullarda ilerliyor? (Bindirme: {ov_sign})",
        f"Bu tema {HOUSE_MEANINGS[result_house]} alanında nasıl görünür? (Sonuç ev: {result_house})",
        f"Yönetici {ruler} hangi evde/burçta? Bu, konunun çalıştığı kanalı gösterir.",
        f"{ruler}’ün güçlü/zorlayıcı açıları hangileri? (Sağ panelde listelenir.)",
    ]

# =========================
# UI
# =========================
st.set_page_config(page_title="Ev Türetme + Astro-Seek", layout="wide", page_icon="🏠")
st.title("🏠 Ev Türetme (Derived Houses) + Astro-Seek Kopyala/Yapıştır")

with st.sidebar:
    st.header("1) Harita verisi girişi")

    planets_text = st.text_area(
        "Gezegen yerleşimleri (Astro-Seek)",
        height=260,
        placeholder=(
            "Boşluksuz:\n"
            "UranusScorpio26°23’7\nMarsCapricorn3°23’9\n\n"
            "Boşluklu:\n"
            "Uranus: Scorpio 26°23'08''  7  Direct\n"
            "Sun: Sagittarius 4°26'10''  end of 7  Direct\n"
        ),
    )

    cusps_text = st.text_area(
        "House cusps (opsiyonel)",
        height=180,
        placeholder=(
            "Örn:\n"
            "1: Taurus (ASC) 2°50’49’’\n"
            "2: Gemini 4°33’55’’\n"
            "...\n"
            "10: Capricorn (MC) 18°03’09’’"
        ),
    )

    st.divider()
    ruler_system = st.radio("Yöneticilik sistemi", ["Modern", "Klasik"], index=0)

    st.divider()
    st.header("2) Türetme sorusu")
    pick_mode = st.selectbox("Kök ev seçimi", ["Tema seç", "Ev numarası seç"], index=1)
    derived_n = st.number_input("Türetilmiş kaçıncı ev? (n)", min_value=1, max_value=12, value=5, step=1)

    if pick_mode == "Tema seç":
        topic = st.selectbox("Tema", list(TOPIC_TO_ROOT.keys()), index=4)
        root_house = TOPIC_TO_ROOT[topic]
    else:
        topic = None
        root_house = st.number_input("Kök ev numarası", min_value=1, max_value=12, value=7, step=1)

# Parse inputs
planets, planet_errors, ignored_lines = parse_planets_from_text(planets_text)
cusps, cusp_errors = parse_house_cusps_from_text(cusps_text)

st.divider()
col1, col2 = st.columns([1.2, 0.8], gap="large")

with col1:
    st.subheader("✅ Harita verisi durumu")
    if planets:
        st.success(f"Okunan yerleşim: {len(planets)}")
    else:
        st.warning("Gezegen verisi okunamadı. (Debug bölümünde görmezden gelinen satırları kontrol et.)")

    if cusps:
        st.success(f"Okunan cusps: {len(cusps)}/12")
    else:
        st.info("Cusps yoksa sorun değil; aşağıdan manuel seçebilirsin.")

    st.subheader("🏠 Ev cusp burçları (manuel/otomatik)")
    cusp_signs = {}
    for h in range(1, 13):
        default = cusps.get(h, SIGNS[h-1])
        idx = SIGN_TO_IDX.get(default, h-1)
        cusp_signs[h] = st.selectbox(f"{h}. ev burcu", SIGNS, index=idx, key=f"cusp_{h}")

with col2:
    st.subheader("🧪 Debug")
    if planet_errors:
        st.error("Hata verilen satırlar:")
        st.code("\n".join(planet_errors), language="text")
    if ignored_lines:
        st.write("Görmezden gelinen satırlar (format dışı olabilir):")
        st.code("\n".join(ignored_lines[:80]), language="text")
    if planets:
        st.write("Okunan gezegen anahtarları:")
        st.code(", ".join(planets.keys()), language="text")

# Derived result
root_sign = cusp_signs[int(root_house)]
result_house = derived_house(int(root_house), int(derived_n))
ov_sign = overlay_sign(root_sign, int(derived_n))
rulers_map = RULERS_MODERN if ruler_system == "Modern" else RULERS_TRAD
ruler = get_ruler(ov_sign, ruler_system)

# Aspects & score
aspects = compute_aspects(planets) if planets else []
strength = compute_ruler_strength(ruler, planets, aspects, rulers_map)

st.divider()
left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("🎯 Türetme sonucu")
    if topic:
        st.write(f"**Konu:** {topic} → **{int(root_house)}. ev** ({HOUSE_MEANINGS[int(root_house)]})")
    else:
        st.write(f"**Kök ev:** **{int(root_house)}. ev** ({HOUSE_MEANINGS[int(root_house)]})")

    st.write(f"**Kök ev cusp burcu:** **{root_sign}**")
    st.write(f"**Türetilmiş (n):** **{int(derived_n)}**")
    st.write(f"**Sonuç ev:** **{result_house}. ev** ({HOUSE_MEANINGS[result_house]})")
    st.write(f"**Burç bindirmesi:** **{ov_sign}**")
    st.write(f"**{ruler_system} yönetici:** **{ruler}**")

    st.divider()
    st.subheader("📈 Skor + Yorum")
    score = strength["score"]
    if score is None:
        st.warning(f"Yönetici **{ruler}** harita verisinde yok. (Okunan gezegen anahtarlarını Debug’da kontrol et.)")
    else:
        lbl = score_label(score)
        if score >= 75:
            st.success(f"Skor: **{score}/100** → **{lbl}**")
        elif score >= 55:
            st.info(f"Skor: **{score}/100** → **{lbl}**")
        elif score >= 35:
            st.warning(f"Skor: **{score}/100** → **{lbl}**")
        else:
            st.error(f"Skor: **{score}/100** → **{lbl}**")

    st.markdown(make_paragraph(int(root_house), int(derived_n), result_house, ov_sign, ruler, strength))

    st.divider()
    st.subheader("❓ Soru şablonları")
    for i, q in enumerate(default_questions(int(root_house), int(derived_n), result_house, ov_sign, ruler), 1):
        st.write(f"**{i}.** {q}")

with right:
    st.subheader("🧩 Yönetici detayı")
    if strength["pos"]:
        pos = strength["pos"]
        retro = " (R)" if pos.get("retro") else ""
        st.write(f"**{ruler}** → {pos['sign']} {pos['deg']:.3f}° | **{pos['house']}. ev**{retro}")
        st.write("**Puan bileşenleri:**")
        st.json(strength["parts"])
    else:
        st.write("Yönetici konumu yok.")

    st.divider()
    st.subheader("🔭 Otomatik açılar (dereceden)")
    if aspects:
        ruler_asps = [a for a in aspects if a["p1"] == ruler or a["p2"] == ruler]
        st.write(f"Toplam açı: **{len(aspects)}**")
        if ruler_asps:
            st.write(f"Yönetici ({ruler}) açıları: **{len(ruler_asps)}**")
            st.dataframe(ruler_asps, use_container_width=True)
        else:
            st.write("Yöneticinin orb içi ana açısı olmayabilir.")
            st.dataframe(aspects[:20], use_container_width=True)
    else:
        st.write("Açı üretmek için en az 2 yerleşim okunmalı.")

st.divider()
st.code(
    f"derived_house(root={int(root_house)}, n={int(derived_n)}) = {result_house}\n"
    f"overlay_sign(root_sign='{root_sign}', n={int(derived_n)}) = '{ov_sign}'\n"
    f"ruler({ruler_system})('{ov_sign}') = '{ruler}'",
    language="text"
)
