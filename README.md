# olaytara

Gerçek dünya AI güvenliği olayı iddia denetçisi. Markdown kaynak listelerini
okur, her girdinin **kanıt düzeyini** denetler.

> Literatürde bir saldırının teoride mümkün olması ile üretimde gerçekten
> yaşanması ayrı şeylerdir. Bir kaynak listesi ikisini ayırmıyorsa, kanıtsız
> iddiayı doğrulanmış gibi sunar.

**Sıfır bağımlılık, çevrimdışı, salt okunur.** Hiçbir kaynağa bağlanmaz,
hiçbir kodu çalıştırmaz, hiçbir dosyayı değiştirmez. Yalnızca metnin kendi
iç tutarlılığını kontrol eder.

`kanaryatara` RAG bilgi tabanındaki belgeleri denetler. olaytara ise o
belgeleri veya kaynak listelerini **kayıt olarak** denetler: her olayın
kimliği, sürümü, kanıtı ve istismar durumu tutarlı mı?

---

## Özellikler

- **Sözleşme denetimi (ONA01–ONA02)** — çıplak bağlantı, hatalı ayırıcı, eksik
  tür/dil etiketi
- **Kanıt ayrımı (ONA03)** — "zafiyet bulundu" ile "üretimde istismar edildi"
  birbirine karışmış mı
- **İzlenebilirlik (ONA04–ONA05)** — sürüm/yama beyanı olup takip kimliği
  (CVE/GHSA/CWE) taşımayan kayıtlar, belirtilmemiş sürüm aralıkları
- **Çapraz doğrulama (ONA06)** — kayıt tek kaynaklı mı
- **Dizin hijyeni (ONA07–ONA08)** — açıklama uzunluğu, bölüm başına kaynak sayısı
- **Maskelenmiş kanıt** — URL yolları ve serbest metinli kanıt parçaları rapora
  yazılmaz
- **CI uyumlu** — `--bicim json`, eşik tabanlı çıkış kodları (0 / 1 / 2)

---

## Kurulum

```bash
git clone https://github.com/mecik-arda/olaytara
cd olaytara
pip install .
```

Kurulum olmadan da çalışır:

```bash
python -m olaytara.cli tara kaynaklar/10-gercek-dunya-olaylari.md
```

---

## Kullanım

```bash
# Tek dosyayı denetle
olaytara tara kaynaklar/10-gercek-dunya-olaylari.md

# Dizini tara, makine okunur çıktı al
olaytara tara kaynaklar/ --bicim json

# Sadece yüksek önem eşiğini raporla (CI için)
olaytara tara kaynaklar/ --esik yuksek

# Kural kümesini göster
olaytara kurallar
olaytara kurallar --bicim json
```

Örnek çıktı:

```text
OlayTara: 1 dosya, 18 girdi, 24 bulgu.
Eşik: orta (altındaki bulgular gizlendi).

[Kritik] 10-gercek-dunya-olaylari.md:11 ONA03: Zafiyet ve istismar iddiası karıştırılmış
  Kanıt: ne istismar edildi ne de bulundu; durum belirsiz
  Güven: orta
  Öneri: Girdide bu iki durumu ayrı ayrı belirtin. Gerçekten istismar edilmediyse
         bunu açıkça yazın ('keşfedildi, istismar edilmedi'); istismar varsa veri
         sızdırma, etkilenen sürüm veya kayıt numarası verin.

[Yüksek] 10-gercek-dunya-olaylari.md:15 ONA04: Sürüm beyanı var ama takip kimliği yok
  Kanıt: sürüm/yama beyanı var, CVE/GHSA/CWE yok
  Güven: orta
  Öneri: Girdiye takip kimliği ekleyin: (CVE-2026-12345) veya (GHSA-xxxx-xxxx-xxxx).
         Kimlik yoksa bu kayıt bir zafiyet değil, olay kaydıdır; o durumda sürüm
         beyanını da kaldırın.
Risk eşiğine ulaşıldı.
```

**Çıkış kodları**

| Kod | Anlam |
|---|---|
| `0` | Temiz |
| `1` | Eşik veya üzerinde bulgu var, ya da girdi sorunu bildirildi |
| `2` | Girdi veya kullanım hatası |

---

## Girdi sözleşmesi

```text
- [Kaynak Adı](url) — Ne olduğu ve neden değerli olduğu. *(tür: makale|araç|lab|dataset, dil: TR|EN)*
```

Ayırıcı **EM DASH** (`—`) olmalıdır, normal tire değil. Bu sözleşme
[awesome-ai-security-tr](https://github.com/fevziegeyurtsevenler/awesome-ai-security-tr)
listesiyle aynıdır; olaytara o listenin kanıt düzlemindeki eksiğini kapatır.

---

## Denetlenenler

| Kural | Ne doğrular | Önem |
|---|---|---|
| **ONA01** | Girdi sözleşmesine uymayan satır (ayırıcı, etiket, girinti) | Yüksek |
| **ONA02** | Bağlantısız çıplak URL | Yüksek |
| **ONA03** | Zafiyet ve istismar iddiası karıştırılmış | Kritik |
| **ONA04** | Sürüm/yama beyanı var ama CVE/GHSA/CWE yok | Orta |
| **ONA05** | Sürüm aralığı belirtilmemiş | Orta |
| **ONA06** | Çapraz doğrulama kaynağı yok (NVD/OSV/advisory) | Düşük |
| **ONA07** | Açıklama çok kısa (<80) veya çok uzun (>900) | Düşük |
| **ONA08** | Bölüm başına kaynak sayısı 10–30 aralığında değil | Düşük |

---

## Rakipler ve fark

Bu alan dolu; işte dürüst konumlandırma.

- **[ValeGuard](https://github.com/valeguard/valeguard)** — LLM çıktı denetimi
  odaklı, model yanıtını izler. **Fark:** olaytara modele hiç bağlanmaz; olay
  *kayıtlarının* kanıt düzeyini denetler.
- **[OSV-Scanner](https://github.com/google/osv-scanner)** — paket bağımlılık
  zafiyetlerini sözlükle eşleştirir. **Fark:** olaytara CVE'nin varlığını
  sorgulamaz, metinde beyan edilen kimliği ve sürüm iddiasını tutarlılık
  açısından denetler; çevrimdışıdır.
- **[awesome-ai-security-tr](https://github.com/fevziegeyurtsevenler/awesome-ai-security-tr)**
  biçim denetleyicisi — girdi sözleşmesini ve ölü bağlantıları CI'da kontrol
  eder. **Fark:** o depo biçim ve bağlantı doğruluğunu denetler; olaytara
  **kanıt yeterliliğini** denetler. İkisi tamamlayıcıdır, rakip değil.
- **Elle gözden geçirme** — olay listesindeki 18 kaydın hepsi tek tek okunmuş
  olabilir, ama 10. bölüm güncellendiğinde kontrol geriye gider. **Fark:**
  mekanik, tekrarlanabilir, CI'a bağlanır.

---

## Güvenlik modeli

- Araç **yalnızca okur** — dosyayı değiştirmez, ağa bağlanmaz, kod
  çalıştırmaz, LLM çağırmaz.
- Araç **asla otomatik engelleme yapmaz**. Bir bulgu bir **risk göstergesidir**,
  kesin gerçek değildir; insan doğrulaması şarttır.
- Statik metin analizi **yaklaşıktır**. Bir olayın gerçekten istismar edilip
  edilmediği yalnızca kaynaktaki ifade biçiminden tahmin edilir; olaytara
  **kaynağa bakmaz**, yazıyı okur.
- Kanıt alanları maskelenir: URL'lerde yol gösterilmez, serbest metinli kanıt
  parçaları kısaltılır. Rapor, tek başına istismar için kullanılabilir bir
  hedef listesi hâline gelmez.
- Araç yalnızca **yetkilendirilmiş** çalışmalarda ve kendi kaynak
  listelerinizde kullanılmalıdır.

---

## Sınırlamalar

- **Kaynağa bağlanmaz.** Bir CVE'nin gerçekten var olduğunu, bir advisory'nin
  gerçekten yayımlandığını sorgulamaz. ONA04 ve ONA06 yalnızca metinde beyan
  edilen varlığı denetler.
- **İstismar durumu dilbilimsel tahmindir.** "gerçekleşti", "istismar edildi"
  gibi ifadeler aranır; yazarın niyetini başka kelimelerle ifade ettiği
  durumda yanlış negatif verebilir.
- **Tarih ve sürüm tutarlılığı denetlenmez.** "En yeni önce" sıralaması ve
  tarih tutarlılığı kapsam dışıdır.
- **Sadece markdown tarar.** HTML, JSON veya başka formatlar desteklenmez.
- **CVE eşleme yapmaz.** Kimlik sözdizimsel olarak doğrulanır
  (`CVE-\d{4}-\d{4,7}`); numaranın gerçekten kayıtlı olduğu sorgulanmaz.

---

## Geliştirme

```bash
python -m unittest discover -s tests -v
ruff check .
```

34 test: her ONA kuralı için en az bir test, kural tasarımının gürültü
ölçümüyle doğrulandığı regresyon testleri, örnek dosyaların kural tablosunu
gerçekten tutturduğu denetimler ve çıkış kodu sözleşmesi.

**Kural gürültüsü ölçümü.** Kurallar mevcut kaynak listelerindeki gerçek
girdilerde sınandı. ONA04 ilk haliyle "ürün adı geçiyor" diye tetikleniyordu ve
18 girdinin 13'ünde yanlış pozitif üretiyordu — Air Canada gibi hukuki vaka
kayıtlarının CVE taşımaması bir eksiklik değil. Kural, sürüm veya yama
beyanı **olduğunda** devreye giracak şekilde daraltıldı: 3/18, ve üçü de
gerçekten aksiyon alınabilir.

**Kaynak: 10. bölüm, 18 girdi**

```
ONA03 1   ONA04 3   ONA05 2   ONA08 2
```

---

## Lisans

[MIT](LICENSE) — Arda Meçik

Bu proje, Türkçe yapay zeka güvenliği kaynak listesi
[awesome-ai-security-tr](https://github.com/fevziegeyurtsevenler/awesome-ai-security-tr)
ekojisisteminе katkı kapsamında geliştirilmiştir.

## Sorumluluk reddi

Bu araç yalnızca yetkilendirilmiş güvenlik çalışmalarında ve kendi kaynak
listelerinizde kullanılmalıdır. Denetlenen kaynakların doğruluğundan
kullanıcı sorumludur.