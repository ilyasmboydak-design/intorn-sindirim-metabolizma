import streamlit as st
import re

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
    page_icon="🐄",
    layout="wide",
)

# Styling
st.markdown("""
    <style>
    .main-title {
        color: #1F4E79;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #595959;
        font-family: 'Arial', sans-serif;
        font-style: italic;
        text-align: center;
        font-size: 15px;
        margin-bottom: 20px;
    }
    .vaka-header {
        background: linear-gradient(90deg, #1F4E79 0%, #2F5597 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .card-found {
        background-color: #F2F4F8;
        border-left: 6px solid #1F4E79;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    .card-title {
        font-weight: bold;
        color: #1F4E79;
        font-size: 15px;
        margin-bottom: 4px;
    }
    .card-content {
        font-size: 15px;
        color: #262626;
        line-height: 1.5;
    }
    .badge-category {
        background-color: #D9E1F2;
        color: #1F4E79;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Cases Knowledge Base
CASES = {
    "Vaka 1 (Sığır 'Yıldız' - BRD Kompleksi / Mannheimia Bronkopnömonisi)": {
        "kod": "VAKA_1_BRD",
        "sikayet": "Yüksek ateş, kranio-ventral akciğer alanlarında solunum seslerinin kaybolması, öksürük ve burun akıntısı.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "kapalı", "ortam", "toz"],
                "content": "Kapalı ve yüksek kapasiteli besi padoğunda barındırılmaktadır. Fan havalandırması yetersiz, ortamda basık yoğun amonyak kokusu ve yüksek toz birikimi mevcuttur. Altlıklar saman olup kısmen nemli ve kirlidir."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mısır", "arpa", "saman", "silaj", "kesif"],
                "content": "Günlük rasyon: 12 kg mısır silajı, 2.5 kg buğday samanı, 7 kg besi büyütme yemi. Yem tüketimi son 2 günde %60 oranında düşmüştür."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "4 gün önce başka bir bölgeden 8 saatlik kamyon nakli ile tesise getirilmiştir. Nakil stresi öyküsü mevcuttur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "aşı", "öykü"],
                "content": "Nakil öncesi viral/bakteriyel solunum aşıları yapılmamıştır. Geçmişinde kronik hastalık kaydı yoktur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "solunum", "mukoza", "crt", "dolum", "dehidrasyon", "burun"],
                "content": "Vücut Sıcaklığı: 40.8 °C | Kalp Frekansı: 108 atım/dk | Solunum Frekansı: 58 nefes/dk | Mukozalar: Hiperemik (Kızarık) | CRT: 2.5 saniye | Dehidrasyon: %6 | Mukopürülan mukuslu burun akıntısı."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer", "rall", "sessiz", "hışırtı", "sürtünme"],
                "content": "Akciğer Oskültasyonu: Bilateral kranio-ventral akciğer loblarında solunum sesleri tamamen sessiz (hepatizasyon/konsolidasyon), kaudo-dorsal alanlarda kaba raller ve plevral sürtünme sesleri duyulmaktadır."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı & İnterkostal Hassasiyet Testleri",
                "keywords": ["ağrı", "sopa", "kama", "withers", "göğüs"],
                "content": "Göğüs duvarı (interkostal aralıklar) palpasyonunda belirgin ağrı reaksiyonu pozitif. Retikulum ağrı testleri (Sopa/Kama) negatif."
            },
            "PING_LIPTAK": {
                "name": "Ping & Abdominosentez Testleri",
                "keywords": ["ping", "liptak", "abomasum"],
                "content": "Sağ ve sol karın duvarında akustik ping sesi YOKTUR. Liptak testi yapılmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen sıvısı", "rumen ph", "protozoa"],
                "content": "Rumen pH: 6.6 | Renk: Yeşilimsi-kahve | Koku: Normal aromatik | Protozoa hareketi aktif."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & BAL Kültürü",
                "keywords": ["kültür", "bal", "bakteri", "gram", "lavaj"],
                "content": "Bronkoalveoler Lavaj (BAL) Kültürü: Gram-negatif, bipolar boyanan Mannheimia haemolytica üremesi pozitif. PCR'da BVDV ve BRSV suşları saptandı."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["ferroskop", "glutaraldehit", "pıhtılaşma"],
                "content": "Ferroskop metal dedektörü: Negatif (Metal sinyali yok). Glutaraldehit Pıhtılaşma Testi: 2.5 Dakika (Ağır Akut Pozitif - Yoğun Fibrinöz Yangı)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "rbc", "pcv", "fibrinojen", "pp/f", "nötrofil"],
                "content": "WBC: 28.5 x10³/µL | Segmenteli Nötrofil: %68 | Çomak (Band) Nötrofil: %12 | Lenfosit: %14 | Monosit: %5 | Eozinofil: %1 | RBC: 6.8 x10⁶/µL | Hb: 11.2 g/dL | PCV: %34 | PLT: 320 x10³/µL | Plazma Fibrinojeni: 1350 mg/dL | PP/F Oranı: 5.8"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "bun", "kreatinin", "albümin", "globülin"],
                "content": "AST: 82 U/L | GGT: 22 U/L | ALT: 18 U/L | ALP: 64 U/L | CK: 120 U/L | LDH: 480 U/L | BUN: 18 mg/dL | Kreatinin: 1.0 mg/dL | Total Protein: 7.8 g/dL | Albümin: 2.7 g/dL | Globülin: 5.1 g/dL | BHBA: 0.4 mmol/L | NEFA: 0.2 mmol/L"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.26 | pO₂: 52 mmHg | pCO₂: 56 mmHg | HCO₃⁻: 24.5 mmol/L | Baz Açığı (BE): -2.5 mmol/L | L-Laktat: 3.2 mmol/L | Na⁺: 138 mEq/L | K⁺: 4.8 mEq/L | Cl⁻: 98 mEq/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Torakal Ultrasonografi",
                "keywords": ["ultrason", "usg", "toraks", "akciğer", "plevra"],
                "content": "Torakal Ultrasonografi: Kranio-ventral akciğer loblarında hiperekojen hepatizasyon (konsolidasyon) alanları, plevral yüzeyde fibrin bantları ve 2 cm plevral sıvı birikimi (Plevritis)."
            }
        }
    },
    "Vaka 2 (Sığır 'Güneş' - Babesiosis / İntravasküler Hemoliz Krizi)": {
        "kod": "VAKA_2_BABESIA",
        "sikayet": "Yüksek ateş, kiremit kırmızısı/koyu çay rengi idrar (hemoglobinüri), sarılık ve mukozalarda solgunluk.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "mera", "kena", "çalı", "otlatma", "altlık"],
                "content": "Yarı açık serbest sistemli işletme. Hayvan gündüzleri çalılık mera otlağına çıkarılmaktadır. Barınak çevresinde meralık mera keneleri (Rhipicephalus / Boophilus spp.) yoğun mevcuttur."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "mera", "otlatma"],
                "content": "Mera otlaması + 4 kg yoğun süt yemi. İştah tamamen durmuş, yem tüketimi sıfırlanmıştır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "coğrafya", "sevk"],
                "content": "Endemik kene bölgesindeki mera alanında barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "kene", "parazit"],
                "content": "Kene mücadelesi ve ektoparazit ilaçlaması aksatılmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "idrar", "hemoglobinüri", "ikter", "sarılık"],
                "content": "Vücut Sıcaklığı: 41.2 °C | Kalp Frekansı: 116 atım/dk | Solunum Frekansı: 48 nefes/dk | Mukozalar: Belirgin İkterik (Sarı) ve İktero-anemik | CRT: 3.5 saniye | İdrar: Koyu kiremit kırmızısı / çay rengi (Hemoglobinüri)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "üfürüm"],
                "content": "Kalp Oskültasyonu: Şiddetli taşikardi, anemiye bağlı anhemik üfürüm sesi. Akciğer sesleri hafif kaba veziküler."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı Testleri",
                "keywords": ["ağrı", "sopa", "kama"],
                "content": "Retikulum ağrı testleri negatif."
            },
            "PING_LIPTAK": {
                "name": "Ping & Abdominosentez",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi yok. Liptak testi yapılmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen pH: 6.8 | İçerik normal aromatik."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Periferik Kan Yayması (Giemsa)",
                "keywords": ["kültür", "giemsa", "kan yayması", "babesia", "parazit", "eritrosit"],
                "content": "Kulak Veninden Alınan Kan Yayması (Giemsa Boyama): Eritrositler içinde armut biçiminde ikili Babesia bovis / B. bigemina merozoitleri saptandı (Parasitemia %8)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Ferroskop: Negatif. Glutaraldehit Testi: 12.0 Dakika (Negatif / Yangısız Hemolitik Süreç)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "hb", "mcv", "rdw", "fibrinojen"],
                "content": "RBC: 2.4 x10⁶/µL | Hb: 4.8 g/dL | PCV: %14 | MCV: 58 fL | RDW: %22.5 | WBC: 14.2 x10³/µL | Nötrofil: %58 | Lenfosit: %36 | PLT: 95 x10³/µL | Plazma Fibrinojeni: 380 mg/dL | PP/F: 18.4"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "bilirubin", "ast", "ggt", "bun", "kreatinin", "serbest hb"],
                "content": "Total Bilirubin: 6.8 mg/dL | İndirekt Bilirubin: 5.4 mg/dL | Direkt Bilirubin: 1.4 mg/dL | AST: 185 U/L | GGT: 32 U/L | BUN: 48 mg/dL | Kreatinin: 2.2 mg/dL | Serbest Plazma Hemoglobini: 420 mg/dL | Total Protein: 6.2 g/dL | Albümin: 2.8 g/dL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.28 | pO₂: 58 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 17.2 mmol/L | Baz Açığı (BE): -7.5 mmol/L | L-Laktat: 4.8 mmol/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Abdominal USG",
                "keywords": ["ultrason", "usg", "dalak", "karaciğer"],
                "content": "Abdominal Ultrasonografi: Dalak boyutlarında ılımlı büyüme (Splenomegali), böbrek korteksinde hemoglobiniğe bağlı ekojenite artışı."
            }
        }
    },
    "Vaka 3 (Sığır 'Benli' - Anaplasmosis / Ekstravasküler Hemoliz Krizi)": {
        "kod": "VAKA_3_ANAPLASMA",
        "sikayet": "Yüksek ateş, ağır sarılık, hızlı zayıflama, berrak açık renkli idrar (Hemoglobinüri Yoktur!).",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "sinek", "mera", "altlık"],
                "content": "Mera dönüşü kapalı ahırda barındırılmaktadır. Taban ıslak, ortamda yoğun at sinekleri (Tabanidae) ve keneler gözlenmektedir."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "mera"],
                "content": "Mera otlaması + kuru ot. İştah azalmıştır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "coğrafya"],
                "content": "Mera otlatma bölgesinde yetişmiştir."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "kene", "enjeksiyon"],
                "content": "Sürüde ortak enjektör kullanımı ve kene stresi kaydı vardır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "idrar", "ikter", "sarılık"],
                "content": "Vücut Sıcaklığı: 40.5 °C | Kalp Frekansı: 110 atım/dk | Solunum Frekansı: 44 nefes/dk | Mukozalar: Şiddetli İkterik (Parlak Sarı/Limon Sarısı) | CRT: 3.2 saniye | İdrar: Berrak açık sarı (Hemoglobinüri veya renk bozukluğu KESİNLİKLE YOKTUR)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp Oskültasyonu: Taşikardik ve anhemik üfürüm. Akciğer sesleri hafif sert veziküler."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı Testleri",
                "keywords": ["ağrı"],
                "content": "Ağrı testleri negatif."
            },
            "PING_LIPTAK": {
                "name": "Ping & Abdominosentez",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi negatif."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen pH: 6.7 | Normal aromatik."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Periferik Kan Yayması (Giemsa)",
                "keywords": ["kültür", "giemsa", "kan yayması", "anaplasma", "eritrosit", "inklüzyon"],
                "content": "Periferik Kan Yayması (Giemsa Boyama): Eritrosit marjinlerinde (çeperinde) koyu mor Anaplasma marginale inklüzyon cisimcikleri saptandı (Parasitemia %12). Babesia merozoiti görülmedi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Ferroskop: Negatif. Glutaraldehit Pıhtılaşma Testi: 14.0 Dakika (Negatif)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "hb", "mcv", "rdw", "fibrinojen"],
                "content": "RBC: 2.1 x10⁶/µL | Hb: 4.2 g/dL | PCV: %13 | MCV: 62 fL | RDW: %24.0 | WBC: 12.8 x10³/µL | Nötrofil: %54 | Lenfosit: %40 | PLT: 110 x10³/µL | Plazma Fibrinojeni: 350 mg/dL | PP/F: 19.1"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "bilirubin", "ast", "ggt", "bun", "kreatinin", "serbest hb"],
                "content": "Total Bilirubin: 8.4 mg/dL | İndirekt Bilirubin: 7.2 mg/dL | Direkt Bilirubin: 1.2 mg/dL | AST: 165 U/L | GGT: 28 U/L | BUN: 24 mg/dL | Kreatinin: 1.1 mg/dL | Serbest Plazma Hemoglobini: 15 mg/dL (NORMAL - İntravasküler hemoliz yok!)"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.32 | pO₂: 62 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 20.5 mmol/L | Baz Açığı (BE): -4.0 mmol/L | L-Laktat: 2.9 mmol/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Abdominal USG",
                "keywords": ["ultrason", "usg", "dalak", "karaciğer"],
                "content": "Abdominal Ultrasonografi: Masif Splenomegali (Dalak parankiminde aşırı büyüme ve parankim kalınlaşması - Ekstravasküler fagositoz kanıtı)."
            }
        }
    },
    "Vaka 4 (Sığır 'Karakız' - Tip I Ketozis / Primer Pik Süt Glukoz Açlığı)": {
        "kod": "VAKA_4_KETOZIS_1",
        "sikayet": "Doğum sonrası 4. haftada aniden iştahsızlık, kesif yemi reddedip sadece kuru ot yeme, nefeste tatlımımsı aseton kokusu ve süt veriminde keskin düşüş.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "altlık", "temiz"],
                "content": "Yarı açık serbest duraklı modern süt tesisi. Temizlik ve havalandırma iyi."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "kesif", "mısır", "süt", "glukoz", "nişasta"],
                "content": "Pik süt dönemindeki (doğum sonrası 28. gün) yüksek verimli ineğe 14 kg mısır silajı, 2 kg yonca, 10 kg yüksek proteinli süt yemi verilmektedir. Hayvan son 2 gündür kesif yemi tamamen reddetmekte, sadece az miktarda kuru ot yemektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "coğrafya"],
                "content": "Sabit süt tesisinde barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "doğum", "laktasyon"],
                "content": "4 hafta önce sorunsuz doğum yapmıştır. Pik süt verimine ulaşmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "aseton", "koku", "crt"],
                "content": "Vücut Sıcaklığı: 38.4 °C | Kalp Frekansı: 74 atım/dk | Solunum Frekansı: 22 nefes/dk | Mukozalar: Pembe | Nefes ve Süt: Belirgin tatlımsı Aseton / Keton kokusu pozitif | Rumen hareketleri: 1/2 dk (Zayıf)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer sesleri fizyolojik sınırlarda."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı Testleri",
                "keywords": ["ağrı"],
                "content": "Ağrı testleri negatif."
            },
            "PING_LIPTAK": {
                "name": "Ping & Liptak Testleri",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi yok. Liptak testi negatif."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen pH: 6.9 | İnfüzorya hareketi hafif yavaşlamış."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & İdrar Keton Testi (Rothera)",
                "keywords": ["kültür", "rothera", "keton", "idrar", "süt"],
                "content": "İdrar ve Süt Rothera Testi: Koyu mor renk değişimi (Aşırı Pozitif +++ Ketonüri ve Ketolaktiya)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Ferroskop: Negatif. Glutaraldehit Pıhtılaşma Testi: 15.0 Dakika (Negatif)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "fibrinojen"],
                "content": "WBC: 7.4 x10³/µL | RBC: 6.2 x10⁶/µL | PCV: %32 | Plazma Fibrinojeni: 340 mg/dL | PP/F: 21.1 (Tüm hemogram değerleri fizyolojik sınırlardadır)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "glikoz", "bhba", "nefa", "ast", "ggt", "bun", "kreatinin"],
                "content": "Serum Glikoz: 24 mg/dL (Şiddetli Hipoglisemi) | BHBA: 3.8 mmol/L (Aşırı Yüksek Keton Cisimciği) | NEFA: 0.6 mmol/L | AST: 92 U/L | GGT: 24 U/L | Total Bilirubin: 0.6 mg/dL | BUN: 14 mg/dL | Kreatinin: 0.9 mg/dL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be"],
                "content": "Kan pH: 7.34 | pO₂: 75 mmHg | pCO₂: 44 mmHg | HCO₃⁻: 21.2 mmol/L | Baz Açığı (BE): -3.2 mmol/L | L-Laktat: 1.2 mmol/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Karaciğer USG",
                "keywords": ["ultrason", "usg", "karaciğer"],
                "content": "Abdominal Ultrasonografi: Karaciğer boyutu ve ekojenitesi normal (Steatoz/yağlanma bulgusu yoktur)."
            }
        }
    },
    "Vaka 5 (Sığır 'Fırtına' - Tip II Ketozis / Yağlı Karaciğer Sendromu)": {
        "kod": "VAKA_5_KETOZIS_2",
        "sikayet": "Doğum yaptıktan hemen sonraki ilk 5 günde kalkamama, ağır depresyon, tedaviye yanıtsız ketozis ve karaciğer yetmezliği bulguları.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "kuruda", "besleme"],
                "content": "Kuru dönem padoğu karmaşası. Kuru dönemde aşırı enerjili besleme yapılmıştır."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "obez", "kuru dönem", "bcs", "kondisyon"],
                "content": "Kuru dönemde (gebeliğin son 2 ayı) mısır silajı ve yoğun yem kısıtlanmamış, inek BCS: 4.5/5.0 (Aşırı Obez) olarak doğuma girmiştir. Doğum sonrası iştah tamamen kapanmıştır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Sabit süt tesisi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "doğum", "güç doğum", "obezite"],
                "content": "3 gün önce güç doğum yapmış, plasenta retensiyonu şekillenmiştir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "depresyon", "stoper"],
                "content": "Vücut Sıcaklığı: 37.8 °C | Kalp Frekansı: 92 atım/dk | Solunum Frekansı: 28 nefes/dk | Mukozalar: Hafif İkterik ve Kirli Sarı | CRT: 3.0 saniye | Derin Stupor/Depresyon, ayağa kalkmakta isteksizlik."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp sesleri boğuk ve zayıf."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı Testleri",
                "keywords": ["ağrı"],
                "content": "Ağrı testleri negatif."
            },
            "PING_LIPTAK": {
                "name": "Ping & Liptak Testleri",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi negatif."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen pH: 6.5 | Rumen haraketleri 0/2 dk (Atonik)."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & İdrar Keton",
                "keywords": ["kültür", "keton", "rothera"],
                "content": "İdrar Rothera Testi: Pozitif (++)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Ferroskop: Negatif. Glutaraldehit Testi: 10.0 Dakika."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "fibrinojen"],
                "content": "WBC: 11.4 x10³/µL | RBC: 5.8 x10⁶/µL | PCV: %30 | Plazma Fibrinojeni: 420 mg/dL"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "nefa", "bhba", "ast", "ggt", "gldh", "glikoz", "karaciğer", "albümin"],
                "content": "NEFA: 1.8 mmol/L (Masif Yağ Asidi Mobilizasyonu) | BHBA: 2.6 mmol/L | Serum Glikoz: 32 mg/dL | AST: 240 U/L | GGT: 85 U/L | GLDH: 68 U/L | Total Bilirubin: 2.8 mg/dL | Albümin: 2.2 g/dL (Karaciğer sentez yetersizliği)"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be"],
                "content": "Kan pH: 7.30 | pO₂: 70 mmHg | pCO₂: 46 mmHg | HCO₃⁻: 19.8 mmol/L | Baz Açığı (BE): -4.8 mmol/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Karaciğer USG ve Biyopsi",
                "keywords": ["ultrason", "usg", "karaciğer", "steatoz", "biyopsi"],
                "content": "Karaciğer Ultrasonografisi: Parankimde yaygın parlak hiperekojenite (Ağır Hepatik Steatoz / Yağlanma). Karaciğer Biyopsisi: Karaciğer doku lipid oranı > %34 (Ağır Yağlı Karaciğer)."
            }
        }
    },
    "Vaka 6 (Sığır 'Ceylan' - Corynebacterium renale Akut Pyelonefrit)": {
        "kod": "VAKA_6_PYELONEFRIT",
        "sikayet": "İdrar yaparken ağrı ve ıkınma (strangüri), kanlı/pürülan pıhtılı idrar (hematüri/piyüri), kambur duruş ve bel bölgesine dokunulunca inleme.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "altlık", "gübre", "hijyen"],
                "content": "Kapalı bağlı duraklı sistem. Yataklık samanları ıslak ve yoğun dışkı/gübre ile bulaşıktır. Perine ve vulva bölgesi gübre ile kirlenmiştir."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem"],
                "content": "Standart süt sığırı rasyonu. Su tüketimi ve yem alımı 3 gündür düşmüştür."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Sabit işletme."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "doğum", "dystocia", "metritis"],
                "content": "6 hafta önce zor doğum yapmış, sonrasında vajinitis ve metritis geçirmiştir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "idrar", "kanlı", "pürülan", "strangüri", "ikınma"],
                "content": "Vücut Sıcaklığı: 39.7 °C | Kalp Frekansı: 98 atım/dk | Solunum Frekansı: 34 nefes/dk | Mukozalar: Soluk pembe | CRT: 2.2 saniye | İdrar Muayenesi: İdrar yaparken kesik kesik ıkınma, idrar sonunda kan pıhtıları ve irinli doku parçaları gelmesi."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer sesleri fizyolojik."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı & Rektal Böbrek Muayenesi",
                "keywords": ["ağrı", "böbrek", "rektal", "inleme", "böbrek muayenesi"],
                "content": "Bel bölgesine (lumbal alana) derin bastırmada şiddetli inleme ve sırtı kamburlaştırma pozitif. Rektal Muayene: Sol böbrek lobları aşırı büyümüş, ağrılı, üreter kanalı başparmak kalınlığında sertleşmiş."
            },
            "PING_LIPTAK": {
                "name": "Ping & Liptak Testleri",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi negatif."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen pH: 6.8."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & İdrar Sedimantasyonu ve Kültür",
                "keywords": ["kültür", "idrar", "sedimantasyon", "bakteri", "gram", "corynebacterium", "piyüri"],
                "content": "İdrar Sedimantasyonu Gram Boyama: Bol miktarda lökosit (piyüri), eritrosit ve Gram-pozitif palisat oluşturan Corynebacterium renale basilleri saptandı. İdrar pH: 8.5 (Alkali - Üreaz aktivitesi)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Ferroskop: Negatif. Glutaraldehit Pıhtılaşma Testi: 4.0 Dakika (Belirgin Yangısal Pozitif)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "fibrinojen", "pp/f"],
                "content": "WBC: 22.8 x10³/µL | Segmenteli Nötrofil: %72 | Çomak Nötrofil: %8 | Lenfosit: %16 | RBC: 5.2 x10⁶/µL | PCV: %26 | Plazma Fibrinojeni: 920 mg/dL | PP/F: 7.8"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "bun", "kreatinin", "azotemi", "ast", "ggt", "albümin", "globülin"],
                "content": "BUN: 86 mg/dL (Ağır Renal Azotemi) | Serum Kreatinin: 4.8 mg/dL | Total Protein: 8.6 g/dL | Albümin: 2.6 g/dL | Globülin: 6.0 g/dL | AST: 74 U/L | GGT: 22 U/L | Ca²⁺: 8.2 mg/dL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be"],
                "content": "Kan pH: 7.28 | pO₂: 72 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 18.2 mmol/L | Baz Açığı (BE): -6.4 mmol/L | K⁺: 5.8 mEq/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Renal Ultrasonografi",
                "keywords": ["ultrason", "usg", "böbrek", "üreter", "pelvis"],
                "content": "Renal Ultrasonografi: Böbrek pelvisinde hiperekojen pürülan irin birikimi, böbrek lobülasyonlarında sınır kaybı ve üreter lümeninde 1.8 cm genişleme."
            }
        }
    },
    "Vaka 7 (Sığır 'Nisa' - Akut Rumen Asidozu / SARA & Karaciğer Apsesi / VCCT)": {
        "kod": "VAKA_7_ASIDOZ",
        "sikayet": "Doğum sonrası süt verimini artırmak için aniden kesif yem artırılması, iştahsızlık, ekşi sulu ishal, sonrasında burun/ağızdan kan gelmesi (hemoptizi) ve melena.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "kapalı"],
                "content": "Kapalı beton zeminli bağlı ahır. Yetersiz havalandırma, basık amonyak kokusu. Ekşi sulu ishale bağlı kirli ve ıslak saman altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mısır", "arpa", "saman", "silaj", "kesif", "kg"],
                "content": "Doğum sonrası süt verimindeki hızlı artış üzerine rasyondaki yoğun yem (arpa/mısır kırması) miktarı aniden artırılmıştır. Günlük verilen yem miktarları: 14 kg mısır silajı, 3 kg buğday samanı ve 12 kg yoğun süt yemi (arpa/mısır kırması)."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "coğrafya"],
                "content": "Sabit süt tesisinde barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "doğum", "asidoz", "rumenitis"],
                "content": "2 ay önce doğum yapmış, ardından tekrarlayan subakut rumen asidozu (SARA) atakları geçirmiştir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "dehidrasyon", "dışkı", "ishal", "hemoptizi", "melena"],
                "content": "Vücut Sıcaklığı: 39.4 °C | Kalp Frekansı: 112 atım/dk | Solunum Frekansı: 48 nefes/dk | Mukozalar: Soluk pembe | CRT: 3.0 saniye | Dehidrasyon: %8 | Dışkı: Sulu, gazlı, ekşi kokulu, yer yer katran siyahı (Melena) | Burun/Ağız: Köpüklü taze kan fışkırması (Hemoptizi)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer & Rumen Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "rumen", "çınlama", "akciğer", "ping"],
                "content": "Kalp Oskültasyonu: Taşikardik, üfürüm veya çalkantı sesi yok. Akciğer Oskültasyonu: Sert veziküler solunum sesleri. Rumen Oskültasyonu: Rumen hareketleri 0/2 dk (Atonik). Sol dorsal rumende gaz birikimine bağlı hafif çınlama sesi var ancak abomasal ping yok."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı Testleri",
                "keywords": ["ağrı", "sopa", "kama", "withers"],
                "content": "Retikulum ağrı testleri (Sopa/Kama) negatif."
            },
            "PING_LIPTAK": {
                "name": "Ping & Liptak Testleri",
                "keywords": ["ping", "liptak", "abomasosentez"],
                "content": "Sol 8-12. ICS hat boyunca metallic abomasal ping sesi YOKTUR. Liptak Testi (Abomasosentez): Sol alt karın duvarından sıvı ponksiyonunda abomasal sıvı çekilemedi (pH > 6.0, yeşilimsi rumen sıvısı girmekte)."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen sıvısı", "rumen ph", "protozoa", "sütümsü", "ekşi"],
                "content": "Rumen Sıvısı Analizi: pH: 4.6 | Renk: Sütümsü-sarımsı | Koku: Ekşi laktik asit kokusu | Kıvam: Sulu, mikro-viskoz | Canlı Protozoa Sayısı: 0 / HPF (Mikroskobide protozoon saptanmadı)."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Gram Boyama",
                "keywords": ["kültür", "gram", "lactobacillus", "streptococcus", "bakteri"],
                "content": "Rumen Sıvısı Gram Boyama: Gram-pozitif rod ve koklar (Lactobacillus spp., Streptococcus bovis) hakim. Gram-negatif flora kaybolmuş. Dışkı kültüründe patojen Salmonella üremedi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Ferroskop: Negatif. Glutaraldehit Pıhtılaşma Testi: 3.5 Dakika (Belirgin Yangısal Pozitif - Karaciğer Apsesi / VCCT)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "hb", "fibrinojen", "pp/f"],
                "content": "WBC: 18.6 x10³/µL | Segmenteli Nötrofil: %65 | Çomak Nötrofil: %10 | Lenfosit: %20 | RBC: 4.8 x10⁶/µL | Hb: 8.2 g/dL | PCV: %24 | PLT: 180 x10³/µL | Plazma Fibrinojeni: 950 mg/dL | PP/F Oranı: 6.8"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "bun", "kreatinin", "albümin", "globülin"],
                "content": "AST: 168 U/L | GGT: 58 U/L | ALT: 28 U/L | ALP: 95 U/L | CK: 110 U/L | LDH: 420 U/L | BUN: 32 mg/dL | Kreatinin: 1.4 mg/dL | Total Protein: 7.2 g/dL | Albümin: 2.4 g/dL | Globülin: 4.8 g/dL | D-Laktat: 4.2 mmol/L | L-Laktat: 3.8 mmol/L"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat", "klor", "potasyum"],
                "content": "Kan pH: 7.18 | pO₂: 68 mmHg | pCO₂: 38 mmHg | HCO₃⁻: 11.5 mmol/L | Baz Açığı (BE): -12.5 mmol/L | Laktat: 8.0 mmol/L | Na⁺: 132 mEq/L | K⁺: 5.2 mEq/L | Cl⁻: 96 mEq/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Abdominal USG",
                "keywords": ["ultrason", "usg", "karaciğer", "apse", "vena cava"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 5 cm ve 3 cm çapında multifokal kılıflı apse odakları, Vena Cava Caudalis lümeninde trombüs ekojenitesi."
            }
        }
    },
    "Vaka 8 (Sığır 'Maviş' - Sola Abomasum Deplasmanı / LDA)": {
        "kod": "VAKA_8_LDA",
        "sikayet": "Doğum sonrası iştahsızlık, süt veriminde yarı yarıya düşüş, sol karın duvarında çınlayan metallik akustik ses (ping).",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "altlık", "temiz"],
                "content": "Yarı açık serbest duraklı (free-stall) kauçuk yataklı modern ahır. Havadar, kokusuz. Temiz ve kuru duraklar."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "doğum", "silaj"],
                "content": "Doğum sonrası yüksek enerjili TMR rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Sabit işletme."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "doğum", "hipokalsemi", "metritis"],
                "content": "2 hafta önce doğum yapmış, hafif hipokalsemi (doğum felci) ve metritis tedavisi görmüştür."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "dışkı"],
                "content": "Vücut Sıcaklığı: 38.6 °C | Kalp Frekansı: 78 atım/dk | Solunum Frekansı: 24 nefes/dk | Mukozalar: Pembe | CRT: 2.0 saniye | Dışkı: Az miktarda, cıvık ve zeytin yeşili."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer sesleri fizyolojik."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı Testleri",
                "keywords": ["ağrı"],
                "content": "Ağrı testleri negatif."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak (Abomasosentez) Testi",
                "keywords": ["ping", "liptak", "abomasum", "çınlama", "ph"],
                "content": "Perküsyon-Oskültasyon: Sol 8-12. Interkostal aralık ve paralumbar fossa hattında net yüksek frekanslı metallic ping (steel band sound) sesi. Liptak Testi (Abomasosentez): Sol karın duvarından ping alanından girilerek çekilen sıvı pH: 2.5 (Kesin Doğrulanmış Abomasum Sıvısı)."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen pH: 6.8 | Rumen motilitesi 1/2 dk."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Kültür",
                "keywords": ["kültür"],
                "content": "Patojen üremesi yok."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Ferroskop: Negatif. Glutaraldehit Pıhtılaşma Testi: 16.0 Dakika (Negatif / Yangısız Mekanik Deplasman)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "fibrinojen"],
                "content": "WBC: 6.8 x10³/µL | RBC: 6.1 x10⁶/µL | PCV: %31 | Plazma Fibrinojeni: 320 mg/dL | PP/F: 22.5"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "bun", "kreatinin", "klor", "potasyum", "albümin"],
                "content": "Serum Klor (Cl⁻): 82 mEq/L (Ağır Hipokloremi) | Serum Potasyum (K⁺): 3.1 mEq/L (Hipokalemi) | AST: 65 U/L | GGT: 18 U/L | BUN: 16 mg/dL | Kreatinin: 0.9 mg/dL | BHBA: 1.6 mmol/L"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "alkaloz"],
                "content": "Kan pH: 7.48 (Metabolik Alkaloz) | pO₂: 76 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 34.5 mmol/L | Baz Açığı (BE): +10.2 mmol/L | Cl⁻: 82 mEq/L | K⁺: 3.1 mEq/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Abdominal USG",
                "keywords": ["ultrason", "usg", "abomasum"],
                "content": "Abdominal Ultrasonografi: Sol 9. interkostal aralıkta rumen ile sol karın duvarı arasında sıvı ve gaz kıvrımları içeren abomasum organ yapısı gözlendi."
            }
        }
    },
    "Vaka 9 (Sığır 'Pamuk' - Sağa Abomasum Deplasmanı & Volvulus / RDA)": {
        "kod": "VAKA_9_RDA",
        "sikayet": "Sağ karın duvarında geniş alanda şiddetli ping sesi, aniden başlayan şiddetli huzursuzluk/sancı, taşikardi, ardından soğuk terleme ve çöküş.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "amonyak", "altlık"],
                "content": "Kapalı duraklı ahır. Pencereler yetersiz, amonyak/dışkı kokusu yüksek. Kısmen kirli ve gübreli altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem"],
                "content": "Yoğun yem ağırlıklı besleme."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Sabit işletme."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "doğum"],
                "content": "3 hafta önce doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "dehidrasyon", "şok", "sancı"],
                "content": "Vücut Sıcaklığı: 37.2 °C (Hipotermik / Şok) | Kalp Frekansı: 124 atım/dk | Solunum Frekansı: 46 nefes/dk | Mukozalar: Soluk ve Siyanotik | CRT: 4.5 saniye | Dehidrasyon: %10 | Sağ karın duvarında belirgin distansiyon ve dışarıdan görülen gerginlik."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp Oskültasyonu: Aşırı taşikardik ve filiform (zayıf) nabız. Akciğer sesleri hafif yüzeysel."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı & Rektal Muayene",
                "keywords": ["ağrı", "rektal", "sancı", "abomasum", "volvulus"],
                "content": "Şiddetli abdominal sancı bulguları. Rektal Muayene: Sağ lumbar alanda arkaya doğru uzanan gergin, devasa gaz ve sıvı dolu abomasum küresi palpe edildi."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi",
                "keywords": ["ping", "liptak", "abomasum", "sağ"],
                "content": "Sağ 8-13. Interkostal aralık ve sağ paralumbar fossa boyunca devasa alanda yüksek frekanslı metallic ping sesi. Liptak Testi (Abomasosentez): Sağ taraftan çekilen sıvı pH: 2.2, kahverengi-kanlı içerik."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen pH: 6.6."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Kültür",
                "keywords": ["kültür"],
                "content": "Patojen üremesi yok."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Ferroskop: Negatif. Glutaraldehit Testi: 14.0 Dakika."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "fibrinojen"],
                "content": "WBC: 16.4 x10³/µL | RBC: 8.2 x10⁶/µL | PCV: %46 (Şiddetli Hemokonsantrasyon) | Plazma Fibrinojeni: 410 mg/dL"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "laktat", "ast", "ggt", "bun", "kreatinin", "klor"],
                "content": "L-Laktat: 9.2 mmol/L (Ağır İskemik Dokusal Doku Nekrozu!) | Serum Klor (Cl⁻): 76 mEq/L | AST: 140 U/L | BUN: 52 mg/dL | Kreatinin: 2.6 mg/dL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "asidoz"],
                "content": "Kan pH: 7.15 (Metabolik İskemik Laktik Asidoz) | pO₂: 62 mmHg | pCO₂: 36 mmHg | HCO₃⁻: 12.0 mmol/L | Baz Açığı (BE): -14.2 mmol/L | Cl⁻: 76 mEq/L | K⁺: 5.6 mEq/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Abdominal USG",
                "keywords": ["ultrason", "usg", "abomasum", "volvulus"],
                "content": "Abdominal Ultrasonografi: Sağ karın duvarını kaplayan masif genişlemiş, duvarı 8 mm kalınlaşmış ödemli abomasum ve omentum dönmesi (Volvulus) görüntüsü."
            }
        }
    },
    "Vaka 10 (Sığır 'Efe' - Traumatik Retikuloperikarditis / TRP)": {
        "kod": "VAKA_10_TRP",
        "sikayet": "Gerdan ve çene altında soğuk hamur kıvamında ödem, sırtı kamburlaştırıp durma, kalp alanında su çalkantısı (splashing) sesi.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "tel", "çivi", "inşaat", "altlık", "bağlı"],
                "content": "Yarı kapalı eski beton zeminli bağlı ahır. Çevre padoğunda balya telleri ve inşaat atıkları mevcut. Rutin amonyak kokulu, kirli ıslak altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "balya", "tel"],
                "content": "Balya kaba yemi parçalanmadan verilmektedir. Tel/çivi karışma öyküsü vardır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Sabit işletme."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "doğum"],
                "content": "2 ay önce doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "dehidrasyon", "ödem", "gerdan", "jugular", "staz"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 104 atım/dk | Solunum Frekansı: 42 nefes/dk | Mukozalar: Soluk pembe | CRT: 2.8 saniye | Dehidrasyon: %6 | Gerdan, göğüs altı ve submandibuler alanda soğuk hamur ödem | Vena jugularis dolgunluğu ve yalancı jugular nabız (+) pozitif."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "splashing", "şılpırtı", "çalkantı", "boğuk"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri duyuluyor. Akciğer sesleri hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "inleme", "kambur"],
                "content": "Sopa testi, kama testi ve Withers pinch (cidago sıkma) ağrı testlerinin tamamı Pozitif (+). Hayvan sırtını kamburlaştırıp inlemektedir."
            },
            "PING_LIPTAK": {
                "name": "Ping & Liptak Testleri",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi negatif."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen pH: 6.7."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Perikardiyosentez Kültürü",
                "keywords": ["kültür", "perikardiyosentez", "bakteri", "eksuda", "trueperella"],
                "content": "Perikardiyosentez: Sol 5. interkostal aralıktan çekilen sıvı kirli sarı-yeşil, pis kokulu pürülan eksuda özellikte. Kültürde Trueperella pyogenes ve anaerobik Gram-negatif basiller üredi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["ferroskop", "glutaraldehit", "pıhtılaşma", "dedektör"],
                "content": "Ferroskop Metal Dedektörü: Sifoid kıkırdak sahasında şiddetli Pozitif metalik sinyal (Metalik Yabancı Cisim). Glutaraldehit Pıhtılaşma Testi: 2.0 Dakika (Ağır Şiddetli Akut Pozitif)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "fibrinojen", "pp/f"],
                "content": "WBC: 24.2 x10³/µL | Segmenteli Nötrofil: %70 | Çomak Nötrofil: %14 | Lenfosit: %12 | RBC: 5.2 x10⁶/µL | PCV: %27 | Plazma Fibrinojeni: 1280 mg/dL | PP/F: 6.1"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "bun", "kreatinin", "albümin", "globülin", "troponin"],
                "content": "Albümin: 2.6 g/dL | Globülin: 5.4 g/dL | AST: 125 U/L | GGT: 26 U/L | BUN: 30 mg/dL | Kreatinin: 1.3 mg/dL | Kardiyak Troponin I (cTnI): 0.92 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be"],
                "content": "Kan pH: 7.30 | pO₂: 70 mmHg | pCO₂: 46 mmHg | HCO₃⁻: 19.5 mmol/L | Baz Açığı (BE): -4.8 mmol/L | Laktat: 3.1 mmol/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Perikardiyal USG",
                "keywords": ["ultrason", "usg", "perikard", "fibrin"],
                "content": "Ultrasonografi: Perikardiyal boşlukta 4.5 cm kalınlığında fibrin bantları, gaz ekojeniteleri ve yoğun eksudatif sıvı birikimi. Retikulum ile diyafram arasında yapışıklık ve yabancı cisim yansıması."
            }
        }
    },
    "Vaka 11 (Buzağı 'Kınalı' - Rotavirus + Cryptosporidium & D-Laktat Nörotoksisitesi)": {
        "kod": "VAKA_11_BUZAGI",
        "sikayet": "10 günlük buzağıda inatçı sarı-yeşil sulu ishal, göz kürelerinde çökmeyle ağır dehidrasyon, sarhoş gibi yürüme (ataksi) ve emme refleksinin kaybolması.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "kulübe", "hutch", "altlık", "ıslak"],
                "content": "Bireysel buzağı kulübeleri (hutches). Dış ortam havadar ancak kulübe içi samanlar sulu dışkı ile bulaşık ve ıslak."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "süt", "kolostrum", "mama"],
                "content": "Günde 2 öğün 2'şer litre ılık anne sütü verilmektedir. Son 2 öğündür süt emmeyi tamamen reddetmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Sabit süt işletmesi doğumhanesi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "kolostrum", "aşı"],
                "content": "Doğumda kolostrum alımı gecikmiştir (Pasif bağışıklık yetersizliği)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "dehidrasyon", "göz", "çökük", "emme", "ataksi", "sarhoş"],
                "content": "Vücut Sıcaklığı: 37.4 °C (Hipotermik) | Kalp Frekansı: 130 atım/dk | Solunum Frekansı: 32 nefes/dk | Göz Küreleri: Yuvaya 8 mm belirgin çökmüş | CRT: 4.0 saniye | Dehidrasyon: %10 | Emme Refleksi: TAMAMEN KAYBOLMUŞ (0) | Duruş: Sarhoş yürüyüşü (Ataksi), ayakta duramayıp yatma (Stupor)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp sesleri taşikardik ve zayıf."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı Testleri",
                "keywords": ["ağrı"],
                "content": "Ağrı testleri negatif."
            },
            "PING_LIPTAK": {
                "name": "Ping & Liptak Testleri",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi yok."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen & Bağırsak Sıvısı",
                "keywords": ["rumen"],
                "content": "Henüz ön mide gelişmemiştir (Süt emme dönemi)."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Dışkı ELISA ve Asit-Fast Boyama",
                "keywords": ["kültür", "elisa", "rotavirus", "cryptosporidium", "dışkı", "kripto", "boyama"],
                "content": "Dışkı Hızlı ELISA Testi: Rotavirus Antijeni Pozitif (+++). Dışkı Ziehl-Neelsen (Asit-Fast) Boyama: Pembe küre şeklinde Cryptosporidium parvum ookistleri yoğun pozitif (+++)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Glutaraldehit Testi: 15.0 Dakika (Negatif)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "fibrinojen"],
                "content": "WBC: 12.4 x10³/µL | RBC: 8.9 x10⁶/µL | PCV: %48 (Ağır Hemokonsantrasyon) | Plazma Fibrinojeni: 380 mg/dL"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "d-laktat", "laktat", "bun", "kreatinin", "glikoz", "potasyum", "sodyum"],
                "content": "D-Laktat: 5.4 mmol/L (Ağır D-Laktik Nörotoksisite!) | BUN: 54 mg/dL | Serum Kreatinin: 2.4 mg/dL | Serum Glikoz: 42 mg/dL | Na⁺: 128 mEq/L | K⁺: 6.4 mEq/L (Hiperkalemi) | Cl⁻: 92 mEq/L"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "asidoz"],
                "content": "Kan pH: 7.08 (Kritik Şiddetli Metabolik Asidoz) | pO₂: 72 mmHg | pCO₂: 34 mmHg | HCO₃⁻: 9.2 mmol/L | Baz Açığı (BE): -18.5 mmol/L | D-Laktat: 5.4 mmol/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Bağırsak USG",
                "keywords": ["ultrason", "usg", "bağırsak"],
                "content": "Abdominal Ultrasonografi: İnce bağırsak lümenlerinde aşırı sıvı dolgunluğu ve peristaltik hızlanma."
            }
        }
    },
    "Vaka 12 (Kuzu 'Torun' - ETEC E. coli K99 & Akut Sekretuar Şok Asidozu)": {
        "kod": "VAKA_12_KUZU",
        "sikayet": "3 günlük kuzuda fışkırır tarzda sarımsı sulu ishal, yatamayıp yan yatma (lateral recumbency), soğuk ekstremiteler ve koma.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "ağıl", "koyun", "amonyak", "altlık", "kirli", "toprak"],
                "content": "Geleneksel toprak zeminli kapalı koyun ağılı. Havasız, nemli, yoğun amonyak kokulu. Aşırı kirli ve dışkı birikintili altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "ağız sütü", "kolostrum"],
                "content": "Ağız sütünü yeterince emememiştir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Sabit koyunculuk işletmesi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "doğum"],
                "content": "3 gün önce ikiz doğumla dünyaya gelmiştir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "mukoza", "crt", "dehidrasyon", "koma", "yan yatma", "ishal"],
                "content": "Vücut Sıcaklığı: 36.5 °C (Ağır Hipotermi) | Kalp Frekansı: 145 atım/dk (Zayıf Filiform) | Solunum Frekansı: 18 nefes/dk (Kussmaul Solunumu) | Mukozalar: Siyanotik ve Soğuk | CRT: 4.5 saniye | Dehidrasyon: %12 | Duruş: Yan yatma (Lateral Recumbency) ve Koma."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp sesleri aşırı zayıf ve ritimsiz (Aritmik - Hiperkalemi etkisi)."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı Testleri",
                "keywords": ["ağrı"],
                "content": "Ağrı testleri yanıt yok (Komatöz)."
            },
            "PING_LIPTAK": {
                "name": "Ping & Liptak Testleri",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi yok."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Sıvısı Analizi",
                "keywords": ["rumen"],
                "content": "Rumen gelişmemiştir."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Dışkı ETEC K99 Hızlı Testi",
                "keywords": ["kültür", "etec", "coli", "k99", "bakteri", "dışkı"],
                "content": "Dışkı ETEC K99 Antijen Testi: Pozitif (+++). Dışkı Kültürü: Masif Enterotoksijenik E. coli üremesi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Ferroskop & Glutaraldehit Testi",
                "keywords": ["ferroskop", "glutaraldehit"],
                "content": "Glutaraldehit Testi: 15.0 Dakika (Negatif)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "fibrinojen"],
                "content": "WBC: 18.2 x10³/µL | RBC: 9.8 x10⁶/µL | PCV: %52 (Şiddetli Şok Hemokonsantrasyonu) | Plazma Fibrinojeni: 350 mg/dL"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "potasyum", "sodyum", "klor", "bun", "kreatinin", "glikoz"],
                "content": "Serum Potasyum (K⁺): 7.2 mEq/L (Öldürücü Hiperkalemi!) | Na⁺: 124 mEq/L | Cl⁻: 88 mEq/L | BUN: 68 mg/dL | Serum Kreatinin: 3.2 mg/dL | Serum Glikoz: 28 mg/dL (Şiddetli Hipoglisemi)"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "asidoz"],
                "content": "Kan pH: 6.95 (Kritik Yaşamsal Dekompanse Asidoz) | pO₂: 65 mmHg | pCO₂: 28 mmHg | HCO₃⁻: 6.5 mmol/L | Baz Açığı (BE): -22.0 mmol/L | K⁺: 7.2 mEq/L"
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & USG",
                "keywords": ["ultrason", "usg"],
                "content": "Abdominal USG: Bağırsak lümenlerinde bol sıvı ve gaz birikimi."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnez & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde şıklar veya hazır butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız 
        (Örn: <i>"Ahır havalandırması nasıl?"</i>, <i>"Rasyonda ne kadar kesif yem var?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Kalp sesleri nasıl?"</i>, <i>"Hemogram tahlili istiyorum"</i>, <i>"Kan gazı analizi"</i>).
    </div>
""", unsafe_allow_html=True)

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

active_case = CASES[selected_case_name]

st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case['sikayet']}")

# Session State for Questions History
if "history" not in st.session_state:
    st.session_state.history = {}

if selected_case_name not in st.session_state.history:
    st.session_state.history[selected_case_name] = []

# Question Input Section
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    matched_cats = []
    
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\\b' + re.escape(kw_clean) + r'\\b', text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
                
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: Rasyon bilgisi nedir?, Ahır şartları nasıl?, Ateşi kaç?):",
        key="query_input",
        placeholder="Örn: Ahır havalandırması nasıl?, Rasyonda kaç kg yem var?, Hemogram sonuçları nedir?..."
    )

with col_button:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    submit_btn = st.button("🔎 Sor ve Sorgula", type="primary", use_container_width=True)

if submit_btn and user_query:
    matches = match_query(user_query, active_case["categories"])
    
    if matches:
        new_discoveries = 0
        for cat_key in matches:
            cat_data = active_case["categories"][cat_key]
            # Check if already in history
            already_in = any(item["cat_key"] == cat_key for item in st.session_state.history[selected_case_name])
            if not already_in:
                st.session_state.history[selected_case_name].append({
                    "cat_key": cat_key,
                    "query": user_query,
                    "title": cat_data["name"],
                    "content": cat_data["content"]
                })
                new_discoveries += 1
        
        if new_discoveries > 0:
            st.success(f"🎉 Teşekkürler! Sorunuzla ilişkili {new_discoveries} yeni klinik bulgu / bilgi açığa çıkarıldı!")
        else:
            st.info("Bu soruyla ilgili bilgi zaten daha önce açığa çıkarılmıştı. Aşağıdaki keşifler listenizden okuyabilirsiniz.")
    else:
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız (Örn: 'ahır', 'rasyon', 'ateş', 'kalp sesleri', 'hemogram', 'biyokimya', 'kan gazı', 'ultrason').")

# Display Discovered Information
st.markdown("---")
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(st.session_state.history[selected_case_name])} Bilgi Açıldı)")

if st.session_state.history[selected_case_name]:
    for idx, item in enumerate(reversed(st.session_state.history[selected_case_name])):
        st.markdown(f"""
            <div class='card-found'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <span class='badge-category'>{item['title']}</span>
                    <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                </div>
                <div class='card-content'><b>🩺 Bulgu / Öykü:</b> {item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Henüz bu vaka için soru sormadınız. Yukarıdaki arama kutusuna merak ettiğiniz soruyu yazarak muayeneye başlayınız.")

# Reset History Button
if st.session_state.history[selected_case_name]:
    if st.button("🗑️ Bu Vakanın Sorgu Geçmişini Temizle"):
        st.session_state.history[selected_case_name] = []
        st.rerun()

# Teacher Portal
with st.sidebar:
    st.markdown("### 🏛️ ÇU Veteriner Fakültesi")
    st.markdown("**VET401 İç Hastalıkları I**")
    st.markdown("---")
    st.markdown("### 🔒 Eğitmen Portalı")
    teacher_login = st.checkbox("Eğitmen Anahtar Paneli")
    if teacher_login:
        pass_code = st.text_input("Giriş Şifresi:", type="password")
        if pass_code == "vet401":
            st.success("Eğitmen Erişimi Onaylandı!")
            st.markdown("#### 🔑 Bu Vakanın Gizli Tüm Bilgileri:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("Hatalı Şifre!")
