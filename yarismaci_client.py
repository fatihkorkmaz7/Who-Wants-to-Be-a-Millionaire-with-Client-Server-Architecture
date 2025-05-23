# ============================================
#  yarismaci_client dosyası "Kim Milyoner Olmak İster" yarışma oyununu istemci tarafında çalıştırmak için
#  kullanılan konsol tabanlı istemci kodunu içerir
#  Oyun isteğe bağlı olarak konsol tabanlı veya GUI ile çalıştırılabilir.
#  Sırasıyla joker_server ve program_server dosyaları çalıştırıldıktan sonra GUI ile oynamak için GUI dosyası,
#  konsol tabanlı oynamak için yarismaci_client (bu dosya) çalıştırılmalıdır.
#
#  yarismaci_client , "program_server" ile iletişim kurarak oyun sırasında sunucudan gelen
#  soruları alır, cevapları girer ve joker kullanımını yönetir. Kullanıcıdan gelen cevaplar
#  doğrudan konsola girilir ve sunucuya iletilir.
#
#  İşlevsel özellikler:
#  1. Program sunucusuna bağlanarak oyun başlatılır.
#  2. Sunucudan gelen mesajları alarak konsola yazdırır.
#  3. Kullanıcıdan cevap alınır ve joker kullanımı için kullanıcıyı yönlendirir.
#  4. Oyun bittiğinde kullanıcıya oyun sona erdiği bildirilir.
#
#  Bağlantı Detayları:
#  - Bu istemci, "program_server" sunucusuna bağlanarak soruları alır ve cevapları gönderir.
#  - Sunucu ile iletişim TCP/IP üzerinden gerçekleşir (IP: 127.0.0.1, Port: 4337).
#  - Oyun süresince gelen her mesaj ekranda yazdırılır ve kullanıcıdan cevap istenir.
#
#  Çalıştırma Talimatları:
#  1. **joker_server.py** dosyasını çalıştırarak joker özelliklerini sunan sunucuyu başlatın.
#  2. **program_server.py** dosyasını çalıştırarak ana oyun sunucusunu başlatın.
#  3. Bu dosyayı çalıştırarak istemciyi başlatın.
#  4. Sunucu tarafından gönderilen sorulara konsolda cevap verin.
#
#  Hata yaşamamak adına joker kullanımlarından hemen sonra cevap vermeyip
#  joker yanıtını görüp enter'a bastıktan sonra soru seçeneğini yollamak önem ar ez eder.
# ============================================


import socket

def start_client():
    server_ip = '127.0.0.1'
    server_port = 4337  # Program Sunucusu'na bağlanacak port

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Program sunucusuna ({server_ip}:{server_port}) bağlanılıyor...")
        client_socket.connect((server_ip, server_port))
        print("Bağlantı kuruldu!")

        # Ana oyun döngüsü
        while True:
            try:
                # Sunucudan mesaj al
                data = client_socket.recv(1024).decode('utf-8')
                if not data:  # Sunucu bağlantıyı kapattıysa
                    print("Sunucu bağlantıyı kapattı.")
                    break

                print(data)  # Gelen mesajı yazdır

                # Oyun sonu kontrolü
                if "Oyun bitti" in data or "Tebrikler" in data:
                    print("Oyun sona erdi!")
                    break

                # Sunucudan cevap/joker talep ediliyorsa
                if "Cevabınız" in data or "joker" in data.lower():
                    answer = input("► ")  # Kullanıcıdan input al
                    client_socket.send(answer.strip().upper().encode('utf-8'))

            except KeyboardInterrupt:
                print("\nProgram kullanıcı tarafından sonlandırıldı.")
                break

            except Exception as e:
                print(f"Oyun sırasında hata: {e}")
                break

    except ConnectionRefusedError:
        print(f"Bağlantı reddedildi. Program sunucusu ({server_ip}:{server_port}) çalışıyor mu?")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
    finally:
        if 'client_socket' in locals():
            client_socket.close()
        print("İstemci kapatıldı.")


if __name__ == "__main__":
    start_client()