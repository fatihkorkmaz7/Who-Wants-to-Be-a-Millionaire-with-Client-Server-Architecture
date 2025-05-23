# ============================================
#  Kod dosyaları joker_server ==> program_server ==> GUI sırasıyla çalıştırılmalıdır.
#  joker_server, oyunun sunucu tarafını yönetir ve istemcilerden gelen
#  joker taleplerine yanıt verir.
# ============================================


import socket  # TCP/IP bağlantıları için socket modülünü içe aktarıyoruz.
import signal  # Programın kapanması durumunda düzgün bir sonlandırma işlemi için signal modülünü kullanıyoruz.
import sys  # Sistemle ilgili işlemleri yönetebilmek için sys modülünü içe aktarıyoruz.


# Program sonlandırıldığında (örneğin, Ctrl+C ile) çalışacak sinyal işleyici fonksiyon
def signal_handler(sig, frame):
    print("\nSunucu kapatılıyor...")  # Kullanıcıya sunucunun kapanmakta olduğunu bildiriyoruz.

    # Eğer server_socket global olarak tanımlandıysa, bağlantıyı düzgün bir şekilde kapatıyoruz.
    if 'server_socket' in globals():
        server_socket.close()  # Aktif bağlantıyı kapatıyoruz, böylece kaynaklar serbest bırakılır.

    sys.exit(0)  # Programı başarıyla sonlandırıyoruz (0 değeri başarılı çıkışı belirtir).


def start_joker():
    server_ip = '127.0.0.1'
    server_port = 4338

    # Signal handler'ı ayarla (Ctrl+C ile düzgün kapanma için)
    signal.signal(signal.SIGINT, signal_handler)

    # Global erişim için server_socket'i global olarak tanımla
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SO_REUSEADDR ayarı, sunucu yeniden başlatıldığında "address already in use" hatasını önler
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Soru bazlı joker yanıtları
    seyirci_yanıtları = [
        "\nA) TCP üçlü el sıkışmayı kullanır ve UDP mesajın teslimini garanti etmez. (%85)\nB) TCP senkronizasyon paketlerini, UDP ise onay paketlerini kullanır. (%5)\nC) UDP güvenilir mesaj aktarımı sağlar, TCP ise bağlantısız bir protokoldür. (%5)\nD) UDP çerçeve başlığında SYN, SYN ACK ve FIN bitlerini kullanırken TCP SYN, SYN ACK ve ACK bitlerini kullanır. (%5)",
        # 1. soru
        "\nA) 192.168.0.1 - 192.168.0.32 (%45)\nB) 192.168.0.1 - 192.168.0.64 (%5)\nC) 192.168.0.1 - 192.168.0.30 (%45)\nD) 192.168.0.1 - 192.168.0.28 (%5)",
        # 2. soru
        "\nA) OSPF Stub Area kullanılarak (%20)\nB) OSPF Virtual Link kullanılarak (%30)\nC) OSPF NSSA kullanılarak (%25)\nD) OSPF Totally Stubby Area kullanılarak (%25)",
        # 3. soru
        "\nA) MAC flooding (%15)\nB) Port mirroring (%25)\nC) Static ARP entries (%30)\nD) Dynamic ARP Inspection (%30)",
        # 4. soru
        "\nA) TTL değerini azaltarak (%5)\nB) RTT ölçümüne göre pencereyi artırarak (%30)\nC) Zaman aşımı veya üçlü ACK ile pencereyi küçülterek (%35)\nD) ACK paketlerini sıralayarak yeniden aktarım yaparak (%30)"
        # 5. soru
    ]

    yarı_yarıya_yanıtları = [
        "\nA) TCP üçlü el sıkışmayı kullanır ve UDP mesajın teslimini garanti etmez.\nC) UDP güvenilir mesaj aktarımı sağlar, TCP ise bağlantısız bir protokoldür.",
        # 1. soru
        "\nA) 192.168.0.1 - 192.168.0.32\nC) 192.168.0.1 - 192.168.0.30",  # 2. soru
        "\nB) OSPF Virtual Link kullanılarak\nC) OSPF NSSA kullanılarak",  # 3. soru
        "\nC) Static ARP entries\nD) Dynamic ARP Inspection",  # 4. soru
        "\nB) RTT ölçümüne göre pencereyi artırarak\nC) Zaman aşımı veya üçlü ACK ile pencereyi küçülterek"  # 5. soru
    ]

    try:
        # Sunucu IP ve portuna bağlanmak ve dinlemeye başlamak için socket'i yapılandırıyoruz.
        server_socket.bind((server_ip, server_port))  # Sunucuyu belirlenen IP adresi ve port numarasına bağla.
        server_socket.listen(5)  # Sunucuya gelen bağlantı taleplerini kabul et, 5 bağlantıya kadar izin ver.
        print(f"Joker Sunucusu {server_ip}:{server_port} adresinde çalışıyor. Dinleniyor...")  # Sunucunun başarılı bir şekilde başlatıldığını bildir.

        while True:
            try:
                # Bir istemciden gelen bağlantıyı kabul et
                client_socket, client_address = server_socket.accept()  # İstemci ile bağlantıyı kabul et.
                print(f"Yeni bağlantı kabul edildi: {client_address}. Bağlantı başlatılıyor...")  # Yeni bağlantıyı bildir.

                # Bağlantıyı işlerken, istemciyi handle_client fonksiyonuna yönlendir
                handle_client(client_socket, client_address, seyirci_yanıtları, yarı_yarıya_yanıtları)
            except Exception as e:
                # Bağlantı sırasında bir hata oluşursa, hata mesajı ver ve döngüye devam et
                print(f"Bağlantı hatası: {e}. Bir hata oluştu, tekrar denenecek.")
                continue  # Hata oluştuğunda bağlantı kurulmaya devam edilir.

    except Exception as e:
        # Sunucu başlatılamazsa, hata mesajı ver ve programı sonlandır
        print(f"Sunucu başlatma hatası: {e}. Sunucu başlatılamadı. Çıkılıyor.")
    finally:
        # Sunucu kapatılırken socket bağlantısı düzgün bir şekilde temizlenir
        server_socket.close()  # Sunucu socket'ini kapatıyoruz.
        print("Sunucu kapanıyor... Socket bağlantısı temizlendi.")  # Kullanıcıya sunucu kapanma durumunu bildir.



def handle_client(client_socket, client_address, seyirci_yanıtları, yarı_yarıya_yanıtları):
    try:
        while True:
            # İstemciden veri almak için recv() fonksiyonu çağrılır
            data = client_socket.recv(1024)  # 1024 byte'lık veri alınır
            if not data:  # Eğer veri alınamazsa, bağlantı kapanmış demektir
                break

            # Veriyi UTF-8 formatında çöz (mesaj bir string olarak gönderildi)
            message = data.decode('utf-8')

            # Mesajı joker tipi ve soru indeksine göre ayır (format: "JokerTipi:SoruIndeksi")
            parts = message.split(':')  # Mesajı ':' karakterine göre bölüyoruz
            joker_type = parts[0]  # Joker tipini alıyoruz
            question_index = 0  # Varsayılan olarak 0. soruyu alır

            if len(parts) > 1:
                try:
                    # Soru indeksini alıp integer'a dönüştürmeye çalışıyoruz
                    question_index = int(parts[1])
                except ValueError:
                    # Eğer indeks bir sayı değilse, 0 kabul edilir
                    question_index = 0

            # Joker tipi ve soru indeksini logla
            print(f"İstemci '{joker_type}' jokerini {question_index + 1}. soru için istedi.")

            # Soru indeksinin geçerli aralıkta olduğundan emin ol
            if question_index >= len(seyirci_yanıtları):
                # Eğer indeks aralığın dışındaysa, son soruyu seç
                question_index = len(seyirci_yanıtları) - 1

            # Joker türüne göre cevabı belirle
            if joker_type == 'S':  # Seyirciye Sorma Jokeri
                response = seyirci_yanıtları[question_index]  # İlgili soru için seyirci yanıtı
            elif joker_type == 'Y':  # Yarı Yarıya Jokeri
                response = yarı_yarıya_yanıtları[question_index]  # İlgili soru için yarı yarıya yanıtı
            else:
                # Eğer joker tipi geçersizse
                response = "Bilinmeyen joker tipi"

            # Cevabı logla ve istemciye gönder
            print(f"Joker cevabı: '{response}' gönderildi. İstemciye iletildi.")
            client_socket.send(response.encode('utf-8'))  # Cevabı istemciye gönder

    except Exception as e:
        # Eğer bir hata oluşursa, hata mesajı yazdırılır ve bağlantı kapatılır
        print(f"İstemci işleme hatası: {e}. Hata oluştu, bağlantı kapatılacak.")
    finally:
        # Bağlantı sonlandırıldığında, socket kapatılır ve bağlantı kapanır
        print(f"Bağlantı kapatıldı: {client_address}. İstemci bağlantısı sonlandırıldı.")
        client_socket.close()



if __name__ == "__main__":
    start_joker()
