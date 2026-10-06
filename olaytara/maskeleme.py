"""Maskeleme — kanıt alanı asla ham kaynak bağlantısını taşımaz.

Amaç: rapor okunabilir kalsın, ama raporun kendisi tek başına istismar için
kullanılabilir bir hedef listesi hâline gelmesin. URL'ler kaynak alanı ve
kimlikler zaten girdi metninde açıkça durduğu için burada ikinci bir kez
gizlenmeleri gerekmez; gizlenen şey serbest metinli kanıt parçalarıdır.
"""

from __future__ import annotations

import re

_URL_RE = re.compile(r"(https?://[^\s)\]]+)")
_ID_RE = re.compile(r"\b(CVE-\d{4}-\d{4,7}|GHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4})\b", re.IGNORECASE)


def metin_maskele(deger: str, bas_tut: int = 6, son_tut: int = 6) -> str:
    """Serbest metinli kanıtı ortadan kaldırır.

    Uzunluğa göre davranış değişir: kısa metinler tamamen gizlenir, uzun
    metinlerde baş ve son korunur ki hangi kalıba takıldığı anlaşılsın.
    """
    if deger is None:
        return ""
    d = deger.strip()
    if not d:
        return ""
    if len(d) <= bas_tut + son_tut:
        return "*" * len(d)
    return f"{d[:bas_tut]}***{d[-son_tut:]}"


def url_maskele(url: str) -> str:
    """URL'de yalnızca şema ve alan adı gösterilir, yol gösterilmez.

    Kaynak bağlantısı zaten girdi satırında açıkça durduğu için buradaki
    gizleme, kanıt alanının bağımsız okunduğu senaryoyu hedefler.
    """
    if not url:
        return ""
    m = re.match(r"(https?://)([^/]+)(/.*)?", url)
    if not m:
        return url
    yol = m.group(3) or ""
    uzunluk = len(yol.rstrip("/"))
    if uzunluk <= 1:
        return f"{m.group(2)}{yol}"
    return f"{m.group(2)}/…{yol[-12:]}"


def kanit_maskele(kanit: str) -> str:
    """Kanıt metnindeki URL ve kimlikleri maskeler, kalan serbest metni kısaltır."""
    if not kanit:
        return ""
    m = _URL_RE.sub(lambda x: url_maskele(x.group(0)), kanit)
    m = _ID_RE.sub(lambda x: x.group(0).upper(), m)
    return m
