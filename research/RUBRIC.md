# Ürün değerlendirme rubriği · v1

İncelemeye hedef kullanıcıyı, yapılacak işi ve verilecek kararı yazarak başla.
Tek özellik inceleniyorsa kapsamı o özellikle sınırla. Ürün karşılaştırırken
aynı senaryo, sürüm veya inceleme tarihi, cihaz ve paket koşullarını kullan.

| Boyut | İnceleme sorusu | Örnek kanıt |
| --- | --- | --- |
| Problem ve hedef kullanıcı | Ürün kimin hangi işini çözüyor? Sonuç kullanıcı için ne kadar anlamlı? | Denenen senaryo, ürün dokümanı, kullanıcı geri bildirimi |
| İlk değer ve onboarding | İlk yararlı sonuca hangi adımlarla ulaşılıyor? Kullanıcı nerede yardıma ihtiyaç duyuyor? | Adım sayısı, süre, varsayılanlar, izin ve kurulum adımları |
| Ana iş akışı ve hata yönetimi | Kullanıcı işi tamamlayabiliyor mu? Hataları anlayıp toparlayabiliyor mu? | Temsilî akış, hata mesajı, düzeltme adımı, erişilebilirlik gözlemi |
| Ayrışma ve alternatifler | Aynı işi yapan alternatiflere göre hangi somut avantajı ve ödünleşimi var? | Eşdeğer senaryoyla karşılaştırma, kaynak tarihleri |
| Teknik kalite ve entegrasyon | Gözlenebilir hız, kararlılık ve entegrasyonlar kullanım senaryosunu ne kadar destekliyor? | Ölçüm koşulları, resmi API dokümanı, yerel REA bulgusu |
| Güven ve veri kontrolü | Erişim, veri dışa aktarma ve gizlilik seçenekleri kullanım için yeterli mi? | İzin ekranı, dışa aktarma denemesi, tarihli politika |
| Fiyat ve kullanım maliyeti | Gerekli özellikler hangi pakette? Para, kurulum, geçiş ve işletim maliyetine değer mi? | Tarihli fiyat sayfası, paket sınırları ve açık maliyet varsayımları |

## Puan ve güven

| Puan | Senaryoda gözlenen durum |
| --- | --- |
| 1 | İhtiyacı karşılayamıyor veya kritik bir adımı engelliyor. |
| 2 | İhtiyacı kısmen karşılıyor. Belirgin bir geçici çözüm ya da efor gerekiyor. |
| 3 | Temel ihtiyacı karşılıyor. Gözlenen eksikler yönetilebilir. |
| 4 | İhtiyacı iyi karşılıyor. Küçük sürtünmeler var. |
| 5 | Temsilî koşullarda güçlü ve tutarlı sonuç veriyor. |
| Bilinmiyor | Eldeki kanıt puan vermeye yetmiyor. |
| Kapsam dışı | Boyut bu incelemenin sorularına uygulanmıyor. |

Her puana kısa bir gerekçe, en az bir bulgu kimliği ve güven düzeyi ekle.
**Yüksek** güven için bulgu aynı koşullarda tekrar gözlenmeli veya bağımsız
kanıtla desteklenmeli. **Orta** güven için kapsamı belli bir doğrudan gözlem ya
da iddiaya uygun birincil kaynak yeterli olabilir. **Düşük** güveni sınırlı örnek
veya dolaylı çıkarımda kullan. Kanıt çok zayıfsa puanı bilinmiyor bırak.
Örneğin resmi fiyat sayfası tarihli liste fiyatını destekler. Bir pazarlama
sayfası tek başına gerçek kullanımda hız veya güvenilirlik puanını desteklemez.

Varsayılan çıktı boyut puanları ve karar gerekçesidir. Bir toplam puan
istenirse ağırlıkları inceleme öncesinde kaydet. Karşılaştırılabilirlik için
aynı kapsamı kullan ve puanlanamayan gerekli bir boyut varsa toplamı açık bırak.
Kararı etkileyen engelleri, belirsizlikleri ve sıradaki doğrulama adımını özete al.

## Bulguyu kaydet

- **Gözlem** doğrudan görülen davranış, ölçüm veya kaynağın açıkça söylediği iddiadır.
- **Türetim** gözlemlenmiş veriden tekrar hesaplanabilen sonuçtur.
- **Çıkarım** kanıtın desteklediği, alternatif açıklaması olabilecek yorumdur.
- **Bilinmiyor** doğrulanamayan veya erişilemeyen bilgidir.

Örneğin `F01`, test hesabının ilk yararlı çıktıya dört adımda ulaştığı bir
gözlem olsun. Onboarding satırında `4 · orta · F01` verilebilir ve tek hesapta
denendiği yazılır. Yönetici onayı gerektiren kurumsal hesap akışı bilinmiyor kalır.
