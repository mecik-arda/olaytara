#!/usr/bin/env python3
"""Denetleyici testleri — her ONA kuralı için en az bir test."""

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from olaytara import tarayici  # noqa: E402
from olaytara.kurallar import KURALLAR, KURALLAR_IDX  # noqa: E402
from olaytara.modeller import Onem  # noqa: E402

GECERLI = (
    "- [Örnek Ürün — test (CVE-2026-12345)](https://nvd.nist.gov/vuln/detail/CVE-2026-12345) — "
    "Üründe prompt injection ile veri sızdırma zafiyeti bulundu; etkilenen sürüm "
    "1.2.3 ve 1.3.0 arasındaydı, üretimde istismar edildi. *(tür: araştırma, dil: EN)*"
)

_GIRDI_BASLANGIC = "- [Örnek Ürün — test (CVE-2026-12345)](https://nvd.nist.gov/vuln/detail/CVE-2026-12345)"
_ACIKLAMA_BASLANGIC = " — Üründe prompt injection"


def _ayirici_degistir(tire: bool) -> str:
    """Girdinin sözleşme ayırıcısını değiştirir; başlıktaki süsü korur."""
    yeni = " - " if tire else " — "
    bas = GECERLI.index(_ACIKLAMA_BASLANGIC)
    return GECERLI[:bas] + yeni + GECERLI[bas + len(_ACIKLAMA_BASLANGIC):]


def _tara_gecici(metin: str, dosya_adi: str = "olaylar.md"):
    """Geçici dosya yazıp tarar, Sonuc listesini döndürür."""
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / dosya_adi
        p.write_text(metin, encoding="utf-8")
        return [tarayici.dosya_tara(p, pathlib.Path(d))]


def _kimlikler(metin: str) -> set[str]:
    out: set[str] = set()
    for s in _tara_gecici(metin):
        out.update(b.kural.kimlik for b in s.bulgular)
    return out


class TestSozlesme(unittest.TestCase):
    def test_ona01_gecerli_girdi_bulgu_uretmez(self):
        sonuc = _tara_gecici(GECERLI)[0]
        self.assertEqual(len(sonuc.girintiler), 1)
        self.assertNotIn("ONA01", {b.kural.kimlik for b in sonuc.bulgular})

    def test_ona01_normal_tire_ayirici_reddedilir(self):
        self.assertIn("ONA01", _kimlikler(_ayirici_degistir(tire=True)))

    def test_ona01_em_dash_ayirici_kabul_edilir(self):
        self.assertNotIn("ONA01", _kimlikler(_ayirici_degistir(tire=False)))

    def test_ona01_tur_etiketi_yoksa_reddedilir(self):
        self.assertIn("ONA01", _kimlikler(GECERLI.replace(" *(tür: araştırma, dil: EN)*", "")))

    def test_ona01_sebep_somut_verir(self):
        sonuc = _tara_gecici(_ayirici_degistir(tire=True))[0]
        self.assertIn("EM DASH", sonuc.bulgular[0].kanit)

    def test_ona02_ciplak_baglanti_reddedilir(self):
        self.assertIn("ONA02", _kimlikler("https://ornek.example.com/yazi"))

    def test_ona02_madde_isaretli_cipnak_link(self):
        self.assertIn("ONA02", _kimlikler("- https://ornek.example.com/yazi\n"))

    def test_ona02_girintiyle_cipnak_link(self):
        self.assertIn("ONA02", _kimlikler("  https://ornek.example.com/yazi\n"))

    def test_ona02_satir_ortasinda_cipnak_link_yok(self):
        self.assertNotIn("ONA02", _kimlikler(GECERLI))

    def test_girinti_ayristirma_alanlari(self):
        g = _tara_gecici(GECERLI)[0].girintiler[0]
        self.assertEqual(g.tur, "araştırma")
        self.assertEqual(g.dil, "EN")
        self.assertIn("CVE-2026-12345", g.ad)
        self.assertEqual(g.konum, "olaylar.md:1")


class TestKurallar(unittest.TestCase):
    def test_ona03_olasilik_dili_gerceklik_iddiasi_kuruyor(self):
        satir = (
            "- [Ürün (CVE-2026-12345)](https://nvd.nist.gov/vuln/detail/CVE-2026-12345) — "
            "Prompt injection yoluyla sistem komutu çalıştırılabilir ve veri sızdırılabilir. "
            "Sürüm 1.2.3. *(tür: araştırma, dil: EN)*"
        )
        self.assertIn("ONA03", _kimlikler(satir))

    def test_ona03_istismar_edildi_gecerli(self):
        self.assertNotIn("ONA03", _kimlikler(GECERLI))

    def test_ona03_bulundu_ama_istismar_edilmedi_gecerli(self):
        satir = (
            "- [Ürün — CVE-2026-12345](https://nvd.nist.gov/vuln/detail/CVE-2026-12345) — "
            "Zafiyet keşfedildi ve raporlandı, istismar edilmedi. Sürüm 1.2.3. "
            "*(tür: araştırma, dil: EN)*"
        )
        self.assertNotIn("ONA03", _kimlikler(satir))

    def test_ona03_belirtilmemis_durum_gurultu_uretmez(self):
        """Durum hiç yazılmamışsa ONA03 tetiklenmez — kural sıfır bilgi
        taşımamalıdır. Mevcut kaynak listelerindeki mekanizma anlatımları
        (yüzlerce giriş) bu durumdadır."""
        satir = (
            "- [Ürün (CVE-2026-12345)](https://nvd.nist.gov/vuln/detail/CVE-2026-12345) — "
            "Prompt injection ile sistem komutu çalıştırılıyor, veri sızdırılıyor. "
            "Etkilenen sürüm 1.2.3. *(tür: araştırma, dil: EN)*"
        )
        self.assertNotIn("ONA03", _kimlikler(satir))

    def test_ona04_kimliksiz_urun_reddedilir(self):
        satir = (
            "- [Bazı Ürün — zafiyet (CVE-2026-99999)](https://ornek.example.com/a) — "
            "Üründe veri sızdırma zafiyeti bulundu, 1.0 sürümü etkilendi. "
            "*(tür: araştırma, dil: EN)*"
        )
        self.assertNotIn("ONA04", _kimlikler(satir))

    def test_ona04_surum_beyani_ama_kimlik_yok_reddedilir(self):
        satir = (
            "- [Bazı Ürün — zafiyet](https://ornek.example.com/a) — Üründe veri "
            "sızdırma zafiyeti bulundu, 1.0 sürümü etkilendi. *(tür: araştırma, dil: EN)*"
        )
        self.assertIn("ONA04", _kimlikler(satir))

    def test_ona04_kimligi_olan_urun_gecerli(self):
        satir = (
            "- [Bazı Ürün — zafiyet (CVE-2026-99999)](https://ornek.example.com/a) — "
            "Üründe veri sızdırma zafiyeti bulundu, 1.0 sürümü etkilendi. "
            "*(tür: araştırma, dil: EN)*"
        )
        self.assertNotIn("ONA04", _kimlikler(satir))

    def test_ona04_cvesi_olmayacak_olay_gurultu_uretmez(self):
        """Hukuki vaka, marka olayı veya derleme sayfası CVE taşımaz ve
        taşıması da beklenmez. Sürüm beyanı yoksa ONA04 üretilmez."""
        for ad, govde in [
            ("Air Canada — chatbot'un hatalı tavsiyesinden sorumlu tutuldu",
             "Mahkeme kararı verdi; kullanıcı zarar gördü. *(tür: vaka, dil: EN)*"),
            ("DPD chatbot'unun küfretmesi ve kendi şirketini eleştirmesi",
             "Kimlik ihlali yaşandı, şirket özür diledi. *(tür: vaka, dil: EN)*"),
            ("The Month of AI Bugs 2025 (Wrap Up)",
             "29 bulgu tek sayfada derlendi. *(tür: araştırma, dil: EN)*"),
        ]:
            satir = f"- [{ad}](https://ornek.example.com/a) — {govde}"
            self.assertNotIn("ONA04", _kimlikler(satir), ad)

    def test_ona05_surum_yoksa_reddedilir(self):
        satir = (
            "- [Ürün (CVE-2026-12345)](https://nvd.nist.gov/vuln/detail/CVE-2026-12345) — "
            "Üründe veri sızdırma zafiyeti bulundu ve üretimde istismar edildi. "
            "*(tür: araştırma, dil: EN)*"
        )
        self.assertIn("ONA05", _kimlikler(satir))

    def test_ona05_surum_araligi_gecerli(self):
        self.assertNotIn("ONA05", _kimlikler(GECERLI))

    def test_ona06_kurumsal_kaynak_yoksa_uyari(self):
        satir = (
            "- [Ürün (CVE-2026-12345)](https://ornek.example.com/a) — Üründe veri "
            "sızdırma zafiyeti bulundu ve üretimde istismar edildi; 1.2.3 sürümü. "
            "*(tür: araştırma, dil: EN)*"
        )
        self.assertIn("ONA06", _kimlikler(satir))

    def test_ona06_kurumsal_kaynak_varsa_gecerli(self):
        self.assertNotIn("ONA06", _kimlikler(GECERLI))

    def test_ona07_cok_kisa_aciklama_uyari(self):
        satir = (
            "- [Ürün (CVE-2026-12345)](https://nvd.nist.gov/vuln/detail/CVE-2026-12345) — "
            "veri sızdı. 1.0. *(tür: araştırma, dil: EN)*"
        )
        self.assertIn("ONA07", _kimlikler(satir))

    def test_ona08_bolum_sayisi_dusuk_reddedilir(self):
        metin = "# Başlık\n\n## Az bölüm\n\n" + GECERLI
        sonuc = _tara_gecici(metin)[0]
        onalari = {b.kural.kimlik for b in sonuc.bulgular}
        self.assertIn("ONA08", onalari)

    def test_ona08_bolum_sayisi_yuksek_reddedilir(self):
        girintiler = "\n".join(GECERLI.replace("CVE-2026-12345", f"CVE-2026-1000{i}")
                               for i in range(35))
        metin = "# Başlık\n\n## Çok büyük\n\n" + girintiler
        sonuc = _tara_gecici(metin)[0]
        self.assertIn("ONA08", {b.kural.kimlik for b in sonuc.bulgular})


class TestKurallarTamligi(unittest.TestCase):
    def test_kural_sayisi_sekiz(self):
        self.assertEqual(len(KURALLAR), 8)

    def test_kimlikler_ona01_ona08_arasi(self):
        for i in range(1, 9):
            self.assertIn(f"ONA{i:02d}", KURALLAR_IDX)

    def test_her_kuralin_onerisi_var(self):
        for k in KURALLAR:
            self.assertTrue(k.oneriler.strip(), f"{k.kimlik} öneri eksik")

    def test_her_kuralin_aciklamasi_var(self):
        for k in KURALLAR:
            self.assertTrue(k.aciklama.strip(), f"{k.kimlik} açıklama eksik")

    def test_her_kuralin_onemi_tanimli(self):
        for k in KURALLAR:
            self.assertIsInstance(k.onem, Onem)


class TestOrnekler(unittest.TestCase):
    """ornekler/ klasöründeki veriler kural tablosunu gerçekten tutturuyor mu."""

    def test_riskli_ornek_en_az_bir_kural_tetikler(self):
        d = pathlib.Path(__file__).resolve().parent.parent / "ornekler"
        sonuclar, _ = tarayici.dizi_tara(d / "riskli.md")
        kimlikler = {b.kural.kimlik for s in sonuclar for b in s.bulgular}
        self.assertTrue(
            {"ONA01", "ONA02", "ONA03", "ONA04"} & kimlikler,
            f"riskli.md beklenen kuralları tetiklemiyor: {kimlikler}",
        )

    def test_temiz_ornek_yuksek_onem_uretmez(self):
        d = pathlib.Path(__file__).resolve().parent.parent / "ornekler"
        sonuclar, _ = tarayici.dizi_tara(d / "temiz.md")
        yuksek = [b for s in sonuclar for b in s.bulgular
                  if b.onem.value >= Onem.YUKSEK.value]
        self.assertEqual(yuksek, [], f"temiz.md yüksek önem üretti: "
                                    f"{[(b.kural.kimlik, b.girinti.konum) for b in yuksek]}")


class TestCikisKodu(unittest.TestCase):
    def test_esik_filtresi(self):
        sonuc = _tara_gecici(GECERLI)[0]
        self.assertFalse(sonuc.esig_gecer(Onem.KRITIK))
        self.assertFalse(sonuc.esig_gecer(Onem.YUKSEK))
        self.assertTrue(sonuc.esig_gecer(Onem.DUSUK))

    def test_bos_girdi_esik_gecmez(self):
        sonuc = _tara_gecici("# Başlık\n")[0]
        self.assertFalse(sonuc.esig_gecer(Onem.DUSUK))


if __name__ == "__main__":
    unittest.main()
