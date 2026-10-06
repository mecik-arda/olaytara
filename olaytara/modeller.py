"""Veri sınıfları — bulgu, kanıt, önem derecesi ve sonuç kovaları.

olaytara girdi sözleşmesi tek kaynaktan beslenir (sozlesme.py); bu modül
yalnızca taşıma ve sunum katmanıdır.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Onem(Enum):
    """Bulgu önem derecesi. Eşik karşılaştırması bu sırayı kullanır."""

    DUSUK = 1
    ORTA = 2
    YUKSEK = 3
    KRITIK = 4

    @classmethod
    def ayristir(cls, metin: str) -> Onem | None:
        """'yuksek' gibi bir metni Onem'e çevirir; bilinmiyorsa None."""
        if not metin:
            return None
        try:
            return cls[metin.strip().upper().replace("İ", "I").replace("ı", "I")]
        except KeyError:
            return None


@dataclass(frozen=True)
class Girinti:
    """Bir girdi satırının sözleşmeye uygun ayrıştırılmış hâli."""

    dosya: str
    satir: int
    ad: str
    url: str
    aciklama: str
    tur: str
    dil: str
    bolum: str = ""

    @property
    def konum(self) -> str:
        return f"{self.dosya}:{self.satir}"


@dataclass(frozen=True)
class Kural:
    """Tek bir denetim kuralı — kimlik ve açıklaması KURALLAR.md'de tanımlıdır."""

    kimlik: str
    ad: str
    onem: Onem
    aciklama: str
    oneriler: str


@dataclass(frozen=True)
class Bulgu:
    """Bir kuralın ihlali. Kanıt alanı her zaman maskelenmiş olmalıdır."""

    kural: Kural
    girinti: Girinti
    kanit: str
    guven: str = "orta"

    @property
    def onem(self) -> Onem:
        return self.kural.onem

    def metin_satiri(self) -> str:
        """Tek satırlık insan okunur özet."""
        return (
            f"[{self.onem.name.capitalize()}] {self.girinti.konum} "
            f"{self.kural.kimlik}: {self.kural.ad}"
        )


@dataclass
class Sonuc:
    """Bir dosyanın tarama sonucu — metin ve JSON çıktı buradan türetilir."""

    dosya: str
    girintiler: list[Girinti] = field(default_factory=list)
    bulgular: list[Bulgu] = field(default_factory=list)
    bolum_sayaci: dict[str, int] = field(default_factory=dict)

    @property
    def en_yuksek_onem(self) -> Onem | None:
        if not self.bulgular:
            return None
        return max(b.onem for b in self.bulgular)

    def esig_gecer(self, esik: Onem) -> bool:
        """En yüksek önem eşiği aşıyor mu — çıkış kodunu belirler."""
        en_yuksek = self.en_yuksek_onem
        return en_yuksek is not None and en_yuksek.value >= esik.value
