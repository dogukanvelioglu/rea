# REA ürün inceleme alanı

Bu fork, REA'yı sohbetten ürün ve özellik incelemek için kullanır. Motorun
kaynak kodu upstream ile korunur; bu dizin kurulum, inceleme kaydı ve Türkçe
raporlama katmanıdır. Bir web uygulaması veya dashboard değildir.

## İlk kurulum

Forkun kök dizininde:

```bash
python3 research/rea.py install
python3 research/rea.py check
```

Python 3.9+ ve npm gerekir. Başlatıcı önce mevcut Node sürümlerini kontrol eder;
uyumlu PATH sürümü, `/usr/local/bin/node`, macOS ChatGPT uygulamasındaki runtime
ve mevcut nvm kurulumları kullanılabilir. Alternatif olarak `REA_NODE` ile tam
bir Node yolu seçilebilir. Node veya diğer sistem yazılımları kurulmaz.

REA **6.8.0** yalnızca `research/.runtime` altına kurulur; npm önbelleği
`research/.cache` altındadır. İlk kurulumun oluşturduğu dependency lock sonraki
kurulumlarda `npm ci` ile kullanılır. Sürüm yükseltmeleri açıkça planlanmalıdır.
Bu sürüm yayımlanmış npm paketidir; forkun `main` dalındaki her yeni özellik
bu pakette bulunmayabilir. Gerçek CLI/MCP araç listesini esas al.

`check` gerçek REA CLI'sını başlatır; sadece dosya varlığından başarı çıkarmaz.
Node uyumluluğunu geçmek MCP bağlantısının veya Ghidra/Hopper'ın hazır olduğunu
göstermez. Paket indirmesi veya bağımlılık çözümü başarısızsa kurulum tamamlanmış
sayılmaz; ağ erişimi sağlandıktan sonra aynı `install` komutunu yeniden çalıştır.

## Bu sohbette kullanım

Ürünün bağlantısını veya uygulama dosyasını ve anlamak istediğin özelliği yaz:

> Bu ürünü REA ile incele. Onboarding ve arama akışını, arkasındaki teknik
> mekanizmayı ve kendi ürünümüzde uygulayabileceğimiz fikirleri kanıtlarıyla anlat.

İnceleme dosyası açmak ve geçmişi görmek için:

```bash
python3 research/rea.py new "Örnek ürün" --target "https://example.com" \
  --question "İlk değer anına nasıl ulaşılıyor?" \
  --question "Arama istemcide mi sunucuda mı çalışıyor?"
python3 research/rea.py list
```

Her çalışma `cases/<tarih>-<ürün>-<kimlik>/` altında `case.json`, `report.md`
ve `evidence/` alır. Yeni kayıt açmak REA analizi çalıştırmaz. Tamamlanan
raporda kanıt bağlantıları ve sınırlar bulunmalı; `case.json` durumu ancak
gerçek sonuç değerlendirildikten sonra `partial` veya `complete` yapılmalıdır.

İncelemeler, hedef dosyalar, ağ kayıtları ve çalışma zamanı Git'e dahil edilmez.
Bu public fork yalnızca araçları ve boş şablonları paylaşır. Özel bulguları
yayınlamak ayrı bir kullanıcı talebi gerektirir.

## REA komutları

```bash
python3 research/rea.py run -- --help
python3 research/rea.py run -- doctor --json
python3 research/rea.py run -- analyze-javascript-application /absolute/path/to/app --json
```

CLI JSON çıktısını ilgili incelemenin `evidence/` dizinine kaydet. Komut çıkış
kodunu ve JSON'daki sonuç/limitleri değerlendir; boş veya yarım çıktıyı bulgu
sayma. Kaynak kodu mevcut sıradan bir repo incelemesinde normal kod araçlarını
kullan; REA'yı paket, binary veya çalışma zamanı kanıtı gerektiğinde seç.

Web ürünlerinde önce kullanıcı akışını mevcut tarayıcı araçlarıyla incele.
REA ile ağ kaydı, dağıtılan script veya runtime analizi gerektiğinde
[web rehberindeki](../docs/guides/web/browser-observation.md) gerçek komut ve
şemaları kullan. Tarayıcı oturumunu ilgisiz hesaplara genişletme.

## İsteğe bağlı Codex MCP bağlantısı

Bu sohbet CLI üzerinden çalışabilir. MCP ayrıca kaydedilir ve istemci yeniden
başlatılır; aşağıdaki komutlar bu hazırlığın kendiliğinden tamamlandığı anlamına
gelmez. Mevcut bir REA plugin'i varsa ikinci bir sunucu kaydı oluşturma.

Önce değişiklik planını göster:

```bash
python3 research/rea.py run -- setup --client codex --dry-run
```

Plan mevcut ayarları koruyup yedekleyecek yolları gösterdikten sonra:

```bash
python3 research/rea.py run -- setup --client codex --yes
```

Bu ikinci komut Codex'in kullanıcı ayarlarını ve REA iş akışı talimatlarını
günceller. İstemciyi yeniden başlatıp REA araçlarının göründüğünü doğrula.
Tam kılavuz: [Kurulum](../docs/getting-started/installation.md).

## İnceleme standardı

1. Ürün, sürüm, hedef özellik ve araştırma sorularını belirle.
2. En küçük yeterli incelemeyle başla; yalnızca açık kalan sorular için derinleş.
3. Gözlem, türetim, çıkarım ve bilinmeyenleri ayır; bulguları kanıta bağla.
4. Kullanıcı akışı ve teknik mekanizmayı ürün açısından yorumla.
5. Öneriyi kendi tasarım kararımız olarak belirt; gözlemlenmiş davranışla karıştırma.
6. Sonucu, sınırlamaları ve yeniden üretim adımlarını kaydet. Aktif REA
   oturumunu bitirirken gerekli bundle'ı dışa aktar.

## Yerel kontroller

```bash
python3 -m unittest discover -s research/tests -v
```

Bu testler çalışma alanı kayıtlarını ve başlatıcının hata davranışını doğrular;
REA motoru, web tarayıcısı veya native sağlayıcı doğrulaması yerine geçmez.
