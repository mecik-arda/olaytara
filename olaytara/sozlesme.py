#!/usr/bin/env python3
"""olaytara — Gerçek dünya AI güvenliği olayı iddia denetçisi.

Girdi sözleşmesinin TEK kaynağı buradadır; hem denetleyici hem raporlayıcı
bu modülü okur. Böylece "CI'dan geçti ama raporda görünmedi" durumu oluşamaz.

Kullanım:  python3 -m olaytara.cli tara <dosya> [--bicim json] [--esik <seviye>]
Çıkış:     0 = temiz, 1 = eşik ve üzeri bulgu, 2 = girdi/kullanım hatası
"""

import re

GIRDI_ADAYI_RE = re.compile(r"^\s*[-*] \[[^\]]+\]\([^)]+\)")

GIRDI_RE = re.compile(
    r"^- \[(?P<ad>.+?)\]\((?P<url>[^)]+)\) — (?P<aciklama>.+?) "
    r"\*\(tür: (?P<tur>[^,]+), dil: (?P<dil>TR|EN)\)\*\s*$"
)

HAM_URL_RE = re.compile(r"^\s*[-*]?\s*(\*\*[^*]+\*\*:?)?\s*https?://")

BOLUM_RE = re.compile(r"^##\s+(?P<baslik>.+?)\s*$")

KIMLIK_RE = {
    "CVE": re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE),
    "GHSA": re.compile(r"GHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}", re.IGNORECASE),
    "CWE": re.compile(r"CWE-\d+", re.IGNORECASE),
}

ISTISMAR_RE = re.compile(
    r"(istismar edil|sömürüldü|sömürül|exploit edil|exploited in the wild|"
    r"gerçek dünyada istismar|üretimde istismar|canlıya çıktı|"
    r"zero-day|sıfır gün|sıfır-tık|sıfır tük|gerçekleşti)",
    re.IGNORECASE,
)

ISTISMAR_YOK_RE = re.compile(
    r"(keşfedildi|keşfedil|raporlandı|zafiyet rapor|proof of concept|"
    r"gönderildi|ödül|bug bounty|doğrulanmadı|sömürülmedi|"
    r"istismar edilmedi|exploit edilmedi|not exploited)",
    re.IGNORECASE,
)

OLASILIK_RE = re.compile(
    r"(yol açabilir|açabilir|olabilir|muhtemel|potansiyel|olası|ihtimal|"
    r"[a-zçğıöşü]ıl?abilir|"
    r"could |would |can lead|might |potential)",
    re.IGNORECASE,
)

SURUM_ARALIGI_RE = re.compile(r"[<>]=?\s*\d+\.\d+")

YAMA_RE = re.compile(
    r"(yamaland|yamalad|patched|fixed|düzelt|versiyon|sürüm)", re.IGNORECASE
)

KURUMSAL_RE = re.compile(
    r"(nvd\.nist\.gov|osv\.dev|msrc\.microsoft\.com|cve\.org|"
    r"cve\.mitre\.org|github\.com/[^/]+/[^/]+/security/advisories)",
    re.IGNORECASE,
)

ACIKLAMA_UYARI_SINIRI = 900

BOLUM_ALT_SINIR = 10
BOLUM_UST_SINIR = 30
