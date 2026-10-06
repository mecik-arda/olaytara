"""Kural kümesi — ONA01–ONA08.

Her kural kalıcı bir kimlik taşır. Kimlik asla yeniden kullanılmaz ve üç
yerde eşitlenir: kaynak kod, README kural tablosu, test adı.

Bir bulgu "kesin gerçek" değil, iddianın doğrulanmamış olduğunun işaretidir.
olaytara hiçbir kaynağa bağlanmaz; yalnızca metnin kendi iç tutarlılığını ve
beyan ettiği kanıtın varlığını denetler.
"""

from __future__ import annotations

from .modeller import Kural, Onem

KURALLAR: tuple[Kural, ...] = (
    Kural(
        kimlik="ONA01",
        ad="Girdi sözleşmesine uymayan satır",
        onem=Onem.YUKSEK,
        aciklama=(
            "Girdi adayı olmak için madde işareti ve markdown bağlantısı içermeli, "
            "ardından EM DASH ayırıcısı ve sonda tür/dil etiketi gelmelidir."
        ),
        oneriler=(
            "Satırı şu biçimde yazın:  - [Ad](url) — açıklama. "
            "*(tür: makale|araç|lab|dataset, dil: TR|EN)*\n"
            "  Ayırıcı normal tire (-) değil EM DASH (—) olmalıdır."
        ),
    ),
    Kural(
        kimlik="ONA02",
        ad="Çıplak bağlantı",
        onem=Onem.YUKSEK,
        aciklama=(
            "Markdown bağlantısı olmadan yazılmış URL kabul edilmez. Sadece adres "
            "taşıyan bir girdi, dizinde tarama değeri katmaz."
        ),
        oneriler=(
            "Bağlantıyı - [Ad](url) biçimine çevirin ve adın ne olduğunu yazın."
        ),
    ),
    Kural(
        kimlik="ONA03",
        ad="Teorik bulgu gerçeklik gibi sunulmuş",
        onem=Onem.KRITIK,
        aciklama=(
            "Girdi, olayın gerçekten yaşandığını söylemeden olasılık diliyle "
            "('yol açabilir', 'olabilir', 'could') anlatıyor. Okuyucu bunu "
            "kanıtsız bir gerçeklik iddiası olarak alabilir."
        ),
        oneriler=(
            "Durumu açıkça belirtin: yaşandıysa 'üretimde istismar edildi' "
            "yazın, yaşanmadıysa 'keşfedildi, istismar edilmedi'. Olasılık "
            "dilini mekanizma açıklamasında kullanabilirsiniz ama ilk cümlede "
            "durumu belirtin."
        ),
    ),
    Kural(
        kimlik="ONA04",
        ad="Kimliksiz zafiyet kaydı",
        onem=Onem.ORTA,
        aciklama=(
            "Ürün adı geçen ancak CVE, GHSA veya CWE taşımayan girdi, takip edilemez. "
            "Bu kimlikler olmadan yamalama durumu ve etkilenen sürümler izlenemez."
        ),
        oneriler=(
            "Girdiye kimlik ekleyin: (CVE-2026-12345) veya (GHSA-xxxx-xxxx-xxxx). "
            "Kimlik bulunamıyorsa girdiyi kaynak listesine almak yerine not olarak tutun."
        ),
    ),
    Kural(
        kimlik="ONA05",
        ad="Etkilenen ürün veya sürüm belirtilmemiş",
        onem=Onem.ORTA,
        aciklama=(
            "Sürüm bilgisi olmayan bir olay kaydı, kullanıcının kendi sisteminde "
            " riski değerlendirmesini imkânsız kılar. 'Düzeltildi' ancak hangi "
            "sürümden itibaren geçerli olduğu bilinirse anlamlıdır."
        ),
        oneriler=(
            "Açıklamaya etkilenen sürüm aralığını yazın: (<1.39.4 → 1.39.4)."
        ),
    ),
    Kural(
        kimlik="ONA06",
        ad="Çapraz doğrulama kaynağı yok",
        onem=Onem.DUSUK,
        aciklama=(
            "Girdi yalnızca tek kaynağa dayanıyor. Ürünün kendi güvenlik danışması, "
            "NVD/OSV kaydı veya bağımsız bir post-mortem ikinci bir doğrulama "
            "kaynağıdır; bulunmadığında kayıt tek kaynaklı kalır."
        ),
        oneriler=(
            "NVD (nvd.nist.gov), OSV (osv.dev) veya ürünün kendi advisory "
            "sayfasına bağlantı ekleyin."
        ),
    ),
    Kural(
        kimlik="ONA07",
        ad="Açıklama eksik veya fazla uzun",
        onem=Onem.DUSUK,
        aciklama=(
            "Bu bir dizindir. Açıklama kısa olmalı ve girdinin neden listelendiğini "
            "anlatmalıdır; paragraf girdiyi taranamaz hale getirir."
        ),
        oneriler=(
            "Açıklamayı 1-2 cümleye indirin ve olayın güvenlik açısından neden "
            "önemli olduğunu belirtin."
        ),
    ),
    Kural(
        kimlik="ONA08",
        ad="Bölüm şişmiş veya boşalmış",
        onem=Onem.DUSUK,
        aciklama=(
            "Bölüm başına 10-30 kaynak aralığı korunur. Çok fazla girdi listeyi "
            "taranamaz yapar, çok az girdi ise bölümün anlamını yitirmesine yol açar."
        ),
        oneriler=(
            "Girdi sayısı 30'u aştıysa yeni bir alt başlık (##) açın; 10'un "
            "altındaysa bölümü birleştirmeyi değerlendirin."
        ),
    ),
)

KURALLAR_IDX: dict[str, Kural] = {k.kimlik: k for k in KURALLAR}
