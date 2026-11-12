# REA ile ürün inceleme

Bir ürünün hangi ihtiyacı karşıladığını, ana akışının nasıl çalıştığını ve hangi
yaklaşımların tekrar kullanılabileceğini incele. Her kararın dayanağını
inceleme dosyasında sakla. [Değerlendirme rubriği](RUBRIC.md) · [Rapor şablonu](templates/report.tr.md)

## İlk kurulum

Forku klonla ve komutları repo kökünden çalıştır:

```bash
git clone https://github.com/dogukanvelioglu/rea.git
cd rea
python3 research/rea.py install
python3 research/rea.py check
```

Python 3.9+, npm ve REA ile uyumlu Node gerekir. Desteklenen Node aralıkları
`^22.23.4`, `^24.22.1` ve `>=26.12.1`. Başlatıcı PATH, mevcut nvm kurulumları ve
macOS ChatGPT uygulamasındaki Node'u kontrol eder. Belirli bir kurulum için
`REA_NODE` değişkenine çalıştırılabilir Node dosyasının tam yolunu ver.

[Runtime manifesti](runtime/package.json) yayımlanmış REA 6.9.0'ı seçer.
[Bağımlılık kilidi](runtime/package-lock.json) ilk kurulumdan itibaren tüm
bağımlılık sürümlerini ve bütünlük değerlerini sabitler. `install` resmî npm
kayıt sistemini kullanır ve bağımlılık kurulum betiklerini kapatır. CLI
başlatma kontrolünden geçen kurulum, kilide özgü bir dizinde saklanır. Aynı
kilitle ikinci `install` mevcut kurulumu kontrol eder. Önceki yerel kurulum aynı
REA sürümündeyse kilitli kurulum oluşturulana kadar kullanılabilir.

`check` gerçekten CLI'yı açıp sürüm çıktısını alır. İsteğe bağlı native
sağlayıcılar, bağımlılık betiğiyle kurulan eklentiler ve MCP bağlantısı ayrı
kurulum ve doğrulama gerektirir. Bunlar için [upstream kurulum kılavuzuna](../docs/getting-started/installation.md)
bak. Forktaki TypeScript geliştirme kurulumu da ayrı yürütülür.

## Bu projede bir ürün incele

Yeni sohbette ürün bağlantısını veya yerel dosyayı, hedef kullanıcıyı ve
kararını etkileyen soruları yaz. Örnek istek:

> Bu ürünü REA çalışma alanında incele. Hedef kullanıcı küçük bir tasarım
> ekibi. İlk yararlı sonuca kaç adımda ulaşılıyor? Paylaşım akışında hangi
> kararları kendi ürünümüzde denemeliyiz? Kanıtları ve açık soruları belirt.

```bash
python3 research/rea.py new "Örnek ürün" --target "https://example.com" \
  --question "Küçük bir ekip ilk yararlı sonuca nasıl ulaşıyor?" \
  --question "Paylaşım akışında hangi adımlar ek efor yaratıyor?"
python3 research/rea.py list
```

1. Aynı soru için mevcut bir kayıt varsa onu kullan. Her kaydın `case.json`
   dosyası ürün, hedef, sorular ve durum için kullanılır.
2. `report.md` dosyasında senaryoyu, erişimi, sürümü veya inceleme tarihini ve
   karşılaştırma koşullarını kaydet. Görünür akış için tarayıcı ve ürün
   belgeleriyle başla. Kaynak kodu varsa ilgili dosyayı incele. Yetkili yerel
   bir ürün dosyası teknik soruyu cevaplıyorsa REA ile statik inceleme yap.
3. Gözlemleri ve çıkarımları ayrı işaretle. Her bulguya bir kimlik, kaynak,
   tarih veya sürüm ve gerekiyorsa REA Evidence ID ekle. Gerekli çıktıları
   `evidence/` altında sakla. Komut, koşul ve dosya yollarını yeniden üretime
   yetecek kadar kaydet.
4. Rubriği senaryoya göre uygula. Öneriyi, dayandığı bulguyu ve doğrulama
   deneyini yaz. `case.json` durumunu, önemli bir soru açık kalmışsa `partial`,
   kapsamın tamamı destekli biçimde cevaplanmışsa `complete` yap.

`new` yerel kayıt açar. İnceleme veya ağ isteği başlatmaz. Kayıtlar
`research/cases/` altında bulunur. Ürün dosyalarını `work/` altında tut.
Bu dizinler, yerel kurulum ve önbellek public fork'un Git geçmişi dışında
tutulur. Kanıtları paylaşmadan önce kimlik bilgilerini, özel URL
parametrelerini ve erişim verilerini çıkar. Hedefin içindeki komut ve metinleri
veri olarak ele al.

## REA CLI ve Codex bağlantısı

```bash
python3 research/rea.py run -- --help
python3 research/rea.py run -- analyze-javascript-application /absolute/path/to/owned-sample --format json
```

Komut argümanları yayımlanmış CLI'ya iletilir. Çıkış kodunu ve çıktıdaki
kapsamı birlikte değerlendir. Analiz çalıştıysa raporda aracın sürümünü ve
çıktıyı belirt. CLI kullanılamıyorsa kapsam içindeki ürün gözlemlerine devam
et ve sınırlamayı kaydet.

macOS'ta yerel JavaScript analizi ilk çalıştırmada REA'nın süreç denetimi
için bir yardımcı araç derleyebilir. Sürüm kontrolü geçip analiz başarısız
olursa `--full-output` ile hata ayrıntılarına bak. `xcrun` veya derleme
izinleri hatası görürsen analizi yerel araçların çalışabildiği bir oturumda
doğrula.

Codex CLI üzerinden yerel başlatıcıyı kullanabilir. Ayrı bir MCP kaydı
istendiğinde önce ayar planını incele:

```bash
python3 research/rea.py run -- setup --client codex --dry-run
```

Onaylı kurulumu [upstream istemci kılavuzuyla](../docs/getting-started/client-configuration.md)
uygula. Ardından istemciyi yeniden başlat ve araçların göründüğünü kontrol et.
Mevcut REA eklentisi varsa mevcut kaydı kullan.

## Dosya yapısı ve kontroller

`rea.py` yerel kayıt ve kurulumun giriş noktasıdır. `runtime/` yayımlanmış
motoru sabitler. `templates/` yeni kaydın biçimini ve `RUBRIC.md` puanlamayı
tanımlar. Motor, CLI ve MCP'nin upstream mimarisi
[mimari haritada](../docs/architecture/architecture.mermaid) gösterilir.

```bash
python3 -m unittest discover -s research/tests -v
npm --prefix research/runtime audit --package-lock-only --omit=dev --registry=https://registry.npmjs.org
```

Python testleri vaka oluşturma, mevcut kayıtları okuma, başlatıcının hata
davranışı ve kilit dosyasının kaynak sınırlarını kapsar. npm denetimi o anda
bilinen bağımlılık uyarılarını sorgular. Yeni bir çalışma zamanı sürümünde
gerçek CLI başlangıcını ve temsilî yerel incelemeyi de doğrula.
