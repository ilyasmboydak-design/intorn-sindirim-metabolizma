import streamlit as st
import re

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
    page_icon="🐄",
    layout="wide",
)

# Custom CSS Styling
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

# Cases Knowledge Base (VET401 Sindirim & Metabolizma Sistemleri)
CASES = {
    "Vaka A (Sığır 'Nisa')": {
        "kod": "VAKA_A",
        "sikayet": "İştahsızlık, süt veriminde ani çöküş, ekşi sulu ishal, durgunluk, yatma eğilimi.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen"],
                "content": "Kapalı beton zeminli bağlı ahır. Yetersiz havalandırma, basık amonyak kokusu. Ekşi sulu ishale bağlı kirli ve ıslak saman altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "misir", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "yogun", "kesif", "kirma", "kg", "miktar"],
                "content": "Doğum sonrası süt verimindeki hızlı artış üzerine rasyondaki yoğun yem (arpa/mısır kırması) miktarı aniden artırılmıştır. Günlük verilen yem miktarları: 14 kg mısır silajı, 3 kg buğday samanı ve 12 kg yoğun süt yemi (arpa/mısır kırması)."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya", "yukseklik", "dag", "ova", "metre"],
                "content": "Ceyhan ovasındaki sabit süt tesisinde doğup büyümüştür. Herhangi bir yayla veya yüksek rakım nakli öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once", "dogum"],
                "content": " Yaklaşık 3 hafta önce sorunsuz doğum yapmıştır. Geçmişinde tekrarlayan hafif subakut şişkinlik atakları dışında kayıtlı kronik enfeksiyon yok."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "cokuk", "vital"],
                "content": "Vücut Sıcaklığı: 38.4 °C | Kalp Frekansı: 98 atım/dk | Solunum Frekansı: 38 nefes/dk | Mukoza: Hiperemik (Kırmızımsı) | CRT: 3.0 saniye | Dehidrasyon: %8 | Göz Küresi Çöküklüğü: 4 mm çökük | Dışkı: Sarımsı-gri sulu, ekşi kokulu, sindirilmemiş yem taneli."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Oskültasyon Bulguları (Kalp & Akciğer & Rumen)",
                "keywords": ["kalp ses", "oskultasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "rumen hareket", "cinlama"],
                "content": "Kalp Oskültasyonu: Taşikardik, üfürüm veya çalkantı sesi yok. Akciğer Oskültasyonu: Sert veziküler solunum sesleri. Rumen Oskültasyonu: Rumen hareketleri 0/2 dk (Atonik). Sol dorsal rumende gaz birikimine bağlı hafif çınlama sesi var ancak abomasal ping yok."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch", "retikulum", "hassasiyet", "inleme"],
                "content": "Sopa testi, kama testi ve Withers pinch (cidago sıkma) ağrı testlerinin tamamı Negatif (-)."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi (Abomasosentez)",
                "keywords": ["ping", "liptak", "abomasosentez", "abomasum ph", "steel band", "cinlama"],
                "content": "Sol 8-12. ICS hat boyunca metallic abomasal ping sesi YOKTUR. Liptak Testi (Abomasosentez): Sol alt karın duvarından sıvı ponksiyonunda abomasal sıvı çekilemedi (pH > 6.0, yeşilimsi rumen sıvısı girmekte)."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen ph", "rumen sivisi", "protozoa", "mikroskobi", "laktik asit", "eksi", "renk"],
                "content": "Rumen Sıvısı pH: 4.6 | Renk: Sütümsü-sarımsı | Koku: Ekşi laktik asit kokusu | Kıvam: Sulu, mikro-viskoz | Canlı Protozoa Sayısı: 0 / HPF (Mikroskobide protozoon saptanmadı)."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Gram Boyama & Kültür",
                "keywords": ["gram", "boyama", "kultur", "bakteri", "lactobacillus", "streptococcus bovis", "flora", "elisa", "diski"],
                "content": "Rumen Sıvısı Gram Boyama: Gram-pozitif rod ve koklar (Lactobacillus spp., Streptococcus bovis) hakim. Gram-negatif flora kaybolmuş. Dışkı kültüründe patojen Salmonella üremedi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektor", "ferroskop", "metal", "hauptner", "miknatis", "yabanci cisim"],
                "content": "Ferroskop Muayenesi: Negatif (-), retikulum veya sifoid bölgesinde metalik sinyal saptanmadı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "plt", "rdw", "mcv"],
                "content": "Lökosit (WBC): 14.8 x10³/µL | Eritrosit (RBC): 7.8 x10⁶/µL | Hemoglobin (Hb): 14.2 g/dL | Hematokrit (PCV): %46 | MCV: 58.9 fL | MCH: 18.2 pg | MCHC: 30.8 g/dL | RDW: %18.5 | Plazma Fibrinojeni: 650 mg/dL | Total Protein: 8.4 g/dL | PP/F Oranı: 12.9 | Trombosit (PLT): 320 x10³/µL | Nötrofil: %68 (Çomak: %12, Segmenteli: %56) | Lenfosit: %24 | Monosit: %5 | Eozinofil: %2 | Bazofil: %1."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "globulin", "bhba", "glikoz"],
                "content": "Albümin: 3.1 g/dL | Globülin: 5.3 g/dL | AST: 185 U/L | GGT: 52 U/L | ALT: 38 U/L | ALP: 110 U/L | CK: 140 U/L | LDH: 1150 U/L | BUN: 38 mg/dL | Kreatinin: 1.6 mg/dL | Total Bilirubin: 0.9 mg/dL | BHBA: 1.1 mmol/L | Glikoz: 42 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "d-laktat", "l-laktat", "sodyum", "potasyum", "klor", "na", "k", "cl"],
                "content": "Kan pH: 7.21 | pO₂: 75 mmHg | pCO₂: 34 mmHg | HCO₃⁻: 13.5 mmol/L | Baz Açığı (BE): -11.8 mmol/L | L-Laktat: 5.4 mmol/L | D-Laktat: 6.8 mmol/L | Na⁺: 132 mEq/L | K⁺: 5.4 mEq/L | Cl⁻: 96 mEq/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "karaciger", "apse", "vena cava", "rontgen"],
                "content": "Abdominal USG: Rumen içeriğinde aşırı sıvılaşma ve serbest gaz kubbesi. Karaciğer parankiminde 3 cm çapında hiperekojen kılıflı apse odakları şüphesi. Perikard ve pleura temiz."
            }
        }
    },
    "Vaka B (Sığır 'Maviş')": {
        "kod": "VAKA_B",
        "sikayet": "İştahsızlık (kaba yemi reddetme, az miktarda yoğun yem yeme), süt veriminde kademeli düşüş, dışkı miktarında azalma ve cıvıklık.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen"],
                "content": "Yarı açık serbest duraklı (free-stall) kauçuk yataklı modern ahır. Havadar, kokusuz. Temiz ve kuru duraklar."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "misir", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "yogun", "yonca", "kg"],
                "content": "Günlük rasyon: 22 kg mısır silajı, 8 kg fabrika süt yemi, 2 kg alfa-alfa yonca otu. Yem reddi ve yem seçme gözleniyor."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya", "yukseklik"],
                "content": "Sabit süt işletmesinde barındırılmaktadır. Rakım değişikliği veya nakil öyküsü bulunmamaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once", "sut hummasi", "hipokalsemi"],
                "content": "12 gün önce sorunsuz doğum yapmış. Doğum sonrası hafif hipokalsemi (süt hummasi) tedavisi görmüştür."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital"],
                "content": "Vücut Sıcaklığı: 38.6 °C | Kalp Frekansı: 78 atım/dk | Solunum Frekansı: 24 nefes/dk | Mukoza: Pembe | CRT: 2.0 saniye | Dehidrasyon: %4 | Göz Küresi Çöküklüğü: 1 mm çökük | Dışkı: Az miktarda, cıvık ve koyu renkli."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Oskültasyon Bulguları (Kalp & Akciğer & Rumen)",
                "keywords": ["kalp ses", "oskultasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "rumen"],
                "content": "Kalp & Akciğer Oskültasyonu: Kalp sesleri ve akciğer sesleri tamamen normal. Rumen Oskültasyonu: Rumen hareketleri 1/2 dk (hipomotil)."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch", "retikulum"],
                "content": "Sopa testi, kama testi ve Withers pinch ağrı testleri Negatif (-)."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi (Abomasosentez)",
                "keywords": ["ping", "liptak", "abomasosentez", "abomasum ph", "steel band", "cinlama"],
                "content": "Sol 8-12. ICS hat boyunca stetoskop-perküsyon uygulandığında yüksek frekanslı metallic ping (steel band sound) sesi pozitif (+). Liptak Testi (Abomasosentez): Sol ping alanının altından çekilen berrak pembe-kahverengi sıvı pH: 2.4."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen ph", "rumen sivisi", "protozoa", "mikroskobi"],
                "content": "Rumen Sıvısı pH: 6.8 | Renk: Zeytin yeşili | Koku: Normal aromatik rumen kokusu | Canlı Protozoa Sayısı: Yoğun ve hareketli."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Gram Boyama & Kültür",
                "keywords": ["gram", "boyama", "kultur", "bakteri", "flora"],
                "content": "Gram-negatif ve Gram-pozitif dengeli normal rumen mikroflorası. Dışkı kültüründe patojen üremedi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektor", "ferroskop", "metal", "hauptner"],
                "content": "Ferroskop Muayenesi: Negatif (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "plt"],
                "content": "Lökosit (WBC): 6.8 x10³/µL | Eritrosit (RBC): 6.2 x10⁶/µL | Hemoglobin (Hb): 11.5 g/dL | Hematokrit (PCV): %33 | MCV: 53.2 fL | MCH: 18.5 pg | MCHC: 34.8 g/dL | RDW: %14.2 | Plazma Fibrinojeni: 350 mg/dL | Total Protein: 7.2 g/dL | PP/F Oranı: 20.5 | Trombosit (PLT): 280 x10³/µL | Nötrofil: %48 (Çomak: %2, Segmenteli: %46) | Lenfosit: %44 | Monosit: %5 | Eozinofil: %2 | Bazofil: %1."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "globulin", "bhba", "glikoz"],
                "content": "Albümin: 3.3 g/dL | Globülin: 3.9 g/dL | AST: 72 U/L | GGT: 22 U/L | ALT: 24 U/L | ALP: 85 U/L | CK: 95 U/L | LDH: 680 U/L | BUN: 16 mg/dL | Kreatinin: 1.0 mg/dL | Total Bilirubin: 0.4 mg/dL | BHBA: 2.4 mmol/L | Glikoz: 38 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "sodyum", "potasyum", "klor", "na", "k", "cl"],
                "content": "Kan pH: 7.48 | pO₂: 82 mmHg | pCO₂: 46 mmHg | HCO₃⁻: 33.5 mmol/L | Baz Açığı (BE): +8.5 mmol/L | L-Laktat: 1.4 mmol/L | D-Laktat: 0.8 mmol/L | Na⁺: 136 mEq/L | K⁺: 3.1 mEq/L | Cl⁻: 88 mEq/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg", "abomasum"],
                "content": "Sol 9-11. ICS alanda sol karın duvarı ile rumen arasında gaz-sıvı ara yüzeyi içeren genişlemiş abomasum kıvrımları tespiti."
            }
        }
    },
    "Vaka C (Sığır 'Pamuk')": {
        "kod": "VAKA_C",
        "sikayet": "Aniden ortaya çıkan şiddetli sancı, kıvranma, arkaya vurma, aşırı dehidrasyon, göz çökmesi, dışkı yapamama.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen"],
                "content": "Kapalı duraklı ahır. Pencereler yetersiz, amonyak/dışkı kokusu yüksek. Kısmen kirli ve gübreli altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "misir", "arpa", "silaj", "yogun", "kg"],
                "content": "18 kg mısır silajı, 9 kg yoğun yem. Son 24 saatte yem tüketimi tamamen durmuştur."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya"],
                "content": "Besi ve süt tesisi sabit barınağı."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once"],
                "content": "3 hafta önce sorunsuz doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital"],
                "content": "Vücut Sıcaklığı: 37.8 °C | Kalp Frekansı: 118 atım/dk | Solunum Frekansı: 48 nefes/dk | Mukoza: Soluk ve Siyanotik | CRT: 4.5 saniye | Dehidrasyon: %11 | Göz Küresi Çöküklüğü: 8 mm çökmüş | Dışkı: Rektum tamamen boş, mukuslu kan var."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Oskültasyon Bulguları (Kalp & Akciğer & Rumen)",
                "keywords": ["kalp ses", "oskultasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "rumen"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düştü sesleri. Akciğer Oskültasyonu: Yüzeyel hızlı solunum. Rumen Oskültasyonu: Rumen hareketleri tamamen durmuş (0/2 dk)."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch", "retikulum", "sanci"],
                "content": "Sırtını kamburlaştırma, karın bölgesine tekme atma, ağrılı inleme. Sopa/Kama genel huzursuzluk yaratıyor."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi (Abomasosentez)",
                "keywords": ["ping", "liptak", "abomasosentez", "abomasum ph", "steel band", "cinlama"],
                "content": "Sağ 8-13. ICS hat ve paralumbar fossaya uzanan geniş alanda aşırı çınlamalı metallic ping sesi pozitif (+). Liptak Testi: Sağ ping alanından çekilen kanlı-bulanık sıvı pH: 3.1."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen ph", "rumen sivisi", "protozoa"],
                "content": "Rumen Sıvısı pH: 7.2 | Renk: Kahverengi-sarı | Kıvam: Durgun | Protozoa sayısı oldukça azalmış."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Gram Boyama & Kültür",
                "keywords": ["gram", "boyama", "kultur", "bakteri"],
                "content": "Dışkı örneği alınamadı (rektum boş, mukuslu kan var). Kan kültüründe bakılan bakteri yok."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektor", "ferroskop", "metal", "hauptner"],
                "content": "Ferroskop Muayenesi: Negatif (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "plt"],
                "content": "Lökosit (WBC): 18.6 x10³/µL | Eritrosit (RBC): 8.9 x10⁶/µL | Hemoglobin (Hb): 16.5 g/dL | Hematokrit (PCV): %51 | MCV: 57.3 fL | MCH: 18.5 pg | MCHC: 32.3 g/dL | RDW: %19.2 | Plazma Fibrinojeni: 780 mg/dL | Total Protein: 9.2 g/dL | PP/F Oranı: 11.7 | Trombosit (PLT): 180 x10³/µL | Nötrofil: %74 (Çomak: %18, Segmenteli: %56) | Lenfosit: %20 | Monosit: %4 | Eozinofil: %1 | Bazofil: %1."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "globulin", "bhba", "glikoz"],
                "content": "Albümin: 3.6 g/dL | Globülin: 5.6 g/dL | AST: 240 U/L | GGT: 65 U/L | ALT: 45 U/L | ALP: 145 U/L | CK: 380 U/L | LDH: 1650 U/L | BUN: 54 mg/dL | Kreatinin: 2.8 mg/dL | Total Bilirubin: 1.8 mg/dL | BHBA: 1.8 mmol/L | Glikoz: 112 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "sodyum", "potasyum", "klor", "na", "k", "cl"],
                "content": "Kan pH: 7.18 | pO₂: 65 mmHg | pCO₂: 38 mmHg | HCO₃⁻: 14.2 mmol/L | Baz Açığı (BE): -12.5 mmol/L | L-Laktat: 8.9 mmol/L | D-Laktat: 2.1 mmol/L | Na⁺: 128 mEq/L | K⁺: 5.9 mEq/L | Cl⁻: 78 mEq/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg", "abomasum", "volvulus"],
                "content": "Sağ 9-12. ICS alanda aşırı distandü olmuş, duvar kalınlığı 8 mm'ye ulaşmış, lümeninde hiperekojen gaz ve kanlı sıvı birikimi gösteren abomasum küresi tespiti."
            }
        }
    },
    "Vaka D (Sığır 'Efe')": {
        "kod": "VAKA_D",
        "sikayet": "Gerdan ve submandibuler bölgede ödem, dirsekleri dışa açarak durma, kambur duruş, inleme, süt veriminde bıçak gibi kesilme.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen"],
                "content": "Yarı kapalı eski beton zeminli bağlı ahır. Çevre padoğunda balya telleri ve inşaat atıkları mevcut. Rutin amonyak kokulu, kirli ıslak altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "misir", "arpa", "silaj", "balya", "saman", "kaba", "tel", "civi", "kg"],
                "content": "Günlük 15 kg mısır silajı, 4 kg saman, 6 kg fabrika yemi. Kaba yeme inşaat telinin karışmış olma öyküsü."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "cografya"],
                "content": "Ceyhan sabit besi/süt işletmesi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "metritis", "rahim", "mastitis", "meme", "oyku", "gecirdi", "once"],
                "content": "2 ay önce sorunsuz doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "odem", "jugular"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 104 atım/dk | Solunum Frekansı: 44 nefes/dk | Mukoza: Soluk pembe | CRT: 2.8 saniye | Dehidrasyon: %6 | Göz Küresi Çöküklüğü: 3 mm çökük | Gerdan ve submandibuler bölgede soğuk hamur ödem, Vena jugularis stazı ve yalancı nabız (+)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Oskültasyon Bulguları (Kalp & Akciğer & Rumen)",
                "keywords": ["kalp ses", "oskultasyon", "dinleme", "ufurum", "silpirti", "calkanti", "splashing", "muffled", "boguk", "rall", "akciger", "rumen"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri azalmış. Rumen Oskültasyonu: Rumen hareketleri 0/2 dk (Atonik)."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "pinch", "retikulum", "hassasiyet", "inleme"],
                "content": "Sopa Testi: Pozitif (+), inleme ve kifoz. Kama Testi: Pozitif (+). Withers Pinch (Cidago sıkma) Testi: Pozitif (+), hayvan sırtını aşağı esnetmeyi reddediyor."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi (Abomasosentez)",
                "keywords": ["ping", "liptak", "abomasosentez"],
                "content": "Sol veya sağ karın duvarında abomasal ping sesi YOKTUR. Liptak Testi: Negatif."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen ph", "rumen sivisi", "protozoa"],
                "content": "Rumen Sıvısı pH: 6.6 | Renk: Koyu yeşil | Koku: Normal | Protozoa hareketliliği azalmış."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Gram Boyama & Kültür",
                "keywords": ["gram", "boyama", "kultur", "bakteri", "perikardiyosentez", "trueperella"],
                "content": "Perikardiyosentez sıvısı kültüründe Trueperella pyogenes ve anaerobik koklar üredi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektor", "ferroskop", "metal", "hauptner", "miknatis"],
                "content": "Ferroskop Muayenesi: Retikulum / Sifoid kıkırdak bölgesi üzerinde Pozitif (+) şiddetli metalik sinyal ve ses reaksiyonu alındı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "plt"],
                "content": "Lökosit (WBC): 22.4 x10³/µL | Eritrosit (RBC): 5.4 x10⁶/µL | Hemoglobin (Hb): 9.8 g/dL | Hematokrit (PCV): %28 | MCV: 51.8 fL | MCH: 18.1 pg | MCHC: 35.0 g/dL | RDW: %16.8 | Plazma Fibrinojeni: 1250 mg/dL | Total Protein: 7.9 g/dL | PP/F Oranı: 6.3 | Trombosit (PLT): 410 x10³/µL | Nötrofil: %76 (Çomak: %22, Segmenteli: %54) | Lenfosit: %18 | Monosit: %4 | Eozinofil: %1 | Bazofil: %1."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "globulin", "troponin"],
                "content": "Albümin: 2.8 g/dL | Globülin: 5.1 g/dL | AST: 118 U/L | GGT: 24 U/L | ALT: 28 U/L | ALP: 92 U/L | CK: 160 U/L | LDH: 890 U/L | BUN: 28 mg/dL | Kreatinin: 1.2 mg/dL | Total Bilirubin: 0.8 mg/dL | BHBA: 0.9 mmol/L | Glikoz: 62 mg/dL | Kardiyak Troponin I (cTnI): 0.85 ng/mL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "sodyum", "potasyum", "klor", "na", "k", "cl", "glutaraldehit"],
                "content": "Kan pH: 7.32 | pO₂: 72 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 20.2 mmol/L | Baz Açığı (BE): -4.1 mmol/L | L-Laktat: 2.8 mmol/L | D-Laktat: 0.5 mmol/L | Na⁺: 134 mEq/L | K⁺: 4.2 mEq/L | Cl⁻: 98 mEq/L | Glutaraldehit Pıhtılaşma Süresi: 2.5 dakika."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg", "perikard", "retikulum", "fibrin"],
                "content": "Ultrasonografi: Perikardiyal boşlukta fibrin bantları, gaz ekojeniteleri ve 4 cm sıvı birikimi. Retikulum çevresinde hiperekojen yapışıklıklar ve fibrin kitleleri."
            }
        }
    },
    "Vaka E (Buzağı 'Kınalı')": {
        "kod": "VAKA_E",
        "sikayet": "10 günlük dişi buzağı. Sarı-yeşil sulu kötü kokulu ishal, emme refleksinin tamamen kaybolması, ayakta duramama, sarhoş ari yürüyüş (ataksi), stupor/koma hali.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen", "kulube", "hutch"],
                "content": "Bireysel buzağı kulübeleri (hutches). Dış ortam havadar ancak kulübe içi samanlar sulu dışkı ile bulaşık ve ıslak."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "sut", "mama", "kova", "litre", "emme"],
                "content": "Günde 2 öğün 2'şer litre açık kova sütü verilmektedir. Son 24 saatte sütü emmeyi tamamen reddetmiştir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil"],
                "content": "Ceyhan süt işletmesi buzağı büyütme ünitesi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "kolostrum", "agiz sutu", "oyku", "gecirdi", "once"],
                "content": "Doğumda kolostrum alma süresi 6 saati bulmuştur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "emme", "ataksi"],
                "content": "Vücut Sıcaklığı: 37.2 °C | Kalp Frekansı: 135 atım/dk | Solunum Frekansı: 52 nefes/dk | Mukoza: Soluk ve kuru | CRT: 3.5 saniye | Dehidrasyon: %10 | Göz Küresi Çöküklüğü: 6 mm çökmüş | Emme Refleksi: 0 (Tamamen yok), Palpebral refleks zayıflamış | Dışkı: Sarı-yeşil, sulu, fışkırır tarzda."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Oskültasyon Bulguları (Kalp & Akciğer & Bağırsak)",
                "keywords": ["kalp ses", "oskultasyon", "dinleme", "ufurum", "silpirti", "calkanti", "bagirsak", "akciger"],
                "content": "Kalp & Akciğer Oskültasyonu: Kalp sesleri ve solunum sesleri hızlı ve yüzeyel. Bağırsak Oskültasyonu: Hypermotil sulu çalkantı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "agri", "karin"],
                "content": "Karın bölgesine alt taraftan dokunulduğunda hassasiyet ve huzursuzluk."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesleri yok. Liptak testi uygulanmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen & Mide İçeriği",
                "keywords": ["rumen", "mide"],
                "content": "Buzağı henüz rumen gelişimi tamamlamamıştır (Ön mide inaktif)."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Dışkı ELISA & Etken Tespiti",
                "keywords": ["elisa", "diski", "rotavirus", "cryptosporidium", "e coli", "k99", "kultur"],
                "content": "Dışkı Hızlı ELISA / İmmünokromatografi Testi: Rotavirus Pozitif (+), Cryptosporidium parvum ookistleri Pozitif (+). E. coli K99 Negatif (-)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör Muayenesi",
                "keywords": ["dedektor", "ferroskop"],
                "content": "Uygulanmadı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "plt"],
                "content": "Lökosit (WBC): 12.4 x10³/µL | Eritrosit (RBC): 9.2 x10⁶/µL | Hemoglobin (Hb): 15.8 g/dL | Hematokrit (PCV): %48 | MCV: 52.1 fL | MCH: 17.1 pg | MCHC: 32.9 g/dL | RDW: %17.4 | Plazma Fibrinojeni: 480 mg/dL | Total Protein: 7.8 g/dL | PP/F Oranı: 16.2 | Trombosit (PLT): 340 x10³/µL | Nötrofil: %58 (Çomak: %8, Segmenteli: %50) | Lenfosit: %34 | Monosit: %5 | Eozinofil: %2 | Bazofil: %1."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "globulin", "glikoz"],
                "content": "Albümin: 3.2 g/dL | Globülin: 4.6 g/dL | AST: 85 U/L | GGT: 32 U/L | ALT: 28 U/L | ALP: 140 U/L | CK: 210 U/L | LDH: 920 U/L | BUN: 48 mg/dL | Kreatinin: 2.2 mg/dL | Total Bilirubin: 0.6 mg/dL | Glikoz: 45 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "d-laktat", "l-laktat", "sodyum", "potasyum", "klor", "na", "k", "cl"],
                "content": "Kan pH: 7.12 | pO₂: 78 mmHg | pCO₂: 32 mmHg | HCO₃⁻: 10.5 mmol/L | Baz Açığı (BE): -16.2 mmol/L | L-Laktat: 2.1 mmol/L | D-Laktat: 8.4 mmol/L | Na⁺: 129 mEq/L | K⁺: 6.4 mEq/L | Cl⁻: 102 mEq/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg", "bagirsak"],
                "content": "Abdominal USG: Bağırsak lümeninde sıvı genişlemesi ve atoni."
            }
        }
    },
    "Vaka F (Kuzu 'Torun')": {
        "kod": "VAKA_F",
        "sikayet": "3 günlük kuzu. Fışkırır tarzda sarımsı sulu ishal, yatar vaziyette doğrulama, soğuk ekstremiteler, komatöz yatış.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahir", "barinak", "durak", "havalandirma", "koku", "amonyak", "altlik", "temiz", "kirli", "islak", "yari acik", "kapali", "bagli", "serbest", "cevre", "paddock", "ortam", "hijyen", "agil", "koyun"],
                "content": "Geleneksel toprak zeminli kapalı koyun ağılı. Havasız, nemli, yoğun amonyak kokusu. Aşırı kirli ve dışkı birikintili altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "emme", "anne", "sut"],
                "content": "Annesini emme çabası var ancak ememiyor."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakim", "yayla", "nereden", "nereli", "yer", "sevk", "nakil"],
                "content": "Ceyhan koyunculuk tesisi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["gecmis", "onceden", "hastalik", "kolostrum", "ikiz", "oyku", "gecirdi", "once"],
                "content": "İkiz doğum, yetersiz kolostrum alma öyküsü."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ates", "sicaklik", "derece", "nabiz", "kalp frekans", "solunum", "nefes", "mukoza", "goz", "crt", "dolum", "dehidrasyon", "deri", "vital", "emme", "koma"],
                "content": "Vücut Sıcaklığı: 36.5 °C | Kalp Frekansı: 150 atım/dk | Solunum Frekansı: 60 nefes/dk | Mukoza: Siyanotik, Soğuk | CRT: 4.0 saniye | Dehidrasyon: %12 | Göz Küresi Çöküklüğü: 7 mm çökmüş | Emme Refleksi: 0 (Tamamen kaybolmuş) | Dışkı: Sarımsı sulu, fışkırır tarzda."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Oskültasyon Bulguları (Kalp & Akciğer & Bağırsak)",
                "keywords": ["kalp ses", "oskultasyon", "dinleme", "ufurum", "silpirti", "calkanti", "akciger"],
                "content": "Kalp Oskültasyonu: Taşikardik ve zayıf düştü sesleri. Akciğer Oskültasyonu: Solunum sesleri sertleşmiş."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "agri"],
                "content": "Yanıt yok (Komatöz yatış)."
            },
            "PING_LIPTAK": {
                "name": "Ping Sesi & Liptak Testi",
                "keywords": ["ping", "liptak"],
                "content": "Uygulanmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen & Mide İçeriği",
                "keywords": ["rumen", "mide"],
                "content": "Ön mide inaktif."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Dışkı ELISA & Etken Tespiti",
                "keywords": ["elisa", "diski", "etec", "k99", "rotavirus", "coronavirus", "kultur"],
                "content": "Dışkı ETEC K99 Antijen Testi: Pozitif (+). Rotavirus / Coronavirus Negatif (-)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör Muayenesi",
                "keywords": ["dedektor", "ferroskop"],
                "content": "Uygulanmadı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lokosit", "kan sayim", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "notrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "plt"],
                "content": "Lökosit (WBC): 16.8 x10³/µL | Eritrosit (RBC): 10.5 x10⁶/µL | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %54 | MCV: 51.4 fL | MCH: 16.3 pg | MCHC: 31.8 g/dL | RDW: %18.8 | Plazma Fibrinojeni: 520 mg/dL | Total Protein: 8.6 g/dL | PP/F Oranı: 16.5 | Trombosit (PLT): 290 x10³/µL | Nötrofil: %66 (Çomak: %14, Segmenteli: %52) | Lenfosit: %28 | Monosit: %4 | Eozinofil: %1 | Bazofil: %1."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "ure", "bun", "kreatinin", "bilirubin", "albumin", "globulin", "glikoz"],
                "content": "Albümin: 3.4 g/dL | Globülin: 5.2 g/dL | AST: 110 U/L | GGT: 38 U/L | ALT: 35 U/L | ALP: 165 U/L | CK: 290 U/L | LDH: 1100 U/L | BUN: 62 mg/dL | Kreatinin: 3.1 mg/dL | Glikoz: 28 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Elektrolitler",
                "keywords": ["kan gazi", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz acigi", "be", "laktat", "d-laktat", "l-laktat", "sodyum", "potasyum", "klor", "na", "k", "cl"],
                "content": "Kan pH: 7.04 | pO₂: 70 mmHg | pCO₂: 28 mmHg | HCO₃⁻: 7.2 mmol/L | Baz Açığı (BE): -21.5 mmol/L | L-Laktat: 6.2 mmol/L | D-Laktat: 1.8 mmol/L | Na⁺: 124 mEq/L | K⁺: 7.2 mEq/L | Cl⁻: 95 mEq/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg"],
                "content": "Uygulanmadı."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Sindirim ve Metabolizma Sistemleri Akıllı Anamnez & Bulgu Sorgulama Konsolu</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde hazır şıklar veya butonlar <u>yoktur</u>. 
        Klinik şüphenize göre öğrenmek istediğiniz muayene, lab veya ortam detayını <b>kendi cümlelerinizle veya anahtar kelimelerinizle</b> yazınız 
        (Örn: <i>"Ahır havalandırması nasıl?"</i>, <i>"Rasyonda ne kadar mısır veriliyor?"</i>, <i>"Rumen pH'sı kaç?"</i>, <i>"Liptak testi pozitif mi?"</i>, <i>"Ping sesi nereden geliyor?"</i>, <i>"Kan gazı ve laktat değerleri"</i>, <i>"Tam hemogram"</i>).
    </div>
""", unsafe_allow_html=True)

# Sidebar Password Portal for Instructors
with st.sidebar:
    st.markdown("### 🔑 Eğitmen Portalı")
    pass_input = st.text_input("Eğitmen Parolası:", type="password", key="pwd_input")
    is_instructor = (pass_input == "vet401")
    if is_instructor:
        st.success("Eğitmen Modu Aktif! Seçilen vakanın tüm verileri görünür yapıldı.")

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

active_case = CASES[selected_case_name]

st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case['sikayet']}")

# Session State for Questions History
if "history" not in st.session_state:
    st.session_state.history = {}

if selected_case_name not in st.session_state.history:
    st.session_state.history[selected_case_name] = []

# Query Matcher Algorithm
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

# Instructor full view mode
if is_instructor:
    st.markdown("---")
    st.markdown("### 🔓 Vakanın Tüm Muayene ve Laboratuvar Kartları (Eğitmen Görünümü):")
    for c_key, c_val in active_case["categories"].items():
        st.markdown(f"""
            <div class='card-found'>
                <span class='badge-category'>{c_val['name']}</span>
                <div class='card-title' style='margin-top:6px;'>{c_val['name']}</div>
                <div class='card-content'>{c_val['content']}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    # Student Query Interface
    st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")
    
    col_input, col_button = st.columns([4, 1])
    
    with col_input:
        user_query = st.text_input(
            "Sorunuzu Buraya Yazınız (Örn: Rasyon bilgisi?, Ahır şartları?, Rumen pH'sı?, Ping var mı?):",
            key="query_input"
        )
        
    with col_button:
        st.write("") # spacing
        st.write("") 
        submit_btn = st.button("🔍 Sorgula", use_container_width=True)
        
    if submit_btn and user_query:
        found_keys = match_query(user_query, active_case["categories"])
        
        if found_keys:
            st.session_state.history[selected_case_name].append({
                "query": user_query,
                "found": found_keys,
                "status": "success"
            })
        else:
            st.session_state.history[selected_case_name].append({
                "query": user_query,
                "found": [],
                "status": "not_found"
            })
            
    # Display History
    if st.session_state.history[selected_case_name]:
        st.markdown("---")
        st.markdown("### 📑 Sorgulama Geçmişiniz ve Elde Edilen Bulgular:")
        
        for item in reversed(st.session_state.history[selected_case_name]):
            if item["status"] == "success":
                st.markdown(f"**❓ Sorduğunuz Soru:** *\"{item['query']}\"*")
                for fk in item["found"]:
                    cat_data = active_case["categories"][fk]
                    st.markdown(f"""
                        <div class='card-found'>
                            <span class='badge-category'>{cat_data['name']}</span>
                            <div class='card-title' style='margin-top:6px;'>{cat_data['name']}</div>
                            <div class='card-content'>{cat_data['content']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"**❓ Sorduğunuz Soru:** *\"{item['query']}\"*")
                st.warning("⚠️ Bu arama terimiyle ilişkili spesifik bir klinik bulgu saptanamadı. Lütfen farklı kelimelerle tekrar deneyiniz (Örn: 'ahır', 'rasyon', 'vital', 'rumen ph', 'liptak', 'ping', 'hemogram', 'kan gazı').")
