# Kim Milyoner Olmak İster? — İstemci-Sunucu Mimarisiyle Quiz Oyunu

## Proje Hakkında

Bu proje, klasik *Kim Milyoner Olmak İster?* yarışmasının temel kurallarına sahip, *istemci-sunucu mimarisi* ile geliştirilmiş çok katmanlı bir bilgi yarışması oyunudur. Oyun hem *konsol* üzerinden hem de *grafiksel kullanıcı arayüzü (GUI)* ile oynanabilir. Proje, Python ile socket programlama kullanılarak, çoklu istemci desteğiyle, gerçek zamanlı soru-cevap ve joker mekanizmalarını destekler.

---

## İçindekiler

- [Proje Hakkında](#proje-hakkında)
- [Mimari ve Genel Akış](#mimari-ve-genel-akış)
- [Kullanılan Kütüphaneler ve Kurulum](#kullanılan-kütüphaneler-ve-kurulum)
- [Program Dosya Yapısı](#program-dosya-yapısı)
- [Çalıştırma Talimatları](#çalıştırma-talimatları)
- [Oyun Akışı ve Detaylar](#oyun-akışı-ve-detaylar)
- [Joker Mekanizması](#joker-mekanizması)

---

## Mimari ve Genel Akış

### Çalışma Sırası ve Akış Şeması

*Kod dosyaları sırasıyla şu şekilde çalıştırılmalıdır:*

1. *joker_server.py*  
   Joker mekanizmasını (Seyirciye Sorma, Yarı Yarıya) yöneten ayrı bir sunucudur. İstemcilerden gelen joker taleplerine cevap verir.

2. *program_server.py*  
   Oyun mantığının işlendiği ana sunucudur. Soru yönetimi, kullanıcıdan cevap alma, doğru/yanlış kontrolü ve joker taleplerinin yönlendirilmesi burada yapılır.

3. *GUI.py* veya *yarışmacı_client.py*  
   - GUI.py: Tkinter ve pygame ile hazırlanmış, kullanıcı dostu bir arayüz sağlar. Sunucu ile haberleşerek gerçek zamanlı olarak soruları ve cevapları yönetir.
   - yarışmacı_client.py: Konsol tabanlı istemcidir. GUI yerine terminalden oynamak isteyen kullanıcılar için tasarlanmıştır.

*Akış Şeması:*


joker_server.py (Joker Sunucusu)
             ↓
program_server.py (Ana Oyun Sunucusu)
             ↓
GUI.py (GUI) veya yarışmacı_client.py (Konsol)


- Önce *joker_server.py* başlatılır.
- Ardından *program_server.py* başlatılır.
- En son olarak *GUI.py* veya *yarışmacı_client.py* ile istemci başlatılır.

---

## Kullanılan Kütüphaneler ve Kurulum

Aşağıdaki kütüphaneler gereklidir:

- Python 3.8 veya üzeri
- [tkinter](https://docs.python.org/3/library/tkinter.html) (genellikle Python ile birlikte gelir)
- [pygame](https://www.pygame.org/) (ses efektleri için)
- Standart Python kütüphaneleri: socket, threading, signal, sys, time

*Gerekli paketleri kurmak için:*

bash
pip install pygame


> Not: Tkinter genellikle Python'un standart dağıtımıyla birlikte gelir. Eğer yüklü değilse:
> - *Windows:* Tkinter otomatik olarak gelir.
> - *Linux:*  
>   bash
>   sudo apt-get install python3-tk
>   

---

## Program Dosya Yapısı


- joker_server.py: Joker mekanizması için ayrı sunucu  
- program_server.py: Ana oyun sunucusu  
- GUI.py: Grafiksel kullanıcı arayüzü (Tkinter)  
- yarışmacı_client.py: Konsol tabanlı istemci  
- correct1.mp3: Doğru cevap sesi (GUI için)  
- wrong1.mp3: Yanlış cevap sesi (GUI için)  
- README.md: Bu dökümantasyon  


---

## Çalıştırma Talimatları

### 1. Gerekli Dosyaların Hazırlanması

Öncelikle, tüm .py dosyalarını aynı klasöre indirin ve GUI için gerekecek olan correct1.mp3 ve wrong1.mp3 ses dosyalarını da klasöre ekleyin.

### 2. Sunucuları ve İstemciyi Başlatma Sırası

*Adım Adım:*

1. *Joker Sunucusunu Başlat*
   bash
   python joker_server.py
   

2. *Program Sunucusunu Başlat*
   bash
   python program_server.py
   

3. *Oynamak İstediğiniz İstemci Türünü Seçin:*
   - *GUI ile Oynamak için:*
     bash
     python GUI.py
     
     - GUI açıldığında "Yarışmayı Başlat" butonuna tıklayın.
   - *Konsol ile Oynamak için:*
     bash
     python yarışmacı_client.py
     

> *Önemli Not:*  
> Dosyalar sırasıyla başlatılmalıdır:  
> 1. joker_server.py  
> 2. program_server.py  
> 3. GUI.py veya yarışmacı_client.py  
> Aksi takdirde, bağlantı hataları alabilirsiniz.

---

## Oyun Akışı ve Detaylar

Bu oyun toplam *5 sorudan* oluşur. Her soru için doğru cevabı verdiğinizde bir sonraki soruya ilerlersiniz ve ödül miktarınız artar. Her doğru cevap sonrası ödül ikiye katlanır ve büyük ödül *80.000 TL*'dir.

1. *Bağlantı*
   - İstemci programı sunucuya (program_server.py) bağlanır.
   - GUI'de, "Yarışmayı Başlat" butonuna tıklanarak bağlantı sağlanır.

2. *Soru Gönderimi ve Cevaplama*
   - Sunucu, sırayla toplam 5 soruyu ve şıklarını gönderir.
   - Kullanıcı GUI veya konsoldan cevap verir (A/B/C/D).
   - Her doğru cevap sonrası bir sonraki soruya geçilir ve ödül artar.

3. *Joker Kullanımı*
   - Kullanıcı, "S" (Seyirciye Sorma) veya "Y" (Yarı Yarıya) jokerlerini kullanabilir.
   - Sunucu, joker isteğini joker_server.py'a iletir ve cevabı kullanıcıya gösterir.
   - Her joker sadece 1 kez kullanılabilir.

4. *Doğru/Yanlış Durumu ve Ödül*
   - Doğru cevapta seviyeniz ve ödülünüz artar, GUI'de güncellenir ve sesli bildirim gelir.
   - Yanlış cevapta oyun biter, sunucu bilgi mesajı gönderir, GUI'de sesli uyarı ve bilgi kutusu çıkar.
   - Yanlış cevap verdiğinizde, o ana kadar kazandığınız ödül miktarı size gösterilir.

5. *Oyun Bitişi*
   - Tüm sorular doğru cevaplanırsa büyük ödül olan *80.000 TL*'yi kazanırsınız.
   - Yanlış cevapta veya bağlantı koparsa oyun sonlanır.
   - GUI'de tekrardan başlatmak için "Yarışmayı Başlat" butonunu kullanabilirsiniz.

---

## Joker Mekanizması

- *Seyirciye Sorma (S):*
  - Seyirci oylaması simülasyonu ile yüzdelik dağılımlar gönderilir.
- *Yarı Yarıya (Y):*
  - İki yanlış seçenek elenir, bir doğru ve bir yanlış seçenek bırakılır.

Jokerler sadece bir kez kullanılabilir ve tekrar seçilemez.
