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
    # TR variants
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

# Sign "micro meaning" for overlay, short & readable
SIGN_MICRO = {
    "Koç": ("hız, cesaret, başlangıç", "Hızlı karar, ilk adımı atma, liderlik dürtüsü."),
    "Boğa": ("güven, istikrar, somutluk", "Yavaş ama kalıcı ilerleme; kaynakları sağlamlaştırma."),
    "İkizler": ("iletişim, seçenek, hareket", "Bilgi akışı, bağlantı kurma, çoklu planlar."),
    "Yengeç": ("aidiyet, koruma, duygu", "Güvenli alan ihtiyacı; duygusal bağ üzerinden ilerler."),
    "Aslan": ("görünürlük, gurur, yaratıcılık", "Sahne/ifade; takdir ve kalpten motivasyon."),
    "Başak": ("detay, düzen, verim", "Plan–program, iyileştirme; küçük adımlarla büyütme."),
    "Terazi": ("denge, ortaklık, uyum", "İşbirliği, adalet; karşılıklı kazanım arar."),
    "Akrep": ("yoğunluk, dönüşüm, kontrol", "Derinleşme; kriz/bağlılık temasıyla güçlenme."),
    "Yay": ("vizyon, büyüme, ufuk", "Uzaklar/eğitim/fırsat; risk–ödül dengesi önemli."),
    "Oğlak": ("hedef, disiplin, yapı", "Uzun vadeli plan; sorumlulukla somut sonuç."),
    "Kova": ("özgürlük, yenilik, farklılık", "Kalabalıklar/projeler; sıra dışı çözüm üretir."),
    "Balık": ("sezgi, akış, anlam", "Bırakma–kabullenme; yaratıcı/ruhsal kanal."),
}

# Planets -> Turkish keys
PLANET_ALIASES = {
    "Sun": "Güneş", "Moon": "Ay", "Mercury": "Merkür", "Venus": "Venüs", "Mars": "Mars",
    "Jupiter": "Jüpiter", "Saturn": "Satürn", "Uranus": "Uranüs", "Neptune": "Neptün", "Pluto": "Plüton",
    "Node": "KuzeyAyDüğümü", "Lilith": "Lilith", "Chiron": "Chiron", "Fortune": "Fortuna", "Vertex": "Vertex",
    # passthrough
    "Güneş": "Güneş", "Ay": "Ay", "Merkür": "Merkür", "Venüs": "Venüs", "Mars": "Mars",
    "Jüpiter": "Jüpiter", "Satürn": "Satürn", "Uranüs": "Uranüs", "Neptün": "Neptün", "Plüton": "Plüton",
    "KuzeyAyDüğümü": "KuzeyAyDüğümü", "Fortuna": "Fortuna",
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

def normalize_sign(token: str):
    token = token.strip()
    if token in SIGN_ALIASES:
        return SIGN_ALIASES[token]
    for k, v in SIGN_ALIASES.items():
        if k.lower() == token.lower():
            return v
    return None

def normalize_planet(raw: str) -> str:
    raw = raw.strip().strip(":").replace("\t", " ").strip()
    raw_nospace = raw.replace(" ", "")

    # Node / Lilith (M) variants
    if raw_nospace.lower().startswith("node"):
        return PLANET_ALIASES.get("Node", "KuzeyAyDüğümü")
    if raw_nospace.lower().startswith("lilith"):
        return PLANET_ALIASES.get("Lilith", "Lilith")

    raw_clean = re.sub(r"[^A-Za-zÇĞİÖŞÜçğıöşü]", "", raw)

    if raw in PLANET_ALIASES:
        return PLANET_ALIASES[raw]
    if raw_nospace in PLANET_ALIASES:
        return PLANET_ALIASES[raw_nospace]
    if raw_clean in PLANET_ALIASES:
        return PLANET_ALIASES[raw_clean]

    for en in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto","Chiron","Fortune","Vertex","Node","Lilith"]:
        if en.lower() in raw_nospace.lower():
            return PLANET_ALIASES.get(en, en)

    return raw_clean or raw

def get_ruler(sign: str, system: str) -> str:
    return (RULERS_MODERN if system == "Modern" else RULERS_TRAD)[sign]

# =========================
# PARSERS (Astro-Seek)
# =========================
# Spaced format:
# Sun: Sagittarius 4°26’10’’  end of 7  Direct
# NOTE: \D+ for unicode quotes
PLANET_LINE_RE = re.compile(
    r"""^\s*
    (?P<planet>[A-Za-zÇĞİÖŞÜçğıöşü]+(?:\s*\(M\))?)\s*:?\s*
    (?P<sign>[A-Za-zÇĞİÖŞÜçğıöşü♈♉♊♋♌♍♎♏♐♑♒♓]+)\s+
    (?P<deg>\d{1,2})\s*°\s*
    (?P<min>\d{1,2})\D+
    (?:(?P<sec>\d{1,2})\D+)?      # seconds optional, any non-digit separators
    (?:(?:end\s+of\s+)?(?P<house>\d{1,2}))\s*
    (?P<motion>Direct|Retrograde|R)?\s*$
    """,
    re.IGNORECASE | re.VERBOSE
)

# Compact format:
# UranusScorpio26°23’7
PLANET_COMPACT_RE = re.compile(
    r"""^\s*
    (?P<planet>[A-Za-zÇĞİÖŞÜçğıöşü]+)
    (?P<sign>[A-Za-zÇĞİÖŞÜçğıöşü♈♉♊♋♌♍♎♏♐♑♒♓]+)
    (?P<deg>\d{1,2})\s*°\s*
    (?P<min>\d{1,2})\D+
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

        # ignore lunar phase lines
        if any(w in line.lower() for w in ["disseminating", "balsamic", "gibbous", "crescent", "phase"]):
            ignored.append(line)
            continue

        m = PLANET_LINE_RE.match(line)
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

        motion = (m.groupdict().get("motion") or "").strip().lower()
        retro = motion in ["retrograde", "r"]

        deg_float = deg + minute / 60.0 + sec / 3600.0
        lon = SIGN_TO_IDX[sign] * 30.0 + deg_float

        planets[planet] = {"sign": sign, "deg": deg_float, "house": house, "lon": lon, "retro": retro}

    return planets, errors, ignored

def parse_house_cusps_from_text(text: str):
    cusps = {}
    errors = []
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
# ASPECTS
# =========================
ASPECTS_DEF = [
    ("conjunction", 0, 6),
    ("sextile", 60, 4.5),
    ("square", 90, 6),
    ("trine", 120, 6),
    ("opposition", 180, 6),
]
ASPECT_WEIGHTS = {"conjunction": 10, "sextile": 8, "trine": 12, "square": -12, "opposition": -14}
ASPECT_TR_LABEL = {
    "conjunction": "kavuşum",
    "sextile": "sekstil",
    "square": "kare",
    "trine": "üçgen",
    "opposition": "karşıt",
}

def aspect_nature(a_type: str) -> str:
    if a_type in ["trine", "sextile"]:
        return "destek"
    if a_type in ["square", "opposition"]:
        return "zorlayıcı"
    return "karışık"

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
    if score is None:
        return "bilinmiyor"
    if score >= 75:
        return "akıcı"
    if score >= 55:
        return "orta"
    if score >= 35:
        return "zorlayıcı"
    return "yoğun"

def pick_ruler_with_fallback(ov_sign: str, primary_system: str, planets: dict):
    """
    If chosen ruler not found in chart, fallback to other system's ruler.
    Returns (ruler_name, used_system, fallback_used: bool)
    """
    primary_map = RULERS_MODERN if primary_system == "Modern" else RULERS_TRAD
    alt_map = RULERS_TRAD if primary_system == "Modern" else RULERS_MODERN

    r1 = primary_map[ov_sign]
    if r1 in planets:
        return r1, primary_system, False

    alt_system = "Klasik" if primary_system == "Modern" else "Modern"
    r2 = alt_map[ov_sign]
    if r2 in planets:
        return r2, alt_system, True

    # neither present
    return r1, primary_system, False

def short_action_tips(ov_sign: str, ruler_house: int | None):
    """
    Simple, readable action tips.
    """
    tips = []
    if ov_sign == "Yay":
        tips.append("Eğitim/sertifika, yurtdışı bağlantı veya yayınlama gibi 'ufuk genişleten' bir hamle ekle.")
        tips.append("Riskli büyümeyi plan–bütçe–takvim ile çerçevele.")
    elif ov_sign == "Başak":
        tips.append("Planı küçült: ölç–iyileştir–tekrar et (verim odaklı).")
        tips.append("Detay/sağlık/iş rutini aksarsa tema zorlanır.")
    elif ov_sign == "Kova":
        tips.append("Yeni yöntem/teknoloji veya farklı bir network kanalı dene.")
        tips.append("Esneklik + net sınır: özgürlük ihtiyacını yönet.")
    else:
        tips.append("Bindirme burcunun 'tarzına' uygun küçük bir somut adım seç ve 2 hafta takip et.")

    if ruler_house is not None:
        tips.append(f"Yönetici {ruler_house}. evde: aksiyonu '{HOUSE_MEANINGS[ruler_house]}' kanalından başlatmak daha verimli olur.")
    return tips[:3]

def make_readable_comment(root_house, n, result_house, ov_sign, ruler, strength, aspects, topic_name=None, ruler_used_system=None, fallback_used=False):
    """
    Human-friendly comment block: summary + bullets + reasons + tips
    """
    s = strength["score"]
    lbl = score_label(s)

    # Micro meaning
    micro_tags, micro_desc = SIGN_MICRO.get(ov_sign, ("", ""))

    # Header line
    subject = topic_name if topic_name else f"{root_house}. ev ({HOUSE_MEANINGS[root_house]})"
    header = (
        f"**Özet:** **{subject}** konusunun **{n}. alt başlığı**, "
        f"**{result_house}. ev** ({HOUSE_MEANINGS[result_house]}) alanında çalışıyor. "
        f"Genel akış: **{lbl}**."
    )

    sys_note = ""
    if ruler_used_system:
        sys_note = f" (**Yönetici sistemi:** {ruler_used_system})"
    if fallback_used:
        sys_note += " _(haritada bulunmadığı için alternatif yönetici kullanıldı)_"

    base_lines = [
        f"- **Kök:** {root_house}. ev → {HOUSE_MEANINGS[root_house]}",
        f"- **Sonuç:** {result_house}. ev → {HOUSE_MEANINGS[result_house]}",
        f"- **Bindirme burcu:** **{ov_sign}** ({micro_tags})",
        f"  - {micro_desc}" if micro_desc else "",
        f"- **Yönetici:** **{ruler}**{sys_note}",
    ]
    base_block = "\n".join([x for x in base_lines if x])

    if s is None or strength["pos"] is None:
        return (
            header + "\n\n" +
            base_block + "\n\n" +
            "⚠️ Yönetici gezegen harita verisinde bulunamadığı için skor/yorum sınırlı."
        )

    pos = strength["pos"]
    retro = " (R)" if pos.get("retro") else ""
    ruler_loc = f"- **Yönetici konumu:** **{pos['house']}. ev / {pos['sign']}**{retro}"
    parts = strength["parts"]

    # Ruler aspects
    ruler_asps = [a for a in aspects if a["p1"] == ruler or a["p2"] == ruler]
    ruler_asps = sorted(ruler_asps, key=lambda x: x.get("orb", 99))[:5]

    asp_lines = []
    for a in ruler_asps:
        other = a["p2"] if a["p1"] == ruler else a["p1"]
        tr = ASPECT_TR_LABEL.get(a["type"], a["type"])
        nat = aspect_nature(a["type"])
        icon = "✅" if nat == "destek" else ("⚠️" if nat == "zorlayıcı" else "⚖️")
        asp_lines.append(f"  - {icon} {other} ile **{tr}** (orb {a['orb']}) → *{nat}*")

    if asp_lines:
        asp_block = "**Yönetici açıları (en yakınlar):**\n" + "\n".join(asp_lines)
    else:
        asp_block = "**Yönetici açıları:** belirgin orb içi majör açı görünmüyor."

    score_block = (
        f"**Skor:** **{s}/100** → **{lbl}**\n\n"
        f"**Skor neden böyle?**\n"
        f"- Ev vurgusu: {parts['house']:+}\n"
        f"- Yöneticilik (domicile/detriment): {parts['rulership']:+}\n"
        f"- Açılar: {parts['aspects']:+}\n"
    )

    interp = (
        "**Ne anlatıyor?**\n"
        f"- {ov_sign} bindirmesi temayı **{micro_tags or 'o burcun tarzı'}** üzerinden çalıştırır.\n"
        f"- Yönetici {ruler}’ün **{pos['house']}. evde** olması, konunun en çok **{HOUSE_MEANINGS[int(pos['house'])]}** kanalından aktığını gösterir.\n"
    )

    tips = short_action_tips(ov_sign, int(pos["house"]))
    tips_block = "**Hızlı aksiyon:**\n" + "\n".join([f"- {t}" for t in tips])

    return (
        header + "\n\n" +
        base_block + "\n" +
        ruler_loc + "\n\n" +
        score_block + "\n" +
        asp_block + "\n\n" +
        interp + "\n" +
        tips_block
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
            "Boşluklu örnek:\n"
            "Sun: Sagittarius 4°26’10’’  end of 7  Direct\n"
            "Moon: Leo 0°53’40’’  4  Direct\n\n"
            "Boşluksuz örnek:\n"
            "UranusScorpio26°23’7\nMarsCapricorn3°23’9\n"
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
    allow_fallback = st.checkbox("Yönetici bulunamazsa alternatif yöneticiye düş (önerilir)", value=True)

    st.divider()
    st.header("2) Türetme sorusu")
    pick_mode = st.selectbox("Kök ev seçimi", ["Tema seç", "Ev numarası seç"], index=0)
    derived_n = st.number_input("Türetilmiş kaçıncı ev? (n)", min_value=1, max_value=12, value=5, step=1)

    if pick_mode == "Tema seç":
        topic = st.selectbox("Tema", list(TOPIC_TO_ROOT.keys()), index=1)
        root_house = TOPIC_TO_ROOT[topic]
        topic_name = topic
    else:
        topic = None
        topic_name = None
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
        st.warning("Gezegen verisi okunamadı. (Debug bölümünde görmezden gelen satırları kontrol et.)")

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

# Choose ruler (with fallback)
if allow_fallback:
    ruler, used_system, fallback_used = pick_ruler_with_fallback(ov_sign, ruler_system, planets)
else:
    ruler = get_ruler(ov_sign, ruler_system)
    used_system = ruler_system
    fallback_used = False

# Aspects & score
aspects = compute_aspects(planets) if planets else []
rulers_map_used = RULERS_MODERN if used_system == "Modern" else RULERS_TRAD
strength = compute_ruler_strength(ruler, planets, aspects, rulers_map_used)

st.divider()
left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("🎯 Türetme sonucu")
    if topic_name:
        st.write(f"**Konu:** {topic_name} → **{int(root_house)}. ev** ({HOUSE_MEANINGS[int(root_house)]})")
    else:
        st.write(f"**Kök ev:** **{int(root_house)}. ev** ({HOUSE_MEANINGS[int(root_house)]})")

    st.write(f"**Kök ev cusp burcu:** **{root_sign}**")
    st.write(f"**Türetilmiş (n):** **{int(derived_n)}**")
    st.write(f"**Sonuç ev:** **{result_house}. ev** ({HOUSE_MEANINGS[result_house]})")
    st.write(f"**Burç bindirmesi:** **{ov_sign}**")
    st.write(f"**Yönetici:** **{ruler}** (sistem: {used_system})" + (" — _alternatif yönetici kullanıldı_" if fallback_used else ""))

    st.divider()
    st.subheader("📈 Skor + Yorum")

    score = strength["score"]
    if score is None:
        st.warning(f"Yönetici **{ruler}** harita verisinde yok. (Debug → Okunan gezegen anahtarlarına bak.)")
        st.markdown(make_readable_comment(int(root_house), int(derived_n), result_house, ov_sign, ruler, strength, aspects, topic_name, used_system, fallback_used))
    else:
        # nice metric-like line
        st.metric("Skor", f"{score}/100", score_label(score))
        st.markdown(make_readable_comment(int(root_house), int(derived_n), result_house, ov_sign, ruler, strength, aspects, topic_name, used_system, fallback_used))

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
        st.write(f"Yönetici ({ruler}) açıları: **{len(ruler_asps)}**")
        if ruler_asps:
            # add nature column for readability
            rows = []
            for a in sorted(ruler_asps, key=lambda x: x.get("orb", 99)):
                other = a["p2"] if a["p1"] == ruler else a["p1"]
                rows.append({
                    "diğer": other,
                    "açı": ASPECT_TR_LABEL.get(a["type"], a["type"]),
                    "doğa": aspect_nature(a["type"]),
                    "orb": a["orb"],
                })
            st.dataframe(rows, use_container_width=True)
        else:
            st.write("Yöneticinin orb içi majör açısı olmayabilir.")
    else:
        st.write("Açı üretmek için en az 2 yerleşim okunmalı.")

st.divider()
st.code(
    f"derived_house(root={int(root_house)}, n={int(derived_n)}) = {result_house}\n"
    f"overlay_sign(root_sign='{root_sign}', n={int(derived_n)}) = '{ov_sign}'\n"
    f"ruler_used('{ov_sign}') = '{ruler}' (system={used_system}, fallback={fallback_used})",
    language="text"
)
