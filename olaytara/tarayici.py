"""Denetleyici — girdi sözleşmesini okur, ONA01–ONA08 kurallarını uygular.

Araç yalnızca okur: hiçbir dosyayı değiştirmez, hiçbir kaynağa bağlanmaz,
hiçbir kodu çalıştırmaz. Girdinin kendi iç tutarlılığını denetler.
"""

from __future__ import annotations

import pathlib
import re

from . import sozlesme as s
from .kurallar import KURALLAR_IDX
from .modeller import Bulgu, Girinti, Onem, Sonuc

ATLANACAK = frozenset({
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".ruff_cache", "build", "dist",
})


def _dosya_adaylari(kok: pathlib.Path) -> list[pathlib.Path]:
    if kok.is_file():
        return [kok]
    return [
        p for p in sorted(kok.rglob("*.md"))
        if not ATLANACAK & set(p.relative_to(kok).parts)
    ]


def dosya_tara(dosya: pathlib.Path, kok: pathlib.Path) -> Sonuc:
    """Tek bir markdown dosyasını okur ve denetler."""
    sonuc = Sonuc(dosya=str(dosya.relative_to(kok)) if dosya != kok else dosya.name)
    satirlar = dosya.read_text(encoding="utf-8").split("\n")
    bolum = ""

    for i, satir in enumerate(satirlar, 1):
        b = s.BOLUM_RE.match(satir)
        if b:
            bolum = b.group("baslik").strip()
            continue

        m = s.GIRDI_RE.match(satir)
        if not m:
            if s.GIRDI_ADAYI_RE.match(satir):
                sonuc.bulgular.append(Bulgu(
                    kural=KURALLAR_IDX["ONA01"],
                    girinti=_gecici(i, str(dosya.name)),
                    kanit=_sozlesme_sebebi(satir),
                    guven="yuksek",
                ))
            elif s.HAM_URL_RE.match(satir):
                sonuc.bulgular.append(Bulgu(
                    kural=KURALLAR_IDX["ONA02"],
                    girinti=_gecici(i, str(dosya.name)),
                    kanit="bağlantısız URL",
                    guven="yuksek",
                ))
            continue

        d = m.groupdict()
        aciklama = d["aciklama"].strip()
        girinti = Girinti(
            dosya=str(dosya.relative_to(kok)) if dosya != kok else dosya.name,
            satir=i,
            ad=d["ad"].strip(),
            url=d["url"].strip(),
            aciklama=aciklama,
            tur=d["tur"].strip(),
            dil=d["dil"].strip(),
            bolum=bolum,
        )
        sonuc.girintiler.append(girinti)
        sonuc.bolum_sayaci[bolum or "(başlıksız)"] = (
            sonuc.bolum_sayaci.get(bolum or "(başlıksız)", 0) + 1
        )
        sonuc.bulgular.extend(_girdi_kurallari(girinti))

    sonuc.bulgular.extend(_bolum_kurallari(sonuc))
    return sonuc


def _gecici(satir: int, dosya: str) -> Girinti:
    """Sözleşmeye uymayan satırlar için konum tutan geçici kayıt."""
    return Girinti(dosya=dosya, satir=satir, ad="", url="", aciklama="", tur="", dil="")


def _sozlesme_sebebi(satir: str) -> str:
    """Reddedilen satıra somut sebep ver — destek gerektirmesin.

    Ayırıcı kontrolü bağlantının kapanış parantezinden sonrasına bakar; başlık
    içindeki "—" bir süs olabilir ve yanıltmamalıdır.
    """
    kapanis = satir.find(")", satir.find("](", satir.find("]")) + 1)
    if kapanis != -1:
        kalan = satir[kapanis + 1:].lstrip()
        if kalan.startswith("- "):
            return "ayırıcı normal tire; EM DASH (—) olmalı"
        if not kalan.startswith("— "):
            return "bağlantıdan sonra ' — ' ayırıcısı yok"
    elif " — " not in satir:
        return "açıklamadan önce ' — ' ayırıcısı yok"

    if "tür:" not in satir:
        return "sonda *(tür: …, dil: TR|EN)* etiketi yok"
    if not satir.startswith("- ["):
        return "satır '- [' ile başlamıyor"
    return "sözleşmeye uymuyor (ad/url/açıklama sırasını kontrol edin)"


def _girdi_kurallari(g: Girinti) -> list[Bulgu]:
    """Sözleşmeye uyan bir girdiye ONA03–ONA07 kurallarını uygular."""
    bulgular: list[Bulgu] = []

    kimlik_var = any(rx.search(g.ad) or rx.search(g.aciklama) for rx in s.KIMLIK_RE.values())
    surum_beyani = bool(
        s.SURUM_ARALIGI_RE.search(g.aciklama) or s.YAMA_RE.search(g.aciklama)
    )
    if surum_beyani and not kimlik_var:
        bulgular.append(Bulgu(
            kural=KURALLAR_IDX["ONA04"],
            girinti=g,
            kanit="sürüm/yama beyanı var, CVE/GHSA/CWE yok",
            guven="orta",
        ))

    if not (re_sürüm(g.ad) or re_sürüm(g.aciklama)) and (
        re_istismar_edildi(g.aciklama) or re_duzeltildi(g.aciklama)
    ):
        bulgular.append(Bulgu(
            kural=KURALLAR_IDX["ONA05"],
            girinti=g,
            kanit="sürüm aralığı belirtilmemiş",
            guven="orta",
        ))

    if not (s.ISTISMAR_RE.search(g.aciklama) or s.ISTISMAR_YOK_RE.search(g.aciklama)):
        if s.OLASILIK_RE.search(g.aciklama):
            bulgular.append(Bulgu(
                kural=KURALLAR_IDX["ONA03"],
                girinti=g,
                kanit="olasılık dili var, istismar durumu belirtilmemiş",
                guven="orta",
            ))
    elif s.ISTISMAR_RE.search(g.aciklama) and not (
        s.KURUMSAL_RE.search(g.url) or s.KURUMSAL_RE.search(g.aciklama)
    ):
        bulgular.append(Bulgu(
            kural=KURALLAR_IDX["ONA06"],
            girinti=g,
            kanit="kurumsal kaynak yok, tek kaynaklı",
            guven="dusuk",
        ))

    if len(g.aciklama) > s.ACIKLAMA_UYARI_SINIRI or len(g.aciklama) < 80:
        bulgular.append(Bulgu(
            kural=KURALLAR_IDX["ONA07"],
            girinti=g,
            kanit=f"açıklama {len(g.aciklama)} karakter",
            guven="dusuk",
        ))

    return bulgular


def _bolum_kurallari(sonuc: Sonuc) -> list[Bulgu]:
    """Bölüm başına kaynak sayısı sınırları (ONA08)."""
    bulgular: list[Bulgu] = []
    for bolum, adet in sonuc.bolum_sayaci.items():
        if adet < s.BOLUM_ALT_SINIR or adet > s.BOLUM_UST_SINIR:
            g = Girinti(
                dosya=sonuc.dosya, satir=0, ad=bolum, url="",
                aciklama="", tur="", dil="",
            )
            bulgular.append(Bulgu(
                kural=KURALLAR_IDX["ONA08"],
                girinti=g,
                kanit=f"{adet} kaynak (sınır {s.BOLUM_ALT_SINIR}-{s.BOLUM_UST_SINIR})",
                guven="dusuk",
            ))
    return bulgular


def dizi_tara(kok: pathlib.Path) -> tuple[list[Sonuc], list[str]]:
    """Dizini tarar. Atlanan veya okunamayan dosyalar ayrıca bildirilir."""
    sonuclar: list[Sonuc] = []
    sorunlar: list[str] = []
    for d in _dosya_adaylari(kok):
        if d.stat().st_size > 2_000_000:
            sorunlar.append(f"{d}: 2 MB üstü, atlandı")
            continue
        try:
            sonuclar.append(dosya_tara(d, kok))
        except (OSError, UnicodeDecodeError) as e:
            sorunlar.append(f"{d}: okunamadı ({e.__class__.__name__})")
    return sonuclar, sorunlar


def tum_tara(kok: pathlib.Path) -> tuple[list[Sonuc], list[str]]:
    if not kok.exists():
        raise FileNotFoundError(kok)
    return dizi_tara(kok)


def filtrele(sonuclar: list[Sonuc], esik: Onem) -> list[Sonuc]:
    """Eşiğin altındaki bulguları atar — çıkış kodunu belirleyen adım."""
    out = []
    for s_ in sonuclar:
        kalan = [b for b in s_.bulgular if b.onem.value >= esik.value]
        if kalan:
            kopya = Sonuc(dosya=s_.dosya, girintiler=s_.girintiler,
                          bulgular=kalan, bolum_sayaci=s_.bolum_sayaci)
            out.append(kopya)
    return out


_Urun_RE = re.compile(r"[A-Z][A-Za-z0-9.]{2,}")
_Surum_RE = re.compile(r"[<>=]?\s*\d+\.\d+")
_Yama_RE = re.compile(r"(yamaland|yamalad|patched|fixed|düzelt)", re.IGNORECASE)


def re_urun_adı(metin: str) -> bool:
    return bool(_Urun_RE.search(metin))


def re_sürüm(metin: str) -> bool:
    return bool(_Surum_RE.search(metin))


def re_istismar_edildi(metin: str) -> bool:
    return bool(s.ISTISMAR_RE.search(metin))


def re_duzeltildi(metin: str) -> bool:
    return bool(_Yama_RE.search(metin))
