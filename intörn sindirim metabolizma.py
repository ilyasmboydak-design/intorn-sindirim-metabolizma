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
    "Vaka A (Nisa - Sığır)": {
        "kod": "VAKA_A",
        "sikayet": "İştahsızlık, süt veriminde ani durma, sol lumbar bölgede dolgunluk, sulu ekşi ishal, sendeleyerek yürüme ve depresyon.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen"],
                "content": "Barınak Tipi: Kapalı tip, beton tabanlı bağlı duraklı ahır. Havalandırma: Yetersiz, içeride basık rutubetli hava ve hafif amonyak kokusu mevcut. Altlık Durumu: Samanlı ancak rumen asidozuna bağlı gelişen sulu ekşi kokulu ishal nedeniyle kirli, nemli ve ıslak."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "misir", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "yogun", "kesif", "nisasta", "kirma"],
                "content": "İşletmede %80 Mısır/Arpa kırması yoğun yem ve %20 Buğday samanı ağırlıklı rasyon verilmektedir. Kaba yem oranı son derece yetersizdir. 2 gün önce padoğa ani yüksek miktar kırma yem dökülmüş ve hayvan aşırı tüketmiştir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya", "yukseklik", "dag", "ova", "ceyhan"],
                "content": "Hayvan Ceyhan ovasında (rakım ~50 metre) sabit besi/süt tesisinde barındırılmaktadır. Nakil veya yayla öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once", "asidoz", "siskinlik", "timpani", "dogum"],
                "content": "Geçmişinde kaydedilmiş kronik sistemik veya metabolik hastalık yoktur. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "turgor", "gerdan", "odem", "jugularis", "staz", "sendeleme", "ataksi"],
                "content": "Vücut Sıcaklığı: 37.8 °C | Kalp Frekansı: 108 atım/dk | Solunum Frekansı: 44 nefes/dk | Mukoza: Soluk pembe-hiperemik | CRT: 3.5 saniye | Dehidrasyon: %10 | Göz Küresi Çöküklüğü: Belirgin çökmüş | Rumen Motilitesi: 0/5 dk (Atonik, sıvı çalkantısı) | Gerdan Ödemi: Yok | Vena Jugularis: Normal."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskutasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "vezikuler"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf sesler. Akciğer Oskültasyonu: Yüzeysel vesiküler solunum sesi. Rumende sıvı dalgalanma sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch", "retikulum", "hassasiyet", "inleme", "kifoz"],
                "content": "Sopa testi, Kama testi ve Withers pinch ağrı testlerinin tamamı NEGATİF (-)."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Rumen Sıvısı Analizi",
                "keywords": ["ping", "liptak", "perkusyon", "celik boru", "cinlama", "abomasosentez", "ph", "rumen ph", "protozoa"],
                "content": "Sol dorsal rumende gaz birikimine bağlı hafif çınlama sesi var ancak abomasal ping yok. Rumen Ponksiyon Sıvısı: pH: 4.6 (Şiddetli Laktik Asidoz), sütümsü-sarımsı renk, ekşi koku, canlı protozoa sayısı: 0 (Tamamı ölü), Gram boyamada Gram-pozitif rod ve koklar (Lactobacillus, S. bovis) hakim."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektor", "ferroskop", "metal", "hauptner", "miknatis", "yabanci cisim", "tel", "civi"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: NEGATİF (-), sifoid veya retikulum bölgesinde metalik sinyal saptanmadı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "comak", "segmenteli", "lenfosit", "monosit", "eozinofil", "bazofil", "plt", "trombosit", "mcv", "mch", "mchc", "rdw", "hb", "hemoglobin"],
                "content": "WBC: 3.8 x10³/µL (Lökopeni) | Çomak Nötrofil: %12 (Degeneratif sola kayma) | Segmenteli Nötrofil: %30 | Lenfosit: %50 | Monosit: %5 | Eozinofil: %2 | Bazofil: %1 | RBC: 8.9 x10⁶/µL | Hb: 15.2 g/dL | PCV: %48 (Ağır hemokonsantrasyon) | MCV: 53.9 fL | MCH: 17.0 pg | MCHC: 31.6 g/dL | RDW: %16.2 | PLT: 210 x10³/µL | Plazma Fibrinojeni: 350 mg/dL | Total Protein: 8.2 g/dL | PP/F Oranı: 23.4."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "alb", "globulin", "troponin", "glikoz", "bhba", "tp", "total protein"],
                "content": "Albümin: 3.1 g/dL | Total Protein: 8.2 g/dL | Globülin: 5.1 g/dL | AST: 185 U/L | GGT: 42 U/L | ALT: 38 U/L | ALP: 95 U/L | CK: 240 U/L | LDH: 1120 U/L | BUN: 48 mg/dL | Kreatinin: 2.1 mg/dL | Glikoz: 110 mg/dL | BHBA: 0.8 mmol/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "l-laktat", "d-laktat", "oksijen", "hipoksi", "potasyum", "klor", "sodyum", "na", "k", "cl", "elektrolit"],
                "content": "Kan pH: 7.12 (Ağır Laktik Asidoz) | pO₂: 58 mmHg | pCO₂: 32 mmHg | HCO₃⁻: 11.2 mmol/L | Baz Açığı (BE): -15.8 mmol/L | L-Laktat: 9.8 mmol/L | D-Laktat: 6.4 mmol/L (D-Laktik Nörotoksisite) | Na⁺: 132 mEq/L | K⁺: 5.8 mEq/L (Hiperkalemi) | Cl⁻: 92 mEq/L."
            },
            "GORUNTULEME_DISKI": {
                "name": "Görüntüleme & Mikrobiyoloji",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kultur", "bakteri", "perikardiyosentez", "ponksiyon", "sivi", "diski"],
                "content": "Abdominal Ultrasonografi: Rumen içeriğinde aşırı sıvı fazı ve üstte gaz tabakalaşması. Periton sıvısı miktarı ve yapısı normal."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "jellesme", "pihtilasma"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 Dakika (NEGATİF - Şiddetli yangısal protein artışı yok)."
            }
        }
    },
    "Vaka B (Maviş - Sığır)": {
        "kod": "VAKA_B",
        "sikayet": "Süt veriminde kademeli düşüş, yem reddi (yoğun yemi bırakıp az kaba yem yeme), sol açlık çukurunda çökme ve ara sıra sert az miktarda dışkılama.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen"],
                "content": "Barınak Tipi: Yarı açık serbest duraklı (free-stall) kauçuk yataklı modern ahır. Havalandırma: Son derece havadar, kokusuz, havalandırma fanları çalışan geniş mekan. Altlık Durumu: Duraklar ve kauçuk yataklar kuru, temiz ve bakımlı."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "misir", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "yogun", "kesif", "sut"],
                "content": "Yeni doğum yapmış yüksek verimli süt sığırı rasyonu (Yoğun yem ağırlıklı, kaba yem oranı %35) ile beslenmektedir. Rasyonda ani yem değişikliği yoktur."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya", "yukseklik"],
                "content": "Sabit süt işletmesinde barındırılmaktadır. Rakım değişikliği veya nakil öyküsü bulunmamaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once", "dogum", "hipokalsemi", "ketozis"],
                "content": "Yaklaşık 10 gün önce sorunsuz doğum yapmıştır. Doğum sonrası hafif subklinik hipokalsemi ve ketozis tedavisi görmüştür."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "turgor", "gerdan", "odem", "jugularis"],
                "content": "Vücut Sıcaklığı: 38.5 °C (Normal) | Kalp Frekansı: 78 atım/dk | Solunum Frekansı: 26 nefes/dk | Mukoza: Pembe-soluk | CRT: 2.0 saniye | Dehidrasyon: %4 | Göz Küresi Çöküklüğü: Hafif çökük | Rumen Motilitesi: 1/5 dk (Zayıf hipomotil) | Gerdan Ödemi: Yok | Vena Jugularis: Normal."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskutasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "vezikuler"],
                "content": "Kalp Oskültasyonu: Normal ritmik kalp sesleri. Akciğer Oskültasyonu: Veziküler solunum sesleri normal."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch", "retikulum", "hassasiyet", "inleme", "kifoz"],
                "content": "Retikulum ağrı testleri (Sopa, Kama, Withers pinch) NEGATİF (-)."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak (Abomasosentez) Testi",
                "keywords": ["ping", "liptak", "perkusyon", "celik boru", "cinlama", "abomasosentez", "sol ping", "ph", "abomasum ph"],
                "content": "Sol 8-12. interkostal aralık ve paralumbar fossa hattında perküsyon-oskültasyonda tipik çelik boru / çınlama sesi (Ping sesi / Steel band sound) duyuluyor. Liptak Testi (Abomasosentez): Sol 9. ICS'den girilerek çekilen sıvı pH: 2.8 (Abomasum hidroklorik asit sıvısı doğrulandı)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektor", "ferroskop", "metal", "hauptner", "miknatis", "yabanci cisim", "tel", "civi"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: NEGATİF (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "comak", "segmenteli", "lenfosit", "monosit", "eozinofil", "bazofil", "plt", "trombosit", "mcv", "mch", "mchc", "rdw", "hb", "hemoglobin"],
                "content": "WBC: 6.8 x10³/µL | Çomak Nötrofil: %1 | Segmenteli Nötrofil: %38 | Lenfosit: %54 | Monosit: %5 | Eozinofil: %2 | Bazofil: %0 | RBC: 6.2 x10⁶/µL | Hb: 11.5 g/dL | PCV: %31 | MCV: 50.0 fL | MCH: 18.5 pg | MCHC: 37.0 g/dL | RDW: %14.1 | PLT: 320 x10³/µL | Plazma Fibrinojeni: 280 mg/dL | Total Protein: 7.2 g/dL | PP/F Oranı: 25.7."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "alb", "globulin", "troponin", "glikoz", "bhba", "tp", "total protein"],
                "content": "Albümin: 3.2 g/dL | Total Protein: 7.2 g/dL | Globülin: 4.0 g/dL | AST: 72 U/L | GGT: 22 U/L | ALT: 25 U/L | ALP: 68 U/L | CK: 110 U/L | LDH: 680 U/L | BUN: 16 mg/dL | Kreatinin: 1.0 mg/dL | Glikoz: 52 mg/dL | BHBA: 2.1 mmol/L (Sekonder Ketozis)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "l-laktat", "d-laktat", "oksijen", "hipoksi", "potasyum", "klor", "sodyum", "na", "k", "cl", "elektrolit"],
                "content": "Kan pH: 7.48 (Metabolik Alkaloz) | pO₂: 42 mmHg | pCO₂: 46 mmHg | HCO₃⁻: 34.2 mmol/L | Baz Açığı (BE): +9.5 mmol/L | L-Laktat: 1.2 mmol/L | D-Laktat: 0.3 mmol/L | Na⁺: 136 mEq/L | K⁺: 3.1 mEq/L (Hipokalemi) | Cl⁻: 88 mEq/L (Hipokloremi - Hipokloremik Hipokalemik Metabolik Alkaloz)."
            },
            "GORUNTULEME_DISKI": {
                "name": "Görüntüleme & Mikrobiyoloji",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kultur", "bakteri", "perikardiyosentez", "ponksiyon", "sivi", "diski"],
                "content": "Abdominal Ultrasonografi: Sol 9-11. ICS hizasında rumen ile sol karın duvarı arasında kıvrımlı abomasum yapısı ve gaz-sıvı ara yüzü."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "jellesme", "pihtilasma"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 Dakika (NEGATİF - Yangısız mekanik/metabolik süreç)."
            }
        }
    },
    "Vaka C (Pamuk - Sığır)": {
        "kod": "VAKA_C",
        "sikayet": "Aniden başlayan şiddetli huzursuzluk, karnına bakma, tepinme (akut sancı), ardından şiddetli çökme, soğuk terleme, tam iştahsızlık ve dışkı yapamama.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen"],
                "content": "Barınak Tipi: Kapalı duraklı ahır. Havalandırma: Pencereleri yetersiz, içeride belirgin amonyak ve dışkı kokusu mevcut. Altlık Durumu: Altlıklar kısmen kirli, ıslak ve gübre birikintilidir."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "misir", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "yogun", "kesif"],
                "content": "Yüksek konsantre yem ağırlıklı besi/süt rasyonu ile beslenmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya", "yukseklik"],
                "content": "Sabit besi/süt tesisinde barındırılmaktadır. Rakım değişikliği yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once"],
                "content": "Son 24 saatte aniden gelişen akut klinik tablo."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "turgor", "gerdan", "odem", "jugularis"],
                "content": "Vücut Sıcaklığı: 37.2 °C (Hipotermik/Şok) | Kalp Frekansı: 124 atım/dk (Şiddetli Taşikardi) | Solunum Frekansı: 52 nefes/dk | Mukoza: Siyanotik, soluk ve soğuk | CRT: 4.5 saniye | Dehidrasyon: %11 | Göz Küresi Çöküklüğü: Belirgin çökmüş | Rumen Motilitesi: 0/5 dk (Atoni) | Gerdan Ödemi: Yok | Vena Jugularis: Dolgunluk zayıf (Şok)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskutasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "vezikuler"],
                "content": "Kalp Oskültasyonu: Hızlı, zayıf filamentöz sesler. Akciğer Oskültasyonu: Yüzeysel vesiküler solunum sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch", "retikulum", "hassasiyet", "inleme", "kifoz"],
                "content": "Sopa testi, Kama testi ve Withers pinch testlerinin tamamı POZİTİF (+) (Abomasal duvar gerilimi ve iskemik visceral ağrı nedeniyle inleme)."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak (Abomasosentez) Testi",
                "keywords": ["ping", "liptak", "perkusyon", "celik boru", "cinlama", "abomasosentez", "sag ping", "ph", "abomasum ph"],
                "content": "Sağ 8-13. interkostal aralık ve sağ paralumbar fossada geniş alanda yüksek frekanslı Sağ Ping Sesi (Steel band sound) ve sıvı çalkantı sesi duyuluyor. Rektal Muayene: Sağ üst kadranda gergin, gaz dolu geniş abomasum küresi palpe ediliyor. Liptak Testi: Sağ 10. ICS'den girilerek çekilen sıvı pH: 2.2 (Kanlı-hemorajik iskemik abomasum içeriği)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektor", "ferroskop", "metal", "hauptner", "miknatis", "yabanci cisim", "tel", "civi"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: NEGATİF (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "comak", "segmenteli", "lenfosit", "monosit", "eozinofil", "bazofil", "plt", "trombosit", "mcv", "mch", "mchc", "rdw", "hb", "hemoglobin"],
                "content": "WBC: 18.5 x10³/µL (Lökositoz) | Çomak Nötrofil: %15 (Şiddetli sola kayma) | Segmenteli Nötrofil: %52 | Lenfosit: %26 | Monosit: %6 | Eozinofil: %1 | Bazofil: %0 | RBC: 9.8 x10⁶/µL | Hb: 16.8 g/dL | PCV: %52 (Kritik hemokonsantrasyon) | MCV: 53.0 fL | MCH: 17.1 pg | MCHC: 32.3 g/dL | RDW: %16.8 | PLT: 140 x10³/µL | Plazma Fibrinojeni: 620 mg/dL | Total Protein: 8.9 g/dL | PP/F Oranı: 14.3."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "alb", "globulin", "troponin", "glikoz", "bhba", "tp", "total protein"],
                "content": "Albümin: 3.4 g/dL | Total Protein: 8.9 g/dL | Globülin: 5.5 g/dL | AST: 280 U/L | GGT: 58 U/L | ALT: 45 U/L | ALP: 140 U/L | CK: 650 U/L (İskemik doku nekrozu) | LDH: 1850 U/L | BUN: 62 mg/dL | Kreatinin: 2.8 mg/dL | Glikoz: 185 mg/dL (Şiddetli stres hiperglisemisi) | BHBA: 1.4 mmol/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "l-laktat", "d-laktat", "oksijen", "hipoksi", "potasyum", "klor", "sodyum", "na", "k", "cl", "elektrolit"],
                "content": "Kan pH: 7.18 (Şiddetli İskemik Laktik Asidoz) | pO₂: 38 mmHg | pCO₂: 38 mmHg | HCO₃⁻: 13.5 mmol/L | Baz Açığı (BE): -12.4 mmol/L | L-Laktat: 9.4 mmol/L (Abomasum gangreni göstergesi) | D-Laktat: 0.8 mmol/L | Na⁺: 128 mEq/L | K⁺: 5.9 mEq/L (Hiperkalemi) | Cl⁻: 76 mEq/L (Ağır Hipokloremi)."
            },
            "GORUNTULEME_DISKI": {
                "name": "Görüntüleme & Mikrobiyoloji",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kultur", "bakteri", "perikardiyosentez", "ponksiyon", "sivi", "diski"],
                "content": "Abdominal Ultrasonografi: Sağ karın duvarında 15 cm'yi aşan çapta duvarda ödem ve venöz staz olan devasa volvuluslu abomasum organı."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "jellesme", "pihtilasma"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: 12 Dakika (Hafif pozitif / Şok doku yanıtı)."
            }
        }
    },
    "Vaka D (Efe - Sığır)": {
        "kod": "VAKA_D",
        "sikayet": "Gerdan ve çene altında soğuk ödem, dirsekleri dışa açarak durma, sırtını kamburlaştırma (kifoz), adım atmaktan kaçınma, iştahsızlık ve inleme.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen"],
                "content": "Barınak Tipi: Yarı kapalı eski beton zeminli bağlı ahır. Çevre padoğunda inşaat atıkları ve balya telleri saçıktır. Havalandırma: Yetersiz, rutin amonyak kokusu mevcuttur. Altlık Durumu: Altlıklar ıslak, kirli ve gübrelidir."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "misir", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "tel", "civi"],
                "content": "Balyalanmış kaba yem (saman/yonca) ve karma fabrika yemi verilmektedir. Balya parçalama esnasında tellerin yeme karışmış olabileceği belirtilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya", "yukseklik"],
                "content": "Ova besi tesisinde (Ceyhan, rakım ~50 m) barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once"],
                "content": "Yaklaşık 1 haftadır devam eden kademeli iştahsızlık ve 3 gün önce gelişen gerdan ödemi."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "turgor", "gerdan", "odem", "jugularis", "staz"],
                "content": "Vücut Sıcaklığı: 39.8 °C (Yüksek Ateş) | Kalp Frekansı: 104 atım/dk | Solunum Frekansı: 44 nefes/dk | Mukoza: Soluk kirli pembe | CRT: 3.0 saniye | Dehidrasyon: %6 | Göz Küresi Çöküklüğü: Hafif çökük | Rumen Motilitesi: 0/5 dk | Gerdan Ödemi: Şiddetli soğuk hamur ödem (Gerdan ve submandibuler) | Vena Jugularis: Staz (+), yalancı jugular nabız (+)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskutasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "vezikuler"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvıya bağlı çamaşır makinesi / su çalkantısı (splashing / washing machine) sesi ve boğuk kalp sesleri. Akciğer Oskültasyonu: Ventro-lateral alanlarda azalmış solunum sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch", "retikulum", "hassasiyet", "inleme", "kifoz"],
                "content": "Sopa testi, Kama testi ve Withers pinch ağrı testlerinin tamamı POZİTİF (+) (Hayvan sırtını esnetmeyip inlemektedir)."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi",
                "keywords": ["ping", "liptak", "perkusyon", "celik boru", "cinlama"],
                "content": "Ping sesi yok. Liptak testi negatif."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektor", "ferroskop", "metal", "hauptner", "miknatis", "yabanci cisim", "tel", "civi"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: POZİTİF (+) (Sifoid kıkırdak üzerinde şiddetli metalik sinyal sesi alındı)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "comak", "segmenteli", "lenfosit", "monosit", "eozinofil", "bazofil", "plt", "trombosit", "mcv", "mch", "mchc", "rdw", "hb", "hemoglobin"],
                "content": "WBC: 24.5 x10³/µL (Şiddetli Lökositoz) | Çomak Nötrofil: %18 (Rejeneratif sola kayma) | Segmenteli Nötrofil: %58 | Lenfosit: %16 | Monosit: %6 | Eozinofil: %2 | Bazofil: %0 | RBC: 5.2 x10⁶/µL | Hb: 8.8 g/dL | PCV: %26 | MCV: 50.0 fL | MCH: 16.9 pg | MCHC: 33.8 g/dL | RDW: %15.8 | PLT: 450 x10³/µL | Plazma Fibrinojeni: 1350 mg/dL | Total Protein: 8.8 g/dL | PP/F Oranı: 6.5 (Aktif supuratif yangı)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "alb", "globulin", "troponin", "glikoz", "bhba", "tp", "total protein"],
                "content": "Albümin: 2.3 g/dL (Hipoalbüminemi) | Total Protein: 8.8 g/dL | Globülin: 6.5 g/dL (Hipergamaglobülinemi) | AST: 142 U/L | GGT: 32 U/L | ALT: 28 U/L | ALP: 110 U/L | CK: 180 U/L | LDH: 920 U/L | BUN: 32 mg/dL | Kreatinin: 1.4 mg/dL | Glikoz: 78 mg/dL | BHBA: 0.6 mmol/L | Kardiyak Troponin I (cTnI): 0.95 ng/mL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "l-laktat", "d-laktat", "oksijen", "hipoksi", "potasyum", "klor", "sodyum", "na", "k", "cl", "elektrolit"],
                "content": "Kan pH: 7.31 | pO₂: 68 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 20.5 mmol/L | Baz Açığı (BE): -4.2 mmol/L | L-Laktat: 2.9 mmol/L | D-Laktat: 0.4 mmol/L | Na⁺: 134 mEq/L | K⁺: 4.2 mEq/L | Cl⁻: 95 mEq/L."
            },
            "GORUNTULEME_DISKI": {
                "name": "Görüntüleme & Ponksiyon Bulguları",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kultur", "bakteri", "perikardiyosentez", "ponksiyon", "sivi", "diski"],
                "content": "Perikardiyosentez (Sol 5. ICS): Kirli sarı-yeşil, pis kokulu pürülan eksuda (Kültürde Trueperella pyogenes). Ultrasonografi: Perikardiyal boşlukta 4 cm kalınlığında fibrin bantları, gaz ekojeniteleri ve retikulum yapışıklıkları."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "jellesme", "pihtilasma"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: 2.0 Dakika (Ağır Akut Pozitif - Şiddetli fibrinojen ve globülin artışı)."
            }
        }
    },
    "Vaka E (Kınalı - Buzağı)": {
        "kod": "VAKA_E",
        "sikayet": "12 günlük dişi buzağıda açık sarı-yeşil sulu kokuşumlu ishal, emme refleksinin kaybolması, başını yana düşürme, sarhoş yürüyüş (ataksi) ve stupor/koma.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen", "kulube"],
                "content": "Barınak Tipi: Bireysel buzağı kulübeleri (hutches). Havalandırma: Dış ortam havadar ancak kulübe içi altlıklar (saman) ıslak, kirli ve sulu dışkı ile bulaşıktır. Serin ve nemli mikroflora."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "sut", "mama", "ikame", "kolostrum"],
                "content": "Anne sütü ve ikame buzağı sütü ile beslenmektedir. Kolostrum alımı doğumda gecikmiştir (FPT şüphesi)."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya", "yukseklik"],
                "content": "Ceyhan süt işletmesi buzağılığı."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once"],
                "content": "3 gündür devam eden kademeli sulu ishal."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "turgor", "gerdan", "odem", "emme", "refleks", "ataksi", "koma", "stupor"],
                "content": "Vücut Sıcaklığı: 37.1 °C (Hipotermi) | Kalp Frekansı: 130 atım/dk | Solunum Frekansı: 58 nefes/dk (Kussmaul solunumu) | Mukoza: Kuru soluk | CRT: 4.0 saniye | Dehidrasyon: %10 | Göz Küresi Çöküklüğü: Belirgin çökmüş | Emme Refleksi: 0 (Tamamen yok, ataksi ve stupor)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskutasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "vezikuler"],
                "content": "Kalp Oskültasyonu: Taşikardik ve aritmik. Akciğer Oskültasyonu: Yüzeysel solunum sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch"],
                "content": "Buzağılarda uygulanmaz."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi",
                "keywords": ["ping", "liptak"],
                "content": "Uygulanmaz."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör Muayenesi",
                "keywords": ["dedektor", "ferroskop"],
                "content": "Uygulanmaz."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "comak", "segmenteli", "lenfosit", "monosit", "eozinofil", "bazofil", "plt", "trombosit", "mcv", "mch", "mchc", "rdw", "hb", "hemoglobin"],
                "content": "WBC: 11.2 x10³/µL | Çomak Nötrofil: %4 | Segmenteli Nötrofil: %48 | Lenfosit: %42 | Monosit: %5 | Eozinofil: %1 | Bazofil: %0 | RBC: 9.2 x10⁶/µL | Hb: 15.8 g/dL | PCV: %46 (Hemokonsantrasyon) | MCV: 50.0 fL | MCH: 17.1 pg | MCHC: 34.3 g/dL | RDW: %15.2 | PLT: 280 x10³/µL | Plazma Fibrinojeni: 320 mg/dL | Total Protein: 7.8 g/dL | PP/F Oranı: 24.3."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "alb", "globulin", "troponin", "glikoz", "bhba", "tp", "total protein"],
                "content": "Albümin: 3.2 g/dL | Total Protein: 7.8 g/dL | Globülin: 4.6 g/dL | AST: 65 U/L | GGT: 25 U/L | ALT: 22 U/L | ALP: 120 U/L | CK: 140 U/L | LDH: 750 U/L | BUN: 54 mg/dL | Kreatinin: 2.4 mg/dL | Glikoz: 42 mg/dL (Hipoglisemi)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "l-laktat", "d-laktat", "oksijen", "hipoksi", "potasyum", "klor", "sodyum", "na", "k", "cl", "elektrolit"],
                "content": "Kan pH: 7.08 (Ağır Metabolik Asidoz) | pO₂: 52 mmHg | pCO₂: 34 mmHg | HCO₃⁻: 9.8 mmol/L | Baz Açığı (BE): -18.2 mmol/L | L-Laktat: 2.8 mmol/L | D-Laktat: 7.8 mmol/L (Ağır D-Laktik Nörotoksisite) | Na⁺: 128 mEq/L | K⁺: 6.8 mEq/L (Kritik Hiperkalemi - EKG Aritmi Riski!) | Cl⁻: 98 mEq/L."
            },
            "GORUNTULEME_DISKI": {
                "name": "Dışkı Muayenesi & ELISA Testi",
                "keywords": ["diski", "elisa", "rotavirus", "crypto", "cryptosporidium", "e. coli", "k99"],
                "content": "Dışkı Hızlı ELISA Kiti: Rotavirus (+) ve Cryptosporidium parvum (+) POZİTİF. E. coli K99 (-)."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "jellesme"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 Dakika (NEGATİF)."
            }
        }
    },
    "Vaka F (Torun - Kuzu)": {
        "kod": "VAKA_F",
        "sikayet": "3 günlük erkek kuzuda aniden başlayan fışkırır tarzda sulu sarımsı ishal, ayağa kalkamama, buz gibi soğuk kulaklar/ağız, şiddetli dehidrasyon ve koma.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen", "agil"],
                "content": "Barınak Tipi: Geleneksel toprak zeminli, pencereleri kapalı yoğun koyun ağılı. Havalandırma: Havasız, amonyak ve rutubet kokusu aşırı yüksek. Altlık Durumu: Altlıklar aşırı kirli, nemli ve dışkı birikintilidir."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "sut", "kolostrum"],
                "content": "Anne sütü emmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya", "yukseklik"],
                "content": "Yayla dönüşü ağıl tesisi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "oyku"],
                "content": "Ağılda son 2 günde 5 kuzuda benzer aniden başlayan salgın ishal öyküsü."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "turgor", "gerdan", "odem", "emme", "refleks", "kulak", "koma"],
                "content": "Vücut Sıcaklığı: 36.4 °C (Derin Hipotermi) | Kalp Frekansı: 145 atım/dk (Zayıf filamentöz) | Solunum Frekansı: 64 nefes/dk | Mukoza: Bembeyaz, kuru | CRT: 5.0 saniye | Dehidrasyon: %12 (Kritik) | Göz Küresi Çöküklüğü: Belirgin çökmüş | Emme Refleksi: 0."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskutasyon", "dinleme", "ufurum", "silpirti", "calkanti", "akciger"],
                "content": "Kalp Oskültasyonu: Taşikardik ve zayıf. Akciğer Oskültasyonu: Hızlı yüzeysel solunum."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers"],
                "content": "Kuzularda uygulanmaz."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi",
                "keywords": ["ping", "liptak"],
                "content": "Uygulanmaz."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör Muayenesi",
                "keywords": ["dedektor", "ferroskop"],
                "content": "Uygulanmaz."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "comak", "segmenteli", "lenfosit", "monosit", "eozinofil", "bazofil", "plt", "trombosit", "mcv", "mch", "mchc", "rdw", "hb", "hemoglobin"],
                "content": "WBC: 16.8 x10³/µL | Çomak Nötrofil: %12 | Segmenteli Nötrofil: %54 | Lenfosit: %28 | Monosit: %5 | Eozinofil: %1 | Bazofil: %0 | RBC: 10.5 x10⁶/µL | Hb: 17.2 g/dL | PCV: %54 (Aşırı hemokonsantrasyon) | MCV: 51.4 fL | MCH: 16.3 pg | MCHC: 31.8 g/dL | RDW: %16.0 | PLT: 190 x10³/µL | Plazma Fibrinojeni: 410 mg/dL | Total Protein: 8.4 g/dL | PP/F Oranı: 20.4."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "alb", "globulin", "troponin", "glikoz", "bhba", "tp", "total protein"],
                "content": "Albümin: 3.5 g/dL | Total Protein: 8.4 g/dL | Globülin: 4.9 g/dL | AST: 88 U/L | GGT: 28 U/L | BUN: 68 mg/dL | Kreatinin: 3.2 mg/dL | Glikoz: 32 mg/dL (Ağır Hipoglisemi)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "l-laktat", "d-laktat", "oksijen", "hipoksi", "potasyum", "klor", "sodyum", "na", "k", "cl", "elektrolit"],
                "content": "Kan pH: 6.98 (Hayati Tehlikeli Ağır Asidoz) | pO₂: 48 mmHg | pCO₂: 32 mmHg | HCO₃⁻: 6.5 mmol/L | Baz Açığı (BE): -22.5 mmol/L | L-Laktat: 8.2 mmol/L (Şok doku hipoksisi) | D-Laktat: 1.2 mmol/L | Na⁺: 122 mEq/L | K⁺: 7.2 mEq/L (Öldürücü Hiperkalemi!) | Cl⁻: 92 mEq/L."
            },
            "GORUNTULEME_DISKI": {
                "name": "Dışkı Muayenesi & Biyotiplendirme",
                "keywords": ["diski", "elisa", "e. coli", "k99", "etec"],
                "content": "Dışkı Hızlı ELISA Kiti: ETEC E. coli K99 (+) POZİTİF (Sekretuar toksijenik ishal)."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "jellesme"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 Dakika (NEGATİF)."
            }
        }
    }
}

# Instructor Portal Password
INSTRUCTOR_PASS = "vet401"

# Sidebar - Instructor Portal
st.sidebar.markdown("## 🔑 Eğitmen Şifreli Portalı")
admin_input = st.sidebar.text_input("Eğitmen Şifresi:", type="password", key="admin_pass_input")

is_instructor = (admin_input == INSTRUCTOR_PASS)

if is_instructor:
    st.sidebar.success("🔓 Eğitmen Erişimi Onaylandı! Tüm vaka kartları açık.")

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnez & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde şıklar veya hazır butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız 
        (Örn: <i>"Ahır yapısı ve havalandırması nasıl?"</i>, <i>"Hayvan ne yiyor?"</i>, <i>"Ping sesi var mı?"</i>, <i>"Ateşi kaç?"</i>, <i>"Ferroskop muayenesi yap"</i>, <i>"Hemogram sonuçları nedir?"</i>, <i>"Kan gazı istiyorum"</i>).
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
            if re.search(r'\b' + re.escape(kw_clean), text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
                
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: Ahır havalandırması nasıl?, Rasyon bilgisi nedir?, Ping var mı?, Ateşi kaç?):",
        key="query_input",
        placeholder="Örn: Ahır şartları ve havalandırma?, Hayvan ne yiyor?, Metal dedektörü, Hemogram, Kan gazı..."
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
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız (Örn: 'ahır', 'rasyon', 'ateş', 'ping', 'ferroskop', 'hemogram', 'kan gazı').")

# Display Discovered Information or Instructor View
st.markdown("---")

if is_instructor:
    st.markdown(f"### 🔓 EĞİTMEN GENEL BAKIŞ MODU — {selected_case_name} Tüm Kartlar")
    for cat_key, cat_data in active_case["categories"].items():
        st.markdown(f"""
            <div class='card-found'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <span class='badge-category'>{cat_data['name']}</span>
                    <span style='font-size:12px; color:#1F4E79; font-weight:bold;'>Eğitmen Görünümü</span>
                </div>
                <div class='card-content'><b>🩺 Bulgu / Öykü:</b> {cat_data['content']}</div>
            </div>
        """, unsafe_allow_html=True)
else:
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
