# ============================================
#  Kod dosyaları joker_server ==> program_server ==> GUI sırasıyla çalıştırılmalıdır.
#  program_server, oyun sunucusu tarafındaki işlevleri yönetir, istemcilerle
#  bağlantıyı sağlar ve soruları sırasıyla iletir. Ayrıca joker kullanımı ve
#  cevabın doğruluğunu kontrol eder.
# ============================================

import socket
import time
import signal
import sys


def signal_handler(sig, frame):
    print("\nSunucu kapatılıyor...")
    if 'server_socket' in globals():
        server_socket.close()  # Sunucu socket bağlantısını kapat
    sys.exit(0)  # Programdan çık



def get_joker_suggestion(joker_type, question_index):
    try:
        joker_ip = '127.0.0.1'  # Joker sunucusunun IP adresi
        joker_port = 4338  # Joker sunucusunun port numarası
        joker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP soket oluşturuluyor
        joker_socket.connect((joker_ip, joker_port))  # Joker sunucusuna bağlan

        # Joker tipi ve soru indeksini mesaj olarak gönder
        message = f"{joker_type}:{question_index}"
        joker_socket.send(message.encode('utf-8'))  # Mesajı gönder

        # Joker sunucusundan yanıt al
        response = joker_socket.recv(1024).decode('utf-8')  # 1024 byte veri al ve UTF-8 formatında çöz
        joker_socket.close()  # Bağlantıyı kapat

        # Konsola bilgi yazdır (Joker tipi ve sonucu)
        joker_ad = "Seyirciye Sorma" if joker_type == "S" else "Yarı Yarıya"
        print(f"JOKER KULLANILDI >> Tür: {joker_ad}, Soru: {question_index + 1}, Sonuç: {response}")

        return response  # Yanıtı döndür
    except Exception as e:
        # Joker sunucusuna bağlantı hatası durumunda hata mesajı
        print(f"Joker sunucusuna bağlantı hatası: {e}")
        return "Joker sunucusuna bağlanılamadı!"


def get_exit_message(score):
    if score == 0:
        return "Keşke sadece evde yarışsaydınız..."
    elif score == 1:
        return "Vasatın üstü..."
    elif score == 2:
        return "Fena değil, biraz daha çalışırsan büyük ödül senin olabilir!"
    elif score == 3:
        return "Ortalama üstü bir performans! Az kaldı, pes etme!"
    elif score == 4:
        return "Bir soru kala elenmek... Resmen kalbimiz kırıldı!"
    else:
        return "Zaten kazandın, bu mesajı asla görmeyeceksin 😎"


def start_server():
    # Sunucu IP adresi ve port numarasını belirle
    server_ip = '127.0.0.1'  # Bu, localhost (yerel makine) adresidir
    server_port = 4337  # Sunucu için kullanılacak port numarası

    # Sunucuya Ctrl+C (SIGINT) sinyali gönderildiğinde düzgün bir şekilde kapanması için signal handler'ı ayarla
    signal.signal(signal.SIGINT, signal_handler)

    # Global olarak kullanılacak server_socket soketini tanımla
    global server_socket
    # TCP/IP soketini oluştur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Sunucunun adresi yeniden kullanılması için soket opsiyonlarını ayarla (address reuse)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Sunucu IP adresine ve port numarasına bağlan (bind işlemi)
        server_socket.bind((server_ip, server_port))

        # Sunucunun bağlantı kabul etmeye başlamasını sağla
        server_socket.listen(5)  # En fazla 5 bağlantıyı kabul etme sınırı

        print(f"Program Sunucusu {server_ip}:{server_port} adresinde çalışıyor...")

        # Sonsuz döngüde sürekli bağlantı kabul et
        while True:
            try:
                # Yeni bir istemciden gelen bağlantıyı kabul et
                client_socket, client_address = server_socket.accept()
                print(f"Bağlantı kuruldu: {client_address}")

                # Her yeni bağlantı için, handle_client fonksiyonu ile işlem başlat
                handle_client(client_socket, client_address)
            except Exception as e:
                # Eğer bağlantı sırasında hata oluşursa, hata mesajı yazdırılır
                print(f"Bağlantı hatası: {e}")
                continue  # Hata oluşsa bile döngüye devam et

    except Exception as e:
        # Sunucu başlatılırken hata oluşursa, hata mesajını yazdır
        print(f"Sunucu başlatma hatası: {e}")
    finally:
        # Sunucu kapanırken, soket bağlantısını temizle
        server_socket.close()


def handle_client(client_socket, client_address):
    try:
        # Sorular ve şıkları, her biri bir sözlükte tutulmaktadır.
        # Her sözlük, bir soru, o soruya ait şıklar ve doğru cevap içerir.
        # Sorular bir liste içinde sıralanır.
        questions = [
            {
                "question": "TCP ve UDP iki uç nokta arasında bağlantı kurma biçimleri açısından nasıl farklılık gösterir?",
                "options": [
                    "A) TCP üçlü el sıkışmayı kullanır ve UDP mesajın teslimini garanti etmez.",
                    "B) TCP senkronizasyon paketlerini, UDP ise onay paketlerini kullanır.",
                    "C) UDP güvenilir mesaj aktarımı sağlar, TCP ise bağlantısız bir protokoldür.",
                    "D) UDP çerçeve başlığında SYN, SYN ACK ve FIN bitlerini kullanırken TCP SYN, SYN ACK ve ACK bitlerini kullanır."
                ],
                "answer": "A"
            },
            {
                "question": "CIDR notasyonunda /27 subnet maskesi ile hangi aralıkta IP adresi atanabilir?",
                "options": [
                    "A) 192.168.0.1 - 192.168.0.32",
                    "B) 192.168.0.1 - 192.168.0.64",
                    "C) 192.168.0.1 - 192.168.0.30",
                    "D) 192.168.0.1 - 192.168.0.28"
                ],
                "answer": "C"
            },
            {
                "question": "Farklı OSPF Area’larındaki iki router arasındaki iletişim nasıl sağlanır?",
                "options": [
                    "A) OSPF Stub Area kullanılarak",
                    "B) OSPF Virtual Link kullanılarak",
                    "C) OSPF NSSA kullanılarak",
                    "D) OSPF Totally Stubby Area kullanılarak",
                    "E) Fiziksel bağlantı eklenerek"
                ],
                "answer": "B"
            },
            {
                "question": "Bir saldırgan, ağda sahte ARP yanıtları göndererek IP-MAC eşleşmelerini bozuyor. Bunu önlemek için switch’te ne yapılandırılır?",
                "options": [
                    "A) MAC flooding",
                    "B) Port mirroring",
                    "C) Static ARP entries",
                    "D) Dynamic ARP Inspection"
                ],
                "answer": "D"
            },
            {
                "question": "TCP, ağda tıkanıklık oluştuğunu nasıl tespit eder ve hangi mekanizma ile yönetir?",
                "options": [
                    "A) TTL değerini azaltarak",
                    "B) RTT ölçümüne göre pencereyi artırarak",
                    "C) Zaman aşımı veya üçlü ACK ile pencereyi küçülterek",
                    "D) ACK paketlerini sıralayarak yeniden aktarım yaparak"
                ],
                "answer": "C"
            }
        ]

        score = 0  # Başlangıçta doğru cevap sayısı sıfırdır.
        available_jokers = ["S", "Y"]  # Kullanılabilir jokerler: Seyirciye Sorma (S) ve Yarı Yarıya (Y)

        # İstemciye hoş geldin mesajı gönderilir
        welcome_message = "Kim Milyoner Olmak İster'e Hoş Geldiniz!\n"
        client_socket.send(welcome_message.encode('utf-8'))
        time.sleep(0.1)

        # Soruların sırasıyla işlenmesi
        for i, question in enumerate(questions):
            print(f"Soru {i + 1} gönderiliyor...")  # Sorunun konsola yazdırılması
            question_text = question['question']  # Sorunun metni
            options = "\n".join(question['options'])  # Şıkları listele
            answer = question['answer']  # Doğru cevabı al

            while True:
                # Jokerlerin durumu gösterilir
                jokers_info = "Kullanılabilir jokerler: "
                if available_jokers:  # Eğer joker varsa
                    for j in available_jokers:
                        if j == 'S':
                            jokers_info += "Seyirciye Sorma (S), "
                        elif j == 'Y':
                            jokers_info += "Yarı Yarıya (Y), "
                    jokers_info = jokers_info.rstrip(", ")
                else:
                    jokers_info += "Yok"  # Hiç joker kalmamışsa "Yok" mesajı gönderilir

                # Soruyu ve seçenekleri istemciye gönder
                full_question = f"\nSoru {i + 1}: {question_text}\n{options}\n\n{jokers_info}\nCevabınız (A/B/C/D)"
                if available_jokers:  # Eğer jokerler varsa, joker seçeneği eklenir
                    full_question += " veya joker (S/Y)"
                full_question += ": "
                client_socket.send(full_question.encode('utf-8'))

                # İstemciden cevabı al
                response = client_socket.recv(1024).decode('utf-8').strip().upper()  # Cevap A, B, C, D, S veya Y olabilir

                # Eğer joker kullanılmışsa
                if response in ['S', 'Y']:
                    if response in available_jokers:  # Joker kullanılabilir mi kontrolü
                        joker_type = response  # Joker tipi alınır
                        available_jokers.remove(joker_type)  # Kullanılan joker listeden çıkarılır
                        joker_response = get_joker_suggestion(joker_type, i)  # Joker sunucusundan yanıt alınır
                        client_socket.send(f"Joker sonucu: {joker_response}\n".encode('utf-8'))
                        continue  # Joker kullanıldıktan sonra aynı soruya devam edilir
                    else:
                        # Eğer joker hakkı yoksa, kullanıcıya uyarı gönderilir
                        client_socket.send("Bu joker hakkınız yok! Lütfen başka bir seçenek deneyin.\n".encode('utf-8'))
                        continue  # Geçerli bir joker kullanılması gerektiği için devam edilir

                # Eğer geçerli bir cevap (A, B, C, D) girilmişse
                if response in ['A', 'B', 'C', 'D']:
                    if response == answer:  # Cevap doğruysa
                        score += 1  # Skor artırılır
                        result_message = f"Doğru cevap! Toplam doğru sayın : {score}\n"
                        client_socket.send(result_message.encode('utf-8'))  # İstemciye doğru cevap mesajı gönderilir
                        break  # Sorudan sonra bir sonraki soruya geçilir
                    else:  # Cevap yanlışsa
                        exit_msg = get_exit_message(score)  # Hatalı cevap mesajı ve son skor alınır
                        result_message = f"Yanlış cevap! Doğru cevap: {answer}.\n{exit_msg}\nSon toplam doğru sayın: {score}\n"
                        client_socket.send(result_message.encode('utf-8'))
                        return  # Yanlış cevap alındıysa oyun sona erer

                else:
                    # Geçersiz giriş (A, B, C, D veya joker dışında bir şey girildi)
                    client_socket.send("Geçersiz giriş! Lütfen A, B, C, D veya kullanılabilir bir joker girin.\n".encode('utf-8'))
                    continue  # Geçersiz giriş olduğu için döngü devam eder

        # Tüm sorular doğru cevaplanmışsa, tebrik mesajı gönderilir
        end_message = "Tebrikler! Tüm soruları doğru cevapladınız ve oyunu kazandınız!\n"
        client_socket.send(end_message.encode('utf-8'))

    except Exception as e:
        print(f"İstemci işleme hatası: {e}")
    finally:
        print(f"Bağlantı kapatıldı: {client_address}")
        client_socket.close()  # Bağlantı sonlandırılır


if __name__ == "__main__":
    start_server()
