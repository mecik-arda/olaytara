#!/usr/bin/env python3
"""olaytara — Gerçek dünya AI güvenliği olayı iddia denetçisi.

Girdi sözleşmesinin TEK kaynağı buradadır; hem denetleyici hem raporlayıcı
bu modülü okur. Böylece "CI'dan geçti ama raporda görünmedi" durumu oluşamaz.

Kullanım:  python3 -m olaytara.cli tara <dosya> [--bicim json] [--esik <seviye>]
Çıkış:     0 = temiz, 1 = eşik ve üzeri bulgu, 2 = girdi/kullanım hatası
"""

import re

# Bir girdi olmaya çalışan satır: madde işareti + markdown bağlantısı.
GIRDI_ADAYI_RE = re.compile(r"^\s*[-*] \[[^\]]+\]\([^)]+\)")

# Girdi sözleşmesi (awesome-ai-security-tr ile aynı ayırıcı):
#   - [Ad](url) — açıklama. *(tür: X, dil: TR|EN)*
GIRDI_RE = re.compile(
    r"^- \[(?P<ad>.+?)\]\((?P<url>[^)]+)\) — (?P<aciklama>.+?) "
    r"\*\(tür: (?P<tur>[^,]+), dil: (?P<dil>TR|EN)\)\*\s*$"
)

# Markdown bağlantısı olmadan yazılmış çıplak URL.
HAM_URL_RE = re.compile(r"^\s*[-*]?\s*(\*\*[^*]+\*\*:?)?\s*https?://")

# Bölüm başlıkları — kaynak listesi çok bölümlü olabilir.
BOLUM_RE = re.compile(r"^##\s+(?P<baslik>.+?)\s*$")

# Kimlik kalıpları: CVE, GHSA, CWE, tamamı opsiyonel ama birden fazlası
# aynı girdide geçerse tutarsız kaynak işaretidir.
KIMLIK_RE = {
    "CVE": re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE),
    "GHSA": re.compile(r"GHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}", re.IGNORECASE),
    "CWE": re.compile(r"CWE-\d+", re.IGNORECASE),
}

# "Zafiyet bulundu" ile "gerçekten istismar edildi" ayrımı.
#
# Kural tasarımı notu: istismar durumu HİÇ yazılmamışsa bu bir çelişki
# DEĞİLDİR ve bulgu üretilmez — aksi hâlde mevcut kaynak listelerindeki her
# girdi tetiklenir ve kural sıfır bilgi taşır. ONA03 yalnızca şu durumda
# çalışır: metin OLASILIK diliyle ("yol açabilir", "olabilir", "could")
# gerçeklik iddiası kurar, yani teorik bulguyu yaşanmış gibi sunar.
ISTISMAR_RE = re.compile(
    r"(istismar edil|sömürüldü|sömürül|exploit edil|exploited in the wild|"
    r"gerçek dünyada istismar|üretimde istismar|canlıya çıktı|"
    r"zero-day|sıfır gün|sıfır-tık|sıfır tük|gerçekleşti)",
    re.IGNORECASE,
)

# Zafiyet bulunduğunu ama istismar edilmediğini söyleyen ifadeler.
ISTISMAR_YOK_RE = re.compile(
    r"(keşfedildi|keşfedil|raporlandı|zafiyet rapor|proof of concept|"
    r"gönderildi|ödül|bug bounty|doğrulanmadı|sömürülmedi|"
    r"istismar edilmedi|exploit edilmedi|not exploited)",
    re.IGNORECASE,
)

# Olasılık dili — teorik bulguyu gerçeklik gibi sunan kalıplar.
# Türkçe "-ebilir / -ılabilir" yüklemleri ayrı bir desende toplanır;
# anahtar kelime listesi tek tek yazılsa bile "çalıştırılabilir",
# "sömürülebilir" gibi yüzlerce biçim kaçardı.
OLASILIK_RE = re.compile(
    r"(yol açabilir|açabilir|olabilir|muhtemel|potansiyel|olası|ihtimal|"
    r"[a-zçğıöşü]ıl?abilir|"
    r"could |would |can lead|might |potential)",
    re.IGNORECASE,
)

# Kurumsal kaynak göstergesi — ikinci doğrulama kaynağı beklenen yerler.
KURUMSAL_RE = re.compile(
    r"(nvd\.nist\.gov|osv\.dev|msrc\.microsoft\.com|cve\.org|"
    r"cve\.mitre\.org|github\.com/[^/]+/[^/]+/security/advisories)",
    re.IGNORECASE,
)

ACIKLAMA_UYARI_SINIRI = 900

BOLUM_ALT_SINIR = 10
BOLUM_UST_SINIR = 30
