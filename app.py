import streamlit as st

# ----------------------------
# CONSTANTS / MAPS
# ----------------------------
SIGNS = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
SIGN_TO_IDX = {s: i for i, s in enumerate(SIGNS)}
IDX_TO_SIGN = {i: s for i, s in enumerate(SIGNS)}

RULERS_MODERN = {
    "Koç": "Mars",
    "Boğa": "Venüs",
    "İkizler": "Merkür",
    "Yengeç": "Ay",
    "Aslan": "Güneş",
    "Başak": "Merkür",
    "Terazi": "Venüs",
    "Akrep": "Plüton",   # modern
    "Yay": "Jüpiter",
    "Oğlak": "Satürn",
    "Kova": "Uranüs",    # modern
    "Balık": "Neptün",   # modern
}
RULERS_TRAD = {
    "Koç": "Mars",
    "Boğa": "Venüs",
    "İkizler": "Merkür",
    "Yengeç": "Ay",
    "Aslan": "Güneş",
    "Başak": "Merkür",
    "Terazi": "Venüs",
    "Akrep": "Mars",     # klasik
    "Yay": "Jüpiter",
    "Oğlak": "Satürn",
    "Kova": "Satürn",    # klasik
    "Balık": "Jüpiter",  # klasik
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

# Hazır “root house” konu seçimi (isteğe bağlı)
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

# ----------------------------
# FUNCTIONS
# ----------------------------
def derived_house(root_house: int, n: int) -> int:
    """Ev türetme: root'u 1 kabul edip n'inci evi bul."""
    return ((root_house - 1) + (n - 1)) % 12 + 1

def overlay_sign(root_sign: str, n: int) -> str:
    """Kök evin burcunu 1 kabul edip, n'inci bindirme burcunu bul."""
    idx = SIGN_TO_IDX[root_sign]
    return IDX_TO_SIGN[(idx + (n - 1)) % 12]

def get_ruler(sign: str, system: str) -> str:
    return (RULERS_MODERN if system == "Modern" else RULERS_TRAD)[sign]

def default_questions(root_house: int, n: int, result_house: int, ov_sign: str, ruler: str) -> list[str]:
    root_mean = HOUSE_MEANINGS[root_house]
    res_mean = HOUSE_MEANINGS[result_house]
    # Basit ama işe yarayan şablonlar
    return [
        f"{root_mean} konusunun {n}. alt başlığı hangi koşullarda gelişiyor? (Burç bindirmesi: {ov_sign})",
        f"Bu konu daha çok {res_mean} alanında mı görünür oluyor? Orada ne tetikler?",
        f"Yönetici gezegen {ruler}. {ruler} haritada nerede ve hangi açılarda? (Cevabın tonu burada netleşir.)",
        f"Konuda ‘çözüm/akış’ mu, ‘zorlanma/kriz’ mi baskın? Bunu {ov_sign} burcu ve {ruler} durumu belirler.",
    ]

# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title="Ev Türetme (Derived Houses)", layout="wide", page_icon="🏠")
st.title("🏠 Ev Türetme Otomasyonu (Derived Houses)")

st.caption("12 evin cusp burcunu gir → kök evi seç → türetilmiş evi seç → sonuç ev + burç bindirmesi + yönetici + soru şablonları.")

with st.sidebar:
    st.header("⚙️ Ayarlar")
    ruler_system = st.radio("Yöneticilik sistemi", ["Modern", "Klasik"], index=0)
    st.divider()

    st.subheader("1) Ev cusp burçları")
    cusp_signs = {}
    for h in range(1, 13):
        cusp_signs[h] = st.selectbox(f"{h}. ev burcu", SIGNS, index=(h-1), key=f"cusp_{h}")

    st.divider()
    st.subheader("2) Kök ev seçimi")

    colA, colB = st.columns([1, 1])
    with colA:
        pick_mode = st.selectbox("Seçim modu", ["Tema seç", "Ev numarası seç"], index=0)
    with colB:
        derived_n = st.number_input("Türetilmiş kaçıncı ev? (n)", min_value=1, max_value=12, value=2, step=1)

    if pick_mode == "Tema seç":
        topic = st.selectbox("Tema", list(TOPIC_TO_ROOT.keys()), index=7)  # default: Kriz/Paylaşımlar
        root_house = TOPIC_TO_ROOT[topic]
    else:
        root_house = st.number_input("Kök ev numarası", min_value=1, max_value=12, value=8, step=1)
        topic = None

# ----------------------------
# CALCULATION
# ----------------------------
root_sign = cusp_signs[root_house]
result_house = derived_house(root_house, int(derived_n))
ov_sign = overlay_sign(root_sign, int(derived_n))
ruler = get_ruler(ov_sign, ruler_system)

# ----------------------------
# OUTPUT
# ----------------------------
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.subheader("✅ Sonuç")
    if topic:
        st.write(f"**Konu (kök ev):** {topic} → **{root_house}. ev** ({HOUSE_MEANINGS[root_house]})")
    else:
        st.write(f"**Kök ev:** **{root_house}. ev** ({HOUSE_MEANINGS[root_house]})")

    st.write(f"**Kök evin cusp burcu:** **{root_sign}**")
    st.write(f"**Türetilmiş ev (n):** **{int(derived_n)}**")
    st.write(f"**Sonuç ev numarası:** **{result_house}. ev** ({HOUSE_MEANINGS[result_house]})")
    st.write(f"**Burç bindirmesi (kök evden sayınca):** **{ov_sign}**")
    st.write(f"**{ruler_system} yönetici:** **{ruler}**")

    st.divider()
    st.subheader("🧩 Otomatik yorum iskeleti")
    st.markdown(
        f"""
- **Mantık:** {root_house}. evi 1 kabul edip {int(derived_n)} sayınca **{result_house}. eve** düşer.
- **Ton / çalışma biçimi:** {root_sign} (kök burç) üzerinden {int(derived_n)} sayınca **{ov_sign}** bindirmesi gelir.
- **Ana anahtar:** {ov_sign}’ün yöneticisi **{ruler}** (haritadaki yerleşimi + açıları).
        """.strip()
    )

with right:
    st.subheader("❓ Soru şablonları")
    qs = default_questions(root_house, int(derived_n), result_house, ov_sign, ruler)
    for i, q in enumerate(qs, 1):
        st.write(f"**{i}.** {q}")

    st.divider()
    st.subheader("🔎 Debug / Kontrol")
    st.code(
        f"derived_house(root={root_house}, n={int(derived_n)}) = {result_house}\n"
        f"overlay_sign(root_sign='{root_sign}', n={int(derived_n)}) = '{ov_sign}'\n"
        f"ruler({ruler_system})('{ov_sign}') = '{ruler}'",
        language="text"
    )

st.divider()
st.info("Sonraki adım: Haritandan gezegen yerleşimlerini (ev/burç/açı) bu yapıya bağlayıp, yönetici gezegenin durumuna göre otomatik skorlama + paragraf yorum üretebiliriz.")

import re

SIGN_ALIASES = {
  "Koç":"Koç","Boga":"Boğa","Boğa":"Boğa","Ikizler":"İkizler","İkizler":"İkizler","Yengec":"Yengeç","Yengeç":"Yengeç",
  "Aslan":"Aslan","Basak":"Başak","Başak":"Başak","Terazi":"Terazi","Akrep":"Akrep","Yay":"Yay","Oglak":"Oğlak","Oğlak":"Oğlak",
  "Kova":"Kova","Balik":"Balık","Balık":"Balık",
  # İngilizce
  "Aries":"Koç","Taurus":"Boğa","Gemini":"İkizler","Cancer":"Yengeç","Leo":"Aslan","Virgo":"Başak","Libra":"Terazi","Scorpio":"Akrep",
  "Sagittarius":"Yay","Capricorn":"Oğlak","Aquarius":"Kova","Pisces":"Balık",
  # Semboller (isteğe göre genişletilir)
  "♈":"Koç","♉":"Boğa","♊":"İkizler","♋":"Yengeç","♌":"Aslan","♍":"Başak","♎":"Terazi","♏":"Akrep","♐":"Yay","♑":"Oğlak","♒":"Kova","♓":"Balık",
}

def normalize_sign(s: str) -> str:
    s = s.strip()
    return SIGN_ALIASES.get(s, s)

def parse_planet_lines(text: str):
    """
    Beklenen: Planet SIGN deg°min' house
    Örn: Sun ♐ 4°26' 7
    """
    planets = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        # gezegen adı = ilk kelime
        parts = line.split()
        planet = parts[0]

        # burç yakala (sembol veya kelime)
        # line içinde SIGN_ALIASES anahtarlarından birini arıyoruz
        sign = None
        for key in SIGN_ALIASES.keys():
            if f" {key} " in f" {line} ":
                sign = normalize_sign(key)
                break
        if sign is None:
            # ikinci token burç olabilir
            if len(parts) > 1:
                sign = normalize_sign(parts[1])
            else:
                continue

        # derece/dakika/ev yakala
        m = re.search(r"(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})\s*$", line)
        if not m:
            # örn: 4°26' 7 gibi de gelebilir (dakika sonra ev)
            m = re.search(r"(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})", line)
        if not m:
            continue

        deg = int(m.group(1))
        minute = int(m.group(2))
        house = int(m.group(3))

        planets[planet] = {"sign": sign, "deg": deg + minute/60.0, "house": house}
    return planets


