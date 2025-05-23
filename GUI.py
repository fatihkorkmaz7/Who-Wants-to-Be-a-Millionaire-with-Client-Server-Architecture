# ============================================
#  Kod dosyaları joker_server ==> program_server ==> GUI sırasıyla çalıştırılmalıdır.
#  GUI kod dosyasında, GUI kısmı yer almaktadır ve kullanıcı arayüzünü oluşturur.
#  Bu GUI, sunucuya bağlanarak soruları ve cevapları alır, doğru cevaplarla birlikte
#  kazanılan ödülleri günceller. Ayrıca, jokerler (seyirciye sor ve yarı yarıya) ile ilgili
#  işlemleri gerçekleştiren butonlar ve sesli geri bildirim mekanizmaları içerir.
#  GUI, tkinter kullanılarak tasarlanmıştır ve pygame ile sesli yanıtlar eklenmiştir.
#
#  İşlevsel özellikler:
#  1. Sunucuya bağlanarak sorular alınır ve GUI üzerinden kullanıcıya gösterilir.
#  2. Kullanıcı cevaplarını seçtikten sonra, bu cevaplar sunucuya gönderilir.
#  3. Jokerler aktif hale gelir ve kullanıcı joker kullanabilir.
#  4. Doğru cevaplar verildiğinde ödüller artar ve kazanılan para ekranda gösterilir.
#  5. Yanlış cevap durumunda sesli geri bildirim ve bilgi penceresi ile kullanıcı bilgilendirilir.
#  6. Oyun bitiminde veya bağlantı kesildiğinde oyun durumu güncellenir.
#
#  Bağlantı Detayları:
#  - Bu GUI, bir socket bağlantısı üzerinden "program_server" ile iletişim kurar.
#  - Sunucuya bağlanıldığında sorular alınır ve cevaplar sunucuya gönderilir.
#  - Sunucu, oyun mantığını yönetir ve oyuncunun cevaplarını değerlendirir.
#  - GUI, soruları ve doğru/yanlış cevapları kullanıcıya görsel olarak iletir.
#
#  Çalıştırma Talimatları:
#  1. **joker_server.py** dosyasını çalıştırarak joker özelliklerini sunan sunucuyu başlatın.
#  2. **program_server.py** dosyasını çalıştırarak ana oyun sunucusunu başlatın.
#  3. Son olarak bu dosyayı (GUI) çalıştırarak yarışma arayüzünü başlatın.
#  4. GUI arayüzünde "Yarışmayı Başlat" butonuna basarak sunucuya bağlanabilirsiniz.
#
# ============================================



import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import pygame


class QuizGameGUI:
    def __init__(self, root):
        self.rewards = [5000, 10000, 20000, 40000, 80000]
        self.correct_count = 0
        self.root = root
        self.root.title("Kim Milyoner Olmak İster - Yarışmacı")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a2e")

        # Pencereyi ekranın ortasına alma
        self.center_window()

        pygame.mixer.init()
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.correct_sound = pygame.mixer.Sound("correct1.mp3")
            self.wrong_sound = pygame.mixer.Sound("wrong1.mp3")
        except pygame.error as e:
            messagebox.showerror("Ses Dosyası Hatası", f"Ses dosyaları yüklenemedi: {e}")
            self.correct_sound = None
            self.wrong_sound = None

        self.client_socket = None
        self.connected = False
        self.money_score = 0

        self.create_widgets()

    def center_window(self):
        """Pencereyi ekranın ortasına yerleştirir"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2
        self.root.geometry(f"1200x800+{x}+{y}")

    def create_widgets(self):
        # Ana çerçeveler
        self.main_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sol panel (soru ve seçenekler)
        self.left_panel = tk.Frame(self.main_frame, bg="#16213e", bd=2, relief=tk.RAISED)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # Sağ panel (ödüller)
        self.right_panel = tk.Frame(self.main_frame, bg="#16213e", width=300, bd=2, relief=tk.RAISED)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Ödüller panosu
        self.create_prizes_board()

        # Bağlantı durumu
        self.status_frame = tk.Frame(self.left_panel, bg="#16213e")
        self.status_frame.pack(fill=tk.X, pady=(0, 20))

        self.status_label = tk.Label(
            self.status_frame,
            text="Yarışmayı Başlatın",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#16213e"
        )
        self.status_label.pack(side=tk.LEFT)

        self.connect_btn = tk.Button(
            self.status_frame,
            text="Yarışmayı Başlat",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            command=self.connect_to_server
        )
        self.connect_btn.pack(side=tk.RIGHT)

        # Soru çerçevesi
        self.question_frame = tk.LabelFrame(
            self.left_panel,
            text=" SORU ",
            font=("Arial", 14, "bold"),
            bg="#0f3460",
            fg="#e94560",
            relief=tk.RAISED,
            bd=3
        )
        self.question_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.question_label = tk.Label(
            self.question_frame,
            text="Yarışmayı Başlat butonuna basarak heyecan dolu yarışmaya hemen katılabilir ve büyük ödülün sahibi olma şansını yakalayabilirsiniz!",
            wraplength=700,
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#0f3460",
            justify="center",
            padx=20,
            pady=20
        )
        self.question_label.pack(fill=tk.BOTH, expand=True)

        # Seçenekler çerçevesi
        self.options_frame = tk.Frame(self.question_frame, bg="#0f3460")
        self.options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.option_labels = []

        for i in range(4):
            frame = tk.Frame(self.options_frame, bg="#0f3460")
            frame.pack(fill=tk.X, pady=5)

            # Seçenek harfi (A, B, C, D) tamamen kaldırıldı

            # Seçenek metni
            label = tk.Label(
                frame,
                text="",
                wraplength=600,
                font=("Arial", 14),
                fg="#ffffff",
                bg="#0f3460",
                justify="left",
                anchor="w"
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.option_labels.append(label)

        # Cevap butonları
        self.answers_frame = tk.Frame(self.left_panel, bg="#16213e")
        self.answers_frame.pack(fill=tk.X, pady=(0, 20))

        self.answer_buttons = []
        answers = ['A', 'B', 'C', 'D']
        button_colors = ["#e94560", "#00b4d8", "#f9c74f", "#90be6d"]

        for i, (ans, color) in enumerate(zip(answers, button_colors)):
            btn = tk.Button(
                self.answers_frame,
                text=f"{ans} Seçeneği",
                font=("Arial", 14, "bold"),
                width=15,
                height=2,
                bg=color,
                fg="#ffffff",
                activebackground=color,
                activeforeground="#ffffff",
                relief=tk.RAISED,
                bd=3,
                command=lambda x=ans: self.submit_answer(x)
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=5, sticky="nsew")
            self.answer_buttons.append(btn)

        # Butonların eşit genişlikte olması için
        self.answers_frame.grid_columnconfigure(0, weight=1)
        self.answers_frame.grid_columnconfigure(1, weight=1)

        # Jokerler ve kazanç
        self.bottom_frame = tk.Frame(self.left_panel, bg="#16213e")
        self.bottom_frame.pack(fill=tk.X)

        # Jokerler
        self.joker_frame = tk.LabelFrame(
            self.bottom_frame,
            text=" JOKER HAKKI ",
            font=("Arial", 12, "bold"),
            bg="#0f3460",
            fg="#e94560",
            relief=tk.RAISED,
            bd=2
        )
        self.joker_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.audience_joker = tk.Button(
            self.joker_frame,
            text="SEYİRCİYE SOR (S)",
            font=("Arial", 12, "bold"),
            bg="#9C27B0",
            fg="white",
            activebackground="#8e24aa",
            activeforeground="white",
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=3,
            command=lambda: self.use_joker('S')
        )
        self.audience_joker.pack(side=tk.LEFT, padx=10, pady=5)

        self.fifty_fifty_joker = tk.Button(
            self.joker_frame,
            text="YARI YARIYA (Y)",
            font=("Arial", 12, "bold"),
            bg="#FF9800",
            fg="white",
            activebackground="#fb8c00",
            activeforeground="white",
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=3,
            command=lambda: self.use_joker('Y')
        )
        self.fifty_fifty_joker.pack(side=tk.LEFT, padx=10, pady=5)

        # Kazanç
        self.score_frame = tk.Frame(self.bottom_frame, bg="#16213e")
        self.score_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.score_label = tk.Label(
            self.score_frame,
            text="₺0",
            font=("Arial", 24, "bold"),
            fg="#f9c74f",
            bg="#16213e"
        )
        self.score_label.pack(pady=10)

        tk.Label(
            self.score_frame,
            text="TOPLAM KAZANÇ",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#16213e"
        ).pack()
    def create_prizes_board(self):
        """Sağ tarafta ödüller panosunu oluşturur"""
        prizes = [
            "5. Soru - ₺80.000",
            "4. Soru - ₺40.000",
            "3. Soru - ₺20.000",
            "2. Soru - ₺10.000",
            "1. Soru - ₺5.000"
        ]

        # Ödüller başlığı
        tk.Label(
            self.right_panel,
            text="ÖDÜLLER",
            font=("Arial", 18, "bold"),
            fg="#f9c74f",
            bg="#16213e",
            pady=10
        ).pack(fill=tk.X)

        # Ödül seviyeleri
        self.prize_labels = []
        for i, prize in enumerate(prizes):
            # Son 5 ödül için farklı renk
            if i < 2:
                fg_color = "#e94560"  # Kırmızı
                font_size = 14
            elif i < 4:
                fg_color = "#00b4d8"  # Mavi
                font_size = 12
            else:
                fg_color = "#ffffff"  # Beyaz
                font_size = 11

            label = tk.Label(
                self.right_panel,
                text=prize,
                font=("Arial", font_size, "bold"),
                fg=fg_color,
                bg="#16213e",
                anchor="w",
                padx=20,
                pady=5
            )
            label.pack(fill=tk.X)
            self.prize_labels.append(label)

            # Mevcut seviyeyi vurgulamak için
            if i == 0:  # En yüksek ödül
                label.config(bg="#0f3460", relief=tk.SUNKEN, bd=1)

    def connect_to_server(self):
        # Puanı sıfırla
        self.correct_count = 0  # Doğru cevap sayacını sıfırla
        self.money_score = 0  # Kazanılan parayı sıfırla
        self.score_label.config(text="₺0")  # Skor etiketini sıfırla
        self.update_prize_highlight(-1)  # Ödül vurgusunu kaldır

        # Jokerleri aktif et
        self.audience_joker.config(state="normal")  # Seyirciye Sorma jokerini aktif et
        self.fifty_fifty_joker.config(state="normal")  # Yarı Yarıya jokerini aktif et

        try:
            # Socket oluşturuluyor ve sunucuya bağlanılıyor
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 4337))  # Sunucuya bağlan (IP: 127.0.0.1, Port: 4337)

            self.connected = True  # Bağlantı başarılıysa 'connected' durumu True olarak ayarlanır
            self.status_label.config(text="Yarışma Başlatıldı")  # Durum etiketi güncellenir
            self.connect_btn.config(state="disabled")  # Bağlantı butonunu devre dışı bırak

            # Sunucudan gelen mesajları almak için ayrı bir thread başlatılır
            threading.Thread(target=self.receive_messages, daemon=True).start()

        except Exception as e:
            # Bağlantı hatası durumunda hata mesajı gösterilir
            messagebox.showerror("Bağlantı Hatası", f"Sunucuya bağlanılamadı: {e}")

    def update_prize_highlight(self, question_index):
        """Mevcut soru seviyesine göre ödülü vurgular"""
        for i, label in enumerate(self.prize_labels):
            if i == (5 - question_index):  # 5 soruluk sistemde ters sırada
                label.config(bg="#0f3460", relief=tk.SUNKEN, bd=1)
            else:
                label.config(bg="#16213e", relief=tk.FLAT)

    def receive_messages(self):
        # Bağlantı aktif olduğu sürece sürekli mesaj al
        while self.connected:
            try:
                # Sunucudan gelen veriyi al (1024 byte)
                data = self.client_socket.recv(1024).decode('utf-8')

                # Eğer veri yoksa, bağlantı kesilmiş demektir, döngüden çıkılır
                if not data:
                    break

                # Gelen veriyi GUI thread'ine yönlendirir ve oyun durumunu günceller
                self.root.after(0, self.update_game_state, data)

            except Exception as e:
                # Hata durumunda hata mesajı yazdırılır
                print(f"Hata: {e}")
                break

        # Bağlantı kesildiyse 'connected' durumu False yapılır
        self.connected = False

        # Bağlantı kesildikten sonra GUI'de de bağlantı kesilme işlemi yapılır
        self.root.after(0, self.handle_disconnect)

    def handle_disconnect(self):
        self.status_label.config(text="Yarışma Tamamlandı")
        self.connect_btn.config(state="normal")
        self.question_label.config(text="Yarışmayı tekrardan başlatabilirsiniz")
        for label in self.option_labels:
            label.config(text="")

        # Puanı sıfırla
        self.money_score = 0
        self.score_label.config(text="₺0")
        self.update_prize_highlight(-1)

        # Jokerleri yeniden aktif et
        self.audience_joker.config(state="normal")
        self.fifty_fifty_joker.config(state="normal")

    def update_game_state(self, data):
        # Eğer gelen veri soru içeriyorsa
        if "Soru" in data:
            # Veriyi satırlara ayır
            lines = data.split('\n')
            question = ""  # Soru metnini tutmak için
            options = []  # Seçenekleri tutmak için
            question_index = 0  # Soru numarasını tutacak değişken

            # Satırlar üzerinden döngü başlat
            for line in lines:
                # "Soru" kelimesi geçen satırı yakala
                if "Soru" in line:
                    question = line
                    # Soru numarasını al (örneğin: "Soru 1:" -> 1)
                    try:
                        question_index = int(line.split()[1].replace(":", "")) - 1
                    except:
                        question_index = 0
                # Seçenek satırlarını al
                elif any(opt in line for opt in ["A)", "B)", "C)", "D)"]):
                    options.append(line)

            # GUI'deki soru etiketini güncelle
            self.question_label.config(text=question)
            # Seçenek etiketlerini güncelle
            for i, option in enumerate(options):
                if i < len(self.option_labels):
                    self.option_labels[i].config(text=option)

            # Mevcut soru seviyesini vurgula
            self.update_prize_highlight(question_index)

        # Eğer gelen veri joker sonucu içeriyorsa
        elif "Joker sonucu" in data:
            # Joker sonucu mesajını bir bilgi kutusunda göster
            messagebox.showinfo("Joker", data)

        # Eğer gelen veri doğru cevapla ilgiliyse
        elif data.startswith("Doğru cevap"):
            # Doğru cevap verildiğinde ses durdurulur ve doğru ses çalınır
            pygame.mixer.stop()
            self.correct_sound.play()
            self.correct_count += 1  # Doğru cevap sayısını artır
            self.update_money()  # Kazanılan parayı güncelle

        # Eğer gelen veri yanlış cevapla ilgiliyse
        elif data.startswith("Yanlış cevap"):
            # Yanlış cevap verildiğinde ses durdurulur ve yanlış ses çalınır
            pygame.mixer.stop()
            self.wrong_sound.play()

            # Kazanılan para miktarını belirle
            if self.correct_count > 0:
                reward = self.rewards[self.correct_count - 1]  # Ödül miktarını al
                data += f"\nKazandığınız ödül: ₺{reward:,}"
            else:
                data += "\nMaalesef ödül kazanamadınız."

            # Yanlış cevap sesinin süresi kadar bekle
            ses_suresi_ms = int(self.wrong_sound.get_length() * 1000)
            # Ses tamamlandıktan sonra yanlış cevap mesajını göster
            self.root.after(ses_suresi_ms, lambda: messagebox.showinfo("Yanlış!", data))

        # Eğer gelen veri oyunun sonunda tebrik mesajı ise
        elif "Tebrikler" in data:
            # Oyunun bittiğini ve kazanılan parayı göster
            final_message = f"{data}\n\nToplam Kazancınız: 80.000 ₺"
            messagebox.showinfo("Oyun Bitti", final_message)
            # Sunucuya bağlantıyı kapat
            self.client_socket.close()
            self.connected = False

    def update_money(self):
        # Her doğru cevapta 2 katına çıkar, başlangıç 5000 TL
        if self.money_score == 0:
            self.money_score = 5000
        else:
            self.money_score *= 2
        self.score_label.config(text=f"₺{self.money_score:,}")

    def submit_answer(self, answer):
        # Eğer bağlantı hala aktifse
        if self.connected:
            try:
                # Cevap veriyi UTF-8 formatında sunucuya gönder
                self.client_socket.send(answer.encode('utf-8'))
            except:
                # Cevap gönderilemezse hata mesajı göster
                messagebox.showerror("Hata", "Cevap gönderilemedi")


    def use_joker(self, joker_type):
        # Eğer bağlantı hala aktifse
        if self.connected:
            try:
                # Joker türünü (Seyirciye Sorma veya Yarı Yarıya) sunucuya gönder
                self.client_socket.send(joker_type.encode('utf-8'))

                # Seyirciye Sorma jokeri kullanıldıysa, ilgili butonu devre dışı bırak
                if joker_type == 'S':
                    self.audience_joker.config(state="disabled")
                # Yarı Yarıya jokeri kullanıldıysa, ilgili butonu devre dışı bırak
                elif joker_type == 'Y':
                    self.fifty_fifty_joker.config(state="disabled")
            except:
                # Joker gönderilemezse hata mesajı göster
                messagebox.showerror("Hata", "Joker kullanılamadı")



if __name__ == "__main__":
    root = tk.Tk()
    app = QuizGameGUI(root)
    root.mainloop()