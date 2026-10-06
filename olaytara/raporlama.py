"""Çıktı üretimi — Türkçe metin ve makine okunur JSON.

Her iki biçim de aynı Sonuc nesnesinden türer; dolayısıyla metin çıktısında
görünen her bulgu JSON'da da bulunur. Kanıt alanları maskelenmiştir.
"""

from __future__ import annotations

import json

from .modeller import Onem, Sonuc

RENKLER = {
    Onem.KRITIK: "\033[1;31m",
    Onem.YUKSEK: "\033[0;31m",
    Onem.ORTA: "\033[0;33m",
    Onem.DUSUK: "\033[0;36m",
}
SIFIRLA = "\033[0m"

_ONEM_ADI = {
    Onem.KRITIK: "Kritik",
    Onem.YUKSEK: "Yüksek",
    Onem.ORTA: "Orta",
    Onem.DUSUK: "Düşük",
}


def metin_uret(
    bulgulu: list[Sonuc],
    sorunlar: list[str],
    renkli: bool = True,
    taranan: list[Sonuc] | None = None,
    esik_ad: str = "",
) -> str:
    """İnsan okunur rapor.

    `taranan` verilmezse `bulgulu` kullanılır. Ayrı verildiğinde özet satırı
    **taranan** dosyaları gösterir — eşik altı bulgular filtrelendiğinde
    "0 dosya, 0 girdi" yazıp hiçbir şey taranmamış izlenimi vermemelidir.
    """
    kaynak = taranan if taranan is not None else bulgulu
    toplam_bulgu = sum(len(s.bulgular) for s in kaynak)
    toplam_girdi = sum(len(s.girintiler) for s in kaynak)
    baslik = f"OlayTara: {len(kaynak)} dosya, {toplam_girdi} girdi"

    satirlar: list[str] = []
    if toplam_bulgu == 0:
        satirlar.append(f"{baslik}, 0 bulgu.")
    else:
        satirlar.append(f"{baslik}, {toplam_bulgu} bulgu ({len(bulgulu)} dosya eşiği geçti).")

    if esik_ad:
        satirlar.append(f"Eşik: {esik_ad} (altındaki bulgular gizlendi).")
    satirlar.append("")

    for sonuc in bulgulu:
        for b in sonuc.bulgular:
            onem_ad = _ONEM_ADI[b.onem]
            if renkli:
                onem_ad = f"{RENKLER[b.onem]}{onem_ad}{SIFIRLA}"
            konum = b.girinti.konum if b.girinti.satir else sonuc.dosya
            satir = f"[{onem_ad}] {konum} {b.kural.kimlik}: {b.kural.ad}"
            satirlar.append(satir)
            if b.kanit:
                satirlar.append(f"  Kanıt: {b.kanit}")
            satirlar.append(f"  Güven: {b.guven}")
            for i, o in enumerate(b.kural.oneriler.split("\n")):
                onek = "  Öneri: " if i == 0 else "         "
                satirlar.append(onek + o.strip())
            satirlar.append("")

    if sorunlar:
        satirlar.append("Atlanan veya okunamayan girdiler:")
        for s_ in sorunlar:
            satirlar.append(f"  Uyarı: {s_}")
        satirlar.append("")

    return "\n".join(satirlar).rstrip() + "\n"


def json_uret(
    bulgulu: list[Sonuc],
    sorunlar: list[str],
    taranan: list[Sonuc] | None = None,
) -> str:
    """Makine okunur rapor — kanıtlar maskelenmiş hâlde."""
    kaynak = taranan if taranan is not None else bulgulu
    veri = {
        "arac": "olaytara",
        "sonuc": {
            "dosya_sayisi": len(kaynak),
            "girdi_sayisi": sum(len(s.girintiler) for s in kaynak),
            "bulgu_sayisi": sum(len(s.bulgular) for s in kaynak),
            "raporlanan_dosya": len(bulgulu),
            "en_yuksek_onem": (
                _ONEM_ADI[max(
                    (b.onem for s in kaynak for b in s.bulgular),
                    key=lambda o: o.value,
                    default=Onem.DUSUK,
                )]
                if any(s.bulgular for s in kaynak) else None
            ),
        },
        "dosyalar": [
            {
                "dosya": s.dosya,
                "girdi_sayisi": len(s.girintiler),
                "bolumler": s.bolum_sayaci,
                "bulgular": [
                    {
                        "kimlik": b.kural.kimlik,
                        "onem": _ONEM_ADI[b.onem],
                        "satir": b.girinti.satir or None,
                        "konum": b.girinti.konum if b.girinti.satir else s.dosya,
                        "kural": b.kural.ad,
                        "aciklama": b.kural.aciklama,
                        "kanit": b.kanit,
                        "guven": b.guven,
                        "oneriler": b.kural.oneriler,
}
                for b in s.bulgular
                ],
            }
            for s in bulgulu
        ],
        "sorunlar": sorunlar,
    }
    return json.dumps(veri, ensure_ascii=False, indent=2)
