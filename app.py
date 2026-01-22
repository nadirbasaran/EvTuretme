import streamlit as st
import re
from math import fabs

# =========================
# CONSTANTS
# =========================
SIGNS = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
SIGN_TO_IDX = {s: i for i, s in enumerate(SIGNS)}
IDX_TO_SIGN = {i: s for i, s in enumerate(SIGNS)}

# Astro-Seek / common sign aliases (TR+EN + symbols)
SIGN_ALIASES = {
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
    # EN
    "Aries": "Koç",
    "Taurus": "Boğa",
    "Gemini": "İkizler",
    "Cancer": "Yengeç",
    "Leo": "Aslan",
    "Virgo": "Başak",
    "Libra": "Terazi",
    "Scorpio": "Akrep",
    "Sagittarius": "Yay",
    "Capricorn": "Oğlak",
    "Aquarius": "Kova",
    "Pisces": "Balık",
    # Symbols
    "♈": "Koç", "♉": "Boğa", "♊": "İkizler", "♋": "Yengeç",
    "♌": "Aslan", "♍": "Başak", "♎": "Terazi", "♏": "Akrep",
    "♐": "Yay", "♑": "Oğlak", "♒": "Kova", "♓": "Balık",
}

PLANET_ALIASES = {
    # EN -> TR (you can extend)
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
    # TR passthrough
    "Güneş": "Güneş", "Ay": "Ay", "Merkür": "Merkür", "Venüs": "Venüs",
    "Mars": "Mars", "Jüpiter": "Jüpiter", "Satürn": "Satürn", "Uranüs": "Uranüs",
    "Neptün": "Neptün", "Plüton": "Plüton",
    # node etc. (optional)
    "Node": "KuzeyAyDüğümü",
    "NorthNode": "KuzeyAyDüğümü",
    "SouthNode": "GüneyAyDüğümü",
    "Chiron": "Chiron",
    "Lilith": "Lilith",
}

RULERS_MODERN = {
    "Koç": "Mars",
    "Boğa": "Venüs",
    "İkizler": "Merkür",
    "Yengeç": "Ay",
    "Aslan": "Güneş",
    "Başak": "Merkür",
    "Terazi": "Venüs",
    "Akrep": "Plüton",
    "Yay": "Jüpiter",
    "Oğlak": "Satürn",
    "Kova": "Uranüs",
    "Balık": "Neptün",
}
RULERS_TRAD = {
    "Koç": "Mars",
    "Boğa": "Venüs",
    "İkizler": "Merkür",
    "Yengeç": "Ay",
    "Aslan": "Güneş",
    "Başak": "Merkür",
    "Terazi": "Venüs",
    "Akrep": "Mars",
    "Yay": "Jüpiter",
    "Oğlak": "Satürn",
    "Kova": "Satürn",
    "Balık": "Jüpiter",
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
def normalize_sign(s: str) -> str | None:
    s = s.strip()
    if s in SIGN_ALIASES:
        return SIGN_ALIASES[s]
    # try loose match (case-insensitive)
    for k, v in SIGN_ALIASES.items():
        if k.lower() == s.lower():
            return v
    return None

def normalize_planet(p: str) -> str:
    p = p.strip()
    if p in PLANET_ALIASES:
        return PLANET_ALIASES[p]
    # strip punctuation
    p2 = re.sub(r"[^A-Za-zÇĞİÖŞÜçğıöşü]", "", p)
    return PLANET_ALIASES.get(p2, p2)

def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def derived_house(root_house: int, n: int) -> int:
    return ((root_house - 1) + (n - 1)) % 12 + 1

def overlay_sign(root_sign: str, n: int) -> str:
    idx = SIGN_TO_IDX[root_sign]
    return IDX_TO_SIGN[(idx + (n - 1)) % 12]

def get_ruler(sign: str, system: str) -> str:
    return (RULERS_MODERN if system == "Modern" else RULERS_TRAD)[sign]

# =========================
# PARSERS (Astro-Seek paste)
# =========================
def parse_planets_from_text(text: str):
    """
    Tries to parse lines like:
      Sun ♐ 4°26' 7
      Moon Leo 0 53 4
      Mercury ♏ 16°24' 7
    Returns:
      planets dict: {planet: {"sign":..., "deg": float, "house": int, "lon": float}}
      errors list: lines we couldn't parse
    """
    planets = {}
    errors = []

    # Flexible regex: find deg & min & (house at end)
    # - captures last number as house
    dm_house = re.compile(r"(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})\s*$")

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) < 3:
            errors.append(line)
            continue

        planet_raw = parts[0]
        planet = normalize_planet(planet_raw)

        # detect sign token: look for any alias present as a standalone token
        sign = None
        for tok in parts[1:]:
            ns = normalize_sign(tok)
            if ns in SIGN_TO_IDX:
                sign = ns
                break

        if sign is None:
            # fallback: try to find any sign alias anywhere in line
            for k in SIGN_ALIASES.keys():
                if re.search(rf"\b{re.escape(k)}\b", line):
                    sign = SIGN_ALIASES[k]
                    break

        if sign is None:
            errors.append(line)
            continue

        m = dm_house.search(line)
        if not m:
            errors.append(line)
            continue

        deg = int(m.group(1))
        minute = int(m.group(2))
        house = int(m.group(3))
        deg_float = deg + minute / 60.0

        lon = SIGN_TO_IDX[sign] * 30.0 + deg_float

        planets[planet] = {"sign": sign, "deg": deg_float, "house": house, "lon": lon}

    return planets, errors

def parse_house_cusps_from_text(text: str):
    """
    Tries to parse 1..12 house cusp sign list from pasted text.
    Accepts formats like:
      1: Aries
      House 1: ♈
      1st house: Leo
      1 Koç
    Returns:
      cusps dict {1:"Koç",...,12:"Balık"}, errors list
    """
    cusps = {}
    errors = []

    # Find house number then a sign token
    # Example matches: "1", "1st", "House 1", "1. house"
    house_re = re.compile(r"(?i)\b(?:house\s*)?([1-9]|1[0-2])(?:st|nd|rd|th)?\b")

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        hm = house_re.search(line)
        if not hm:
            # ignore lines that don't look like cusps
            continue

        h = int(hm.group(1))

        # find sign token in line
        sign = None
        # try tokens first
        for tok in line.split():
            ns = normalize_sign(tok)
            if ns in SIGN_TO_IDX:
                sign = ns
                break
        if sign is None:
            # search anywhere
            for k in SIGN_ALIASES.keys():
                if re.search(rf"\b{re.escape(k)}\b", line):
                    sign = SIGN_ALIASES[k]
                    break

        if sign is None:
            errors.append(line)
            continue

        cusps[h] = sign

    # If user pasted something and we found nothing, treat as error
    if text.strip() and len(cusps) == 0:
        errors.append("House cusp metni algılanamadı. Lütfen Astro-Seek 'House cusps' satırlarını yapıştır.")

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
    """
    planets values must include 'lon'
    Returns list of aspects: {"p1","p2","type","orb"}
    """
    keys = list(planets.keys())
    aspects = []
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
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
# SCORING + TEXT
# =========================
ANGULAR = {1, 4, 7, 10}
SUCCEDENT = {2, 5, 8, 11}
CADENT = {3, 6, 9, 12}

def house_score(house: int) -> int:
    if house in ANGULAR:
        return 12
    if house in SUCCEDENT:
        return 6
    return 0

ASPECT_WEIGHTS = {
    "conjunction": 10,
    "sextile": 8,
    "trine": 12,
    "square": -12,
    "opposition": -14,
}

def rulership_score(planet: str, sign: str, rulers_map: dict) -> int:
    # rulership
    if rulers_map.get(sign) == planet:
        return 10

    # detriment (very simplified)
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
        w = max(0.0, 1.0 - orb / 6.0)  # 0..1
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
        "parts": {
            "base": 50,
            "house": hs,
            "rulership": rs,
            "aspects": round(aps, 1),
        }
    }

def score_label(score: float | None) -> str:
    if score is None:
        return "bilinmiyor"
    if score >= 75:
        return "akıcı"
    if score >= 55:
        return "orta"
    if score >= 35:
        return "zorlayıcı"
    return "yoğun"

def make_paragraph(root_house, n, result_house, ov_sign, ruler, strength):
    s = strength["score"]
    pos = strength["pos"]
    parts = strength["parts"]
    lbl = score_label(s)

    if s is None:
        return (
            f"{root_house}. evi 1 kabul edip {n} saydığımızda konu {result_house}. evde ({HOUSE_MEANINGS[result_house]}) çalışıyor. "
            f"Burç bindirmesi {ov_sign} ve yöneticisi {ruler}. Ancak harita verisinde **{ruler}** bulunamadığı için skor/ton analizi yapılamadı."
        )

    return (
        f"{root_house}. evi 1 kabul edip {n} saydığımızda konu **{result_house}. ev** alanına düşüyor "
        f"({HOUSE_MEANINGS[result_house]}). Burç bindirmesi **{ov_sign}** olduğu için süreç "
        f"{ov_sign} temalarıyla (tarz/işleyiş) şekilleniyor. Bu yapının ana anahtarı **{ruler}**: "
        f"{ruler} haritada **{pos['house']}. evde** ve **{pos['sign']}** burcunda. "
        f"Genel akış **{lbl}** (skor **{s}/100**). "
        f"Puan bileşenleri: ev {parts['house']:+}, yöneticilik {parts['rulership']:+}, açılar {parts['aspects']:+}. "
        f"Özetle, sonuçta en çok {ruler}’ün açıları ve bulunduğu evin gündemleri belirleyici olur."
    )

def default_questions(root_house: int, n: int, result_house: int, ov_sign: str, ruler: str) -> list[str]:
    root_mean = HOUSE_MEANINGS[root_house]
    res_mean = HOUSE_MEANINGS[result_house]
    return [
        f"{root_mean} konusunun {n}. alt başlığı hangi koşullarda gelişiyor? (Bindirme: {ov_sign})",
        f"Bu konu en çok {res_mean} alanında nasıl görünür oluyor? (Sonuç ev: {result_house})",
        f"Yönetici {ruler} haritada nerede? (Ev/burç) Bu konu ‘nereden çalışıyor’u gösterir.",
        f"{ruler}’ün güçlü/zorlayıcı açıları hangileri? (Skor bunu özetler; detay için aspect listesi.)",
    ]

# =========================
# APP
# =========================
st.set_page_config(page_title="Ev Türetme + Harita Girişi (Astro-Seek)", layout="wide", page_icon="🏠")
st.title("🏠 Ev Türetme (Derived Houses) + Astro-Seek Harita Girişi")

st.caption("Önce harita verisini Astro-Seek’ten kopyala-yapıştır → sonra türetme sorunu sor → yönetici gezegene göre skor + paragraf yorum al.")

with st.sidebar:
    st.header("1) Harita verisi girişi")
    st.write("Astro-Seek’ten **gezegen listesi**ni (Sun/Moon/Mercury...) kopyalayıp buraya yapıştır.")
    planets_text = st.text_area(
        "Gezegen yerleşimleri (kopyala-yapıştır)",
        height=220,
        placeholder="Örnek:\nSun ♐ 4°26' 7\nMoon ♌ 0°53' 4\nMercury ♏ 16°24' 7\nVenus ♏ 3°03' 7\n...",
    )

    st.write("Astro-Seek’ten **House cusps** satırlarını kopyalayıp buraya yapıştır (1–12).")
    cusps_text = st.text_area(
        "House cusps (kopyala-yapıştır)",
        height=220,
        placeholder="Örnek:\n1st house: Leo\n2nd house: Virgo\n...\n12th house: Cancer",
    )

    st.divider()
    ruler_system = st.radio("Yöneticilik sistemi", ["Modern", "Klasik"], index=0)

    st.divider()
    st.header("2) Türetme sorusu")
    pick_mode = st.selectbox("Kök ev seçimi", ["Tema seç", "Ev numarası seç"], index=0)
    derived_n = st.number_input("Türetilmiş kaçıncı ev? (n)", min_value=1, max_value=12, value=6, step=1)

    if pick_mode == "Tema seç":
        topic = st.selectbox("Tema", list(TOPIC_TO_ROOT.keys()), index=4)
        root_house = TOPIC_TO_ROOT[topic]
    else:
        topic = None
        root_house = st.number_input("Kök ev numarası", min_value=1, max_value=12, value=5, step=1)

# Parse inputs
planets, planet_errors = parse_planets_from_text(planets_text)
cusps, cusp_errors = parse_house_cusps_from_text(cusps_text)

# If cusps missing some houses, fall back to manual selectboxes
st.divider()
col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.subheader("✅ Harita verisi durumu")
    if planets:
        st.success(f"Gezegenler okundu: {len(planets)} adet")
    else:
        st.warning("Gezegen verisi yok veya okunamadı. (Soldaki kutuya Astro-Seek gezegen satırlarını yapıştır.)")

    if cusps and len(cusps) >= 8:
        st.success(f"House cusps okundu: {len(cusps)}/12")
    else:
        st.warning("House cusps eksik/okunamadı. Aşağıdan manuel seçebilirsin (1–12).")

    # Manual cusps fallback / completion
    st.subheader("🏠 Ev cusp burçları (otomatik + manuel tamamla)")
    cusp_signs = {}
    for h in range(1, 13):
        default = cusps.get(h, SIGNS[h-1])
        idx = SIGN_TO_IDX.get(default, h-1)
        cusp_signs[h] = st.selectbox(f"{h}. ev burcu", SIGNS, index=idx, key=f"cusp_{h}")

with col2:
    st.subheader("🧪 Debug")
    if planet_errors:
        st.error("Okunamayan gezegen satırları:")
        st.code("\n".join(planet_errors), language="text")
    else:
        st.write("Gezegen satırlarında hata yok (veya veri yok).")

    if cusp_errors:
        st.error("Okunamayan cusp satırları / uyarılar:")
        st.code("\n".join(cusp_errors), language="text")
    else:
        st.write("Cusp satırlarında hata yok (veya veri yok).")

# Run derived logic
root_sign = cusp_signs[int(root_house)]
result_house = derived_house(int(root_house), int(derived_n))
ov_sign = overlay_sign(root_sign, int(derived_n))
rulers_map = RULERS_MODERN if ruler_system == "Modern" else RULERS_TRAD
ruler = get_ruler(ov_sign, ruler_system)

# Compute aspects automatically (if enough planets with degrees)
aspects = compute_aspects(planets) if planets else []

# Strength / score
strength = compute_ruler_strength(ruler, planets, aspects, rulers_map)

st.divider()
left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("🎯 Türetme sonucu")
    if topic:
        st.write(f"**Konu (kök ev):** {topic} → **{int(root_house)}. ev** ({HOUSE_MEANINGS[int(root_house)]})")
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
        st.warning(f"Yönetici gezegen **{ruler}** harita verisinde bulunamadı. (Gezegen satırlarında isim farklı olabilir.)")
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
        st.write(f"**{ruler}** → {pos['sign']} {pos['deg']:.2f}° | **{pos['house']}. ev**")
        st.write("**Puan bileşenleri:**")
        st.json(strength["parts"])
    else:
        st.write("Yönetici konumu yok.")

    st.divider()
    st.subheader("🔭 Otomatik açılar (dereceden)")
    if aspects:
        # show only aspects involving ruler first
        ruler_asps = [a for a in aspects if a["p1"] == ruler or a["p2"] == ruler]
        st.write(f"Toplam açı sayısı: **{len(aspects)}**")
        if ruler_asps:
            st.write(f"Yönetici ({ruler}) açıları: **{len(ruler_asps)}**")
            st.dataframe(ruler_asps, use_container_width=True)
        else:
            st.write("Yöneticinin yakalanan ana açısı yok (orb dışında olabilir).")
            st.dataframe(aspects[:20], use_container_width=True)
    else:
        st.write("Açı üretmek için en az 2 gezegenin derece bilgisi lazım.")

st.divider()
st.code(
    f"derived_house(root={int(root_house)}, n={int(derived_n)}) = {result_house}\n"
    f"overlay_sign(root_sign='{root_sign}', n={int(derived_n)}) = '{ov_sign}'\n"
    f"ruler({ruler_system})('{ov_sign}') = '{ruler}'",
    language="text"
)
