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
    "Vaka A (Sığır 'Nisa')": {
        "kod": "VAKA_A",
        "sikayet": "Doğum sonrası süt verimi artınca rasyona arpa/mısır kırması ilave edilmiş; son 24 saattir tam iştahsızlık, şiddetli durgunluk, ekşi sulu ishal ve yatma eğilimi.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "yoğun", "süt yemi", "kırma", "miktar", "kg", "kilo"],
                "content": "Doğum sonrası süt verimindeki hızlı artış üzerine rasyondaki yoğun yem (arpa/mısır kırması) miktarı aniden artırılmıştır. Günlük verilen yem miktarları: 14 kg mısır silajı, 3 kg buğday samanı ve 12 kg yoğun süt yemi (arpa/mısır kırması)."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova"],
                "content": "Ceyhan ovasındaki sabit süt sığırcılığı tesisinde doğup büyümüştür. Herhangi bir yayla veya yükseklik nakli öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce", "doğum"],
                "content": "2 hafta önce sorunsuz doğum yapmıştır. Geçmişinde kronik sistemik veya metabolik hastalık kaydı yoktur."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "yarı açık", "kapalı", "bağlı", "serbest", "çevre", "paddock", "ortam", "hijyen"],
                "content": "Kapalı beton zeminli bağlı ahır. Yetersiz havalandırma, basık amonyak kokusu. Ekşi sulu ishale bağlı kirli ve ıslak saman altlık."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "deri", "vital", "çökük"],
                "content": "Vücut Sıcaklığı: 38.1 °C | Kalp Frekansı: 104 atım/dk | Solunum Frekansı: 40 nefes/dk | Mukoza: Hiperemik / Soluk | CRT: 3.5 saniye | Dehidrasyon: %8 | Göz küresi: 4 mm çökük | Rumen Motilitesi: 0 / 2 dk (Atonik) | Dışkı: Sık, ekşi kokulu sulu ishal."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp, Akciğer & Rumen Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer", "ping", "çınlama"],
                "content": "Kalp Oskültasyonu: Taşikardik, üfürüm veya çalkantı sesi yok. Akciğer Oskültasyonu: Sert veziküler solunum sesleri. Rumen Oskültasyonu: Sol dorsal rumende gaz birikimine bağlı hafif çınlama sesi var ancak abomasal ping yok."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "hassasiyet", "inleme"],
                "content": "Sopa testi, kama testi ve Withers pinch (cidago sıkma) ağrı testlerinin tamamı Negatif (-)."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal", "hauptner", "mıknatıs", "yabancı cisim"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Negatif (-), retikulum veya ön karın bölgesinde metalik sinyal saptanmadı."
            },
            "LIPTAK_TESTI": {
                "name": "Liptak Testi (Abomasosentez)",
                "keywords": ["liptak", "abomasosentez", "iğne", "karın delme"],
                "content": "Liptak Testi: Sol alt karın duvarından sıvı ponksiyonunda abomasal sıvı çekilemedi (pH > 6.0, yeşilimsi rumen sıvısı girmekte)."
            },
            "GLUTARALDEHIT_TESTI": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma", "jelleşme", "çökelme"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 dakika (Negatif)."
            },
            "RUMEN_SIVISI_ANALIZI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen sıvısı", "ponksiyon", "ph", "renk", "koku", "protozoa", "mikroskopi"],
                "content": "Rumen Sıvısı Ponksiyonu: pH: 4.6 | Renk: Sütümsü-sarımsı | Koku: Ekşi laktik asit kokusu | Kıvam: Sulu, mikro-viskoz | Canlı Protozoa Sayısı: 0 / HPF (Mikroskobide protozoon saptanmadı)."
            },
            "MIKROBIYOLOJI_GRAM": {
                "name": "Gram Boyama & Mikrobiyoloji",
                "keywords": ["gram", "boyama", "kültür", "bakteri", "lactobacillus", "streptococcus"],
                "content": "Rumen Sıvısı Gram Boyama: Gram-pozitif rod ve koklar (Lactobacillus spp., Streptococcus bovis) hakim. Gram-negatif flora kaybolmuş."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt", "trombosit"],
                "content": "Lökosit (WBC): 14.2 x10³/µL | Eritrosit (RBC): 8.8 x10⁶/µL | Hemoglobin (Hb): 15.4 g/dL | Hematokrit (PCV): %46 | MCV: 52.3 fL | MCH: 17.5 pg | MCHC: 33.5 g/dL | RDW: %16.8 | Plazma Fibrinojeni: 380 mg/dL | Total Protein: 8.6 g/dL | PP/F Oranı: 22.6 | Trombosit (PLT): 340 x10³/µL | Segmenteli Nötrofil: %58 | Çomak Nötrofil: %6 | Lenfosit: %30 | Monosit: %4 | Eozinofil: %2 | Bazofil: %0."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "troponin", "glikoz", "bhba"],
                "content": "Albümin: 3.8 g/dL | Globülin: 4.8 g/dL | AST: 112 U/L | GGT: 32 U/L | ALT: 28 U/L | ALP: 92 U/L | CK: 165 U/L | LDH: 840 U/L | BUN: 38 mg/dL | Kreatinin: 1.8 mg/dL | Glikoz: 42 mg/dL | BHBA: 1.4 mmol/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "oksijen", "d-laktat", "sodyum", "potasyum", "klor"],
                "content": "Kan pH: 7.18 | pO₂: 64 mmHg | pCO₂: 34 mmHg | HCO₃⁻: 12.4 mmol/L | Baz Açığı (BE): -14.2 mmol/L | L-Laktat: 6.8 mmol/L | D-Laktat: 5.4 mmol/L | Na⁺: 132 mEq/L | K⁺: 5.6 mEq/L | Cl⁻: 96 mEq/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Ultrasonografi",
                "keywords": ["ultrason", "usg", "röntgen", "görüntüleme"],
                "content": "Abdominal Ultrasonografi: Rumen içeriği tamamen sıvılaşmış ve gaz tabakası genişlemiş. Perikardiyum, abomasum ve karaciğer parankimi normal."
            }
        }
    },
    "Vaka B (Sığır 'Maviş')": {
        "kod": "VAKA_B",
        "sikayet": "Doğum sonrası iştahsızlık, sol paralumbar fossada çökme, dışkı miktarında azalma ve süt veriminde belirgin düşüş.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "süt yemi", "kg", "kilo"],
                "content": "Doğum sonrası rasyonda kaba yem oranı yüksek tutulmuş ancak iştahsızlık nedeniyle tüketim düşmüştür. Günlük verilen yem miktarları: 10 kg alfalfa otu, 4 kg buğday samanı, 4 kg süt yemi."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Sabit süt işletmesinde barındırılmaktadır. Rakım nakli yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "doğum"],
                "content": "3 hafta önce sorunsuz doğum yapmıştır. Son 5 gündür aralıklı iştahsızlık ve süt veriminde yarı yarıya düşüş vardır."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "yarı açık", "kapalı", "bağlı", "serbest", "ortam"],
                "content": "Yarı açık serbest duraklı (free-stall) kauçuk yataklı modern ahır. Havadar, kokusuz. Temiz ve kuru duraklar."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "vital"],
                "content": "Vücut Sıcaklığı: 38.5 °C | Kalp Frekansı: 78 atım/dk | Solunum Frekansı: 24 nefes/dk | Mukoza: Pembe | CRT: 2.0 saniye | Dehidrasyon: %4 | Göz küresi: Normal | Sol paralumbar fossa çökmüş, rumen motilitesi 1 / 2 dk (zayıf)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp, Akciğer & Rumen Oskültasyonu (Ping Sesi)",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk", "rall", "akciğer", "ping", "çınlama", "steel band"],
                "content": "Kalp Oskültasyonu: Normal ritim ve ses şiddeti, üfürüm yok. Akciğer Oskültasyonu: Veziküler solunum sesleri normal. Sol Oskültasyon-Perküsyon: Sol 8-12. interkostal aralıkta paralumbar fossa hattında yüksek frekanslı meşhur çelik boru çınlaması / metalik ping sesi (steel band sound) duyulmaktadır."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa, kama ve cidago sıkma ağrı testleri Negatif (-)."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal", "hauptner", "mıknatıs"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Negatif (-), retikulum veya ön karın bölgesinde metalik sinyal saptanmadı."
            },
            "LIPTAK_TESTI": {
                "name": "Liptak Testi (Abomasosentez)",
                "keywords": ["liptak", "abomasosentez", "iğne", "karın delme"],
                "content": "Liptak Testi: Sol 9. interkostal aralıkta ping alınan noktanın altından yapılan ponksiyonda pembemsi-kahverengi berrak sıvı çekildi. Sıvı pH: 3.1 (Abomasum sıvısı)."
            },
            "GLUTARALDEHIT_TESTI": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma", "jelleşme"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 dakika (Negatif)."
            },
            "RUMEN_SIVISI_ANALIZI": {
                "name": "Abomasum / Rumen Sıvısı Analizi",
                "keywords": ["rumen sıvısı", "abomasum sıvısı", "ponksiyon", "ph"],
                "content": "Abomasal Sıvı Analizi: pH: 3.1 | Renk: Berrak pembemsi-kahverengi | Odor: Ekşimsi abomasal koku | Protozoon: Yok."
            },
            "MIKROBIYOLOJI_GRAM": {
                "name": "Gram Boyama & Mikrobiyoloji",
                "keywords": ["gram", "boyama", "kültür", "bakteri"],
                "content": "Abomasal ve Kan Kültürü: Bakteriyel üreme yok (Steril)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt"],
                "content": "Lökosit (WBC): 6.8 x10³/µL | Eritrosit (RBC): 6.2 x10⁶/µL | Hemoglobin (Hb): 11.2 g/dL | Hematokrit (PCV): %32 | MCV: 51.6 fL | MCH: 18.0 pg | MCHC: 35.0 g/dL | RDW: %14.2 | Plazma Fibrinojeni: 310 mg/dL | Total Protein: 7.2 g/dL | PP/F Oranı: 23.2 | Trombosit (PLT): 280 x10³/µL | Segmenteli Nötrofil: %48 | Çomak Nötrofil: %1 | Lenfosit: %45 | Monosit: %4 | Eozinofil: %2 | Bazofil: %0."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "glikoz", "bhba"],
                "content": "Albümin: 3.3 g/dL | Globülin: 3.9 g/dL | AST: 62 U/L | GGT: 22 U/L | ALT: 18 U/L | ALP: 74 U/L | CK: 95 U/L | LDH: 480 U/L | BUN: 16 mg/dL | Kreatinin: 1.0 mg/dL | Glikoz: 54 mg/dL | BHBA: 2.1 mmol/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "sodyum", "potasyum", "klor"],
                "content": "Kan pH: 7.48 | pO₂: 78 mmHg | pCO₂: 46 mmHg | HCO₃⁻: 34.2 mmol/L | Baz Açığı (BE): +9.5 mmol/L | L-Laktat: 1.2 mmol/L | D-Laktat: 0.4 mmol/L | Na⁺: 138 mEq/L | K⁺: 3.1 mEq/L | Cl⁻: 88 mEq/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Ultrasonografi",
                "keywords": ["ultrason", "usg", "röntgen"],
                "content": "Sol Torako-Abdominal USG: Sol karın duvarı ile rumen arasında gaz ve sıvı içerikli genişlemiş abomasum lümeni tespiti."
            }
        }
    },
    "Vaka C (Sığır 'Pamuk')": {
        "kod": "VAKA_C",
        "sikayet": "Sağ karın bölgesinde aniden başlayan şiddetli şişkinlik, huzursuzluk, karnına bakma, ıkınma, tam iştahsızlık ve dışkılayamama.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "kg", "kilo"],
                "content": "Doğum sonrası yüksek enerjili süt rasyonu verilmektedir. Günlük verilen yem miktarları: 12 kg mısır silajı, 2 kg yonca otu, 9 kg süt yemi."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Sabit süt tesisi. Nakil geçmişi yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "doğum"],
                "content": "4 hafta önce doğum yapmıştır. Son 24 saattir aniden başlayan şiddetli huzursuzluk, karnına bakma, ıkınma, tam iştahsızlık ve süt veriminin sıfırlanması."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "kapalı", "ortam"],
                "content": "Kapalı duraklı ahır. Pencereler yetersiz, amonyak/dışkı kokusu yüksek. Kısmen kirli ve gübreli altlık."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "vital", "dışkı"],
                "content": "Vücut Sıcaklığı: 37.6 °C | Kalp Frekansı: 118 atım/dk | Solunum Frekansı: 48 nefes/dk | Mukoza: Soluk ve siyanotik | CRT: 4.0 saniye | Dehidrasyon: %10 | Göz küresi: 6 mm çökmüş | Dışkı: Dışkılama yok (zift gibi mukuslu az miktar dışkı), Rektal muayenede sağda gergin kitle."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp, Akciğer & Rumen Oskültasyonu (Ping Sesi)",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk", "rall", "akciğer", "ping", "çınlama"],
                "content": "Kalp Oskültasyonu: Şiddetli taşikardi, zayıf vuruşlar. Akciğer Oskültasyonu: Yüzeksel hızlı solunum. Sağ Oskültasyon-Perküsyon: Sağ 8-13. interkostal aralıklar ve paralumbar fossa alanında geniş alana yayılan çok şiddetli metalik ping sesi duyulmaktadır."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa ve kama testleri Negatif (-), ancak sağ karın palpasyaonunda şiddetli ağrı reaksiyonu."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal", "hauptner"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Negatif (-), retikulumda metal sinyali yok."
            },
            "LIPTAK_TESTI": {
                "name": "Liptak Testi (Abomasosentez)",
                "keywords": ["liptak", "abomasosentez", "iğne", "karın delme"],
                "content": "Liptak Testi: Sağ 10. interkostal aralıktan ponksiyonda kanlı-koyu kahverengi sıvı çekildi. Sıvı pH: 2.4."
            },
            "GLUTARALDEHIT_TESTI": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma", "jelleşme"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 dakika (Negatif)."
            },
            "RUMEN_SIVISI_ANALIZI": {
                "name": "Abomasal Sıvı Analizi",
                "keywords": ["rumen sıvısı", "abomasum sıvısı", "ponksiyon", "ph"],
                "content": "Abomasal Sıvı Analizi: pH: 2.4 | Renk: Kanlı koyu kahverengi | Odor: Hemorajik nekrotik koku."
            },
            "MIKROBIYOLOJI_GRAM": {
                "name": "Gram Boyama & Mikrobiyoloji",
                "keywords": ["gram", "boyama", "kültür", "bakteri"],
                "content": "Ponksiyon sıvısı bakteriyolojik kültür: Üreme yok (Steril)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt"],
                "content": "Lökosit (WBC): 18.6 x10³/µL | Eritrosit (RBC): 9.2 x10⁶/µL | Hemoglobin (Hb): 16.8 g/dL | Hematokrit (PCV): %50 | MCV: 54.3 fL | MCH: 18.2 pg | MCHC: 33.6 g/dL | RDW: %17.1 | Plazma Fibrinojeni: 420 mg/dL | Total Protein: 9.2 g/dL | PP/F Oranı: 21.9 | Trombosit (PLT): 390 x10³/µL | Segmenteli Nötrofil: %68 | Çomak Nötrofil: %8 | Lenfosit: %20 | Monosit: %3 | Eozinofil: %1 | Bazofil: %0."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "glikoz", "bhba"],
                "content": "Albümin: 4.1 g/dL | Globülin: 5.1 g/dL | AST: 185 U/L | GGT: 45 U/L | ALT: 34 U/L | ALP: 110 U/L | CK: 420 U/L | LDH: 1250 U/L | BUN: 54 mg/dL | Kreatinin: 2.6 mg/dL | Glikoz: 115 mg/dL | BHBA: 1.8 mmol/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "sodyum", "potasyum", "klor"],
                "content": "Kan pH: 7.15 | pO₂: 58 mmHg | pCO₂: 30 mmHg | HCO₃⁻: 10.2 mmol/L | Baz Açığı (BE): -16.8 mmol/L | L-Laktat: 9.4 mmol/L | D-Laktat: 1.1 mmol/L | Na⁺: 130 mEq/L | K⁺: 2.8 mEq/L | Cl⁻: 76 mEq/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Ultrasonografi",
                "keywords": ["ultrason", "usg", "röntgen"],
                "content": "Sağ Abdominal USG: Abomasum duvarında 14 mm ödem/kalınlaşma, lümende gaz-sıvı seviyelenmesi ve abdominal effüzyon."
            }
        }
    },
    "Vaka D (Sığır 'Efe')": {
        "kod": "VAKA_D",
        "sikayet": "Dirsekleri dışa açarak durma, kambur duruş, inleme, gerdanda hamur ödemi ve kalpten su çalkantısı sesi gelmesi.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kg", "kilo"],
                "content": "Entansif besi rasyonu ile beslenmektedir. Paket balya parçalama esnasında inşaat teli ve çivi atıkları karışmış olabileceği bildirilmektedir. Günlük verilen yem miktarları: 8 kg kuru ot, 2 kg saman, 8 kg besi yemi."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Ceyhan ovası sabit besi işletmesi. Rakım değişikliği yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü"],
                "content": "Geçmişte kronik hastalık kaydı yoktur. Son 3 gündür dirsekleri dışa açarak durma, kambur duruş, inleme ve iştahsızlık."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "yarı kapalı", "bağlı", "ortam"],
                "content": "Yarı kapalı eski beton zeminli bağlı ahır. Çevre padoğunda balya telleri ve inşaat atıkları mevcut. Rutin amonyak kokulu, kirli ıslak altlık."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "vital", "ödem"],
                "content": "Vücut Sıcaklığı: 39.9 °C | Kalp Frekansı: 106 atım/dk | Solunum Frekansı: 44 nefes/dk | Mukoza: Soluk pembe | CRT: 3.0 saniye | Dehidrasyon: %6 | Göz küresi: 2 mm çökük | Gerdan ve submandibuler bölgede soğuk hamur kıvamında ödem | Vena jugularis stazı +, yalancı nabız +."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp, Akciğer & Rumen Oskültasyonu (Su Çalkantısı)",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk", "rall", "akciğer", "ping"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri duyuluyor. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri hafif azalmış. Rumen Oskültasyonu: Rumen hareketleri 0 / 2 dk (hipomotil/atonik). Abomasal ping sesi YOKTUR."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "inleme"],
                "content": "Sopa testi Pozitif (+), Kama testi Pozitif (+), Withers pinch (cidago sıkma) testi Pozitif (+). Hayvan esnememekte ve inlemektedir."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal", "hauptner", "mıknatıs"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Retikulum / Sifoid kıkırdak bölgesi üzerinde Pozitif (+) şiddetli metalik sinyal ve ses reaksiyonu alındı."
            },
            "LIPTAK_TESTI": {
                "name": "Liptak Testi (Abomasosentez)",
                "keywords": ["liptak", "abomasosentez", "iğne"],
                "content": "Liptak Testi: Negatif / Sıvı çekilemedi (Abomasum deplasmanı yoktur)."
            },
            "GLUTARALDEHIT_TESTI": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma", "jelleşme"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: 2.2 dakika (Şiddetli Akut Pozitif Jelleşme)."
            },
            "RUMEN_SIVISI_ANALIZI": {
                "name": "Perikardiyosentez / Rumen Sıvısı Analizi",
                "keywords": ["rumen sıvısı", "perikardiyosentez", "ponksiyon", "eksuda"],
                "content": "Perikardiyosentez Sıvısı: Kirli sarı-yeşil renkli, pis fötid kokulu pürülan eksuda. Sıvı Lökosit: 85.000 /µL, Protein: 5.8 g/dL."
            },
            "MIKROBIYOLOJI_GRAM": {
                "name": "Gram Boyama & Mikrobiyoloji",
                "keywords": ["gram", "boyama", "kültür", "bakteri", "trueperella"],
                "content": "Perikard Sıvısı Kültürü: Trueperella pyogenes ve anaerobik Gram-negatif basiller üredi."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt"],
                "content": "Lökosit (WBC): 24.8 x10³/µL | Eritrosit (RBC): 5.2 x10⁶/µL | Hemoglobin (Hb): 9.8 g/dL | Hematokrit (PCV): %27 | MCV: 51.9 fL | MCH: 18.8 pg | MCHC: 36.2 g/dL | RDW: %15.8 | Plazma Fibrinojeni: 1350 mg/dL | Total Protein: 8.9 g/dL | PP/F Oranı: 6.59 | Trombosit (PLT): 410 x10³/µL | Segmenteli Nötrofil: %62 | Çomak Nötrofil: %12 | Lenfosit: %20 | Monosit: %5 | Eozinofil: %1 | Bazofil: %0."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "troponin", "glikoz", "bhba"],
                "content": "Albümin: 2.4 g/dL | Globülin: 6.5 g/dL | AST: 135 U/L | GGT: 28 U/L | ALT: 22 U/L | ALP: 88 U/L | CK: 180 U/L | LDH: 920 U/L | BUN: 32 mg/dL | Kreatinin: 1.4 mg/dL | Glikoz: 62 mg/dL | BHBA: 0.8 mmol/L | Kardiyak Troponin I (cTnI): 0.95 ng/mL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "sodyum", "potasyum", "klor"],
                "content": "Kan pH: 7.31 | pO₂: 70 mmHg | pCO₂: 46 mmHg | HCO₃⁻: 19.8 mmol/L | Baz Açığı (BE): -4.8 mmol/L | L-Laktat: 3.2 mmol/L | D-Laktat: 0.5 mmol/L | Na⁺: 136 mEq/L | K⁺: 4.2 mEq/L | Cl⁻: 98 mEq/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Ultrasonografi",
                "keywords": ["ultrason", "usg", "röntgen"],
                "content": "Kardiyak & Retiküler USG: Perikardiyal kesede 4.5 cm kalınlığında fibrin bantları ve hiperekojen gaz birikimi. Retikulum çevresinde hiperekojen yapışıklıklar."
            }
        }
    },
    "Vaka E (Buzağı 'Kınalı')": {
        "kod": "VAKA_E",
        "sikayet": "Sarımsı sulu ishal, emme isteğinde azalma, ayakta durmakta zorlanma (ataksi), sarhoş yürüyüşü ve koma hali.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "süt", "mama", "buzağı", "öğün", "litre", "kg"],
                "content": "12 günlük Simental ırkı erkek buzağı. Besleme: Günde 2 öğün 2'şer litre ılık süt."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "coğrafya"],
                "content": "Ceyhan doğum tesisi buzağı bölmesi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "doğum", "kolostrum"],
                "content": "Doğumda kolostrum içirilmiştir. Son 3 gündür sarımsı sulu ishal ve emme isteksizliği başlamıştır."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "kulübe", "ortam"],
                "content": "Bireysel buzağı kulübeleri (hutches). Dış ortam havadar ancak kulübe içi samanlar sulu dışkı ile bulaşık ve ıslak."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "vital", "emme", "ataksi"],
                "content": "Vücut Sıcaklığı: 37.8 °C | Kalp Frekansı: 132 atım/dk | Solunum Frekansı: 48 nefes/dk | Mukoza: Soluk ve kuru | CRT: 3.5 saniye | Dehidrasyon: %9 | Göz küresi: 5 mm çökmüş | Emme refleksi: Kaybolmuş (Zayıf/Yok) | Nörolojik Durum: Ataksi, stupor, palpebral refleks yavaşlamış."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer & Karın Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "akciğer", "ping"],
                "content": "Kalp Oskültasyonu: Taşikardik. Akciğer Oskültasyonu: Temiz. Karın Oskültasyonu: Bağırsak motilitesi aşırı artmış (hipermotil su sesleri). Ping sesi yok."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı"],
                "content": "Uygulanmadı / Negatif."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal"],
                "content": "Uygulanmadı / Negatif."
            },
            "LIPTAK_TESTI": {
                "name": "Liptak Testi (Abomasosentez)",
                "keywords": ["liptak", "abomasosentez"],
                "content": "Uygulanmadı / Negatif."
            },
            "GLUTARALDEHIT_TESTI": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 dakika (Negatif)."
            },
            "RUMEN_SIVISI_ANALIZI": {
                "name": "Dışkı Muayenesi & Mikroskopik İnceleme",
                "keywords": ["dışkı", "mikroskop", "cryptosporidium", "ookist"],
                "content": "Dışkı Fiziksel: Sarımsı sulu, mukuslu, kötü kokulu. Dışkı Mikroskopisi (Acid-Fast Boyama): Cryptosporidium parvum ookistleri (4-5 µm pembe küreler) görüldü."
            },
            "MIKROBIYOLOJI_GRAM": {
                "name": "Dışkı Hızlı Antigen ELISA / PCR Kit",
                "keywords": ["elisa", "pcr", "kit", "rotavirus", "cryptosporidium", "e. coli"],
                "content": "Dışkı Antigen ELISA Testi: Rotavirus Pozitif (+), Cryptosporidium parvum Pozitif (+), E. coli K99 Negatif (-), Coronavirus Negatif (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt"],
                "content": "Lökosit (WBC): 11.4 x10³/µL | Eritrosit (RBC): 9.8 x10⁶/µL | Hemoglobin (Hb): 15.8 g/dL | Hematokrit (PCV): %48 | MCV: 48.9 fL | MCH: 16.1 pg | MCHC: 32.9 g/dL | RDW: %16.2 | Plazma Fibrinojeni: 340 mg/dL | Total Protein: 7.8 g/dL | PP/F Oranı: 22.9 | Trombosit (PLT): 320 x10³/µL | Segmenteli Nötrofil: %52 | Çomak Nötrofil: %2 | Lenfosit: %40 | Monosit: %4 | Eozinofil: %2 | Bazofil: %0."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "glikoz", "bhba"],
                "content": "Albümin: 3.6 g/dL | Globülin: 4.2 g/dL | AST: 48 U/L | GGT: 28 U/L | ALT: 16 U/L | ALP: 140 U/L | CK: 110 U/L | LDH: 520 U/L | BUN: 46 mg/dL | Kreatinin: 2.1 mg/dL | Glikoz: 48 mg/dL | BHBA: 0.4 mmol/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "d-laktat", "sodyum", "potasyum", "klor"],
                "content": "Kan pH: 7.12 | pO₂: 68 mmHg | pCO₂: 32 mmHg | HCO₃⁻: 10.4 mmol/L | Baz Açığı (BE): -16.2 mmol/L | L-Laktat: 2.4 mmol/L | D-Laktat: 7.8 mmol/L | Na⁺: 130 mEq/L | K⁺: 6.2 mEq/L | Cl⁻: 104 mEq/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Ultrasonografi",
                "keywords": ["ultrason", "usg"],
                "content": "Abdominal USG: Sıvı dolu ince bağırsak lümenleri, periton sıvısı yok."
            }
        }
    },
    "Vaka F (Kuzu 'Torun')": {
        "kod": "VAKA_F",
        "sikayet": "Aniden başlayan şeffaf bol sulu ishal, yutkunma ve emme refleksinin tamamen durması, koma ve soğuk ekstremiteler.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "süt", "kuzu", "ağız sütü", "kolostrum"],
                "content": "3 günlük İle de France ırkı dişi kuzu. İkiz doğum. Besleme: Anne sütü emmeye çalışmaktadır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "coğrafya"],
                "content": "Ceyhan koyunculuk tesisi ağılı."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "doğum"],
                "content": "Doğum sonrası ilk 12 saat normal emmiş, son 12 saattir aniden başlayan bol sulu ishal krizine girmiştir."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "ağıl", "toprak", "ortam"],
                "content": "Geleneksel toprak zeminli kapalı koyun ağılı. Havasız, nemli, yoğun amonyak kokusu. Aşırı kirli ve dışkı birikintili altlık."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "vital", "emme", "koma"],
                "content": "Vücut Sıcaklığı: 36.8 °C | Kalp Frekansı: 160 atım/dk | Solunum Frekansı: 60 nefes/dk | Mukoza: Siyanotik ve soğuk | CRT: 4.5 saniye | Dehidrasyon: %11 | Göz küresi: 7 mm çökmüş | Emme refleksi: Tamamen yok (0)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer & Karın Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "akciğer", "ping"],
                "content": "Kalp Oskültasyonu: Şiddetli taşikardi, aritmik vuruşlar (Hiperkalemik dalgalar). Akciğer Oskültasyonu: Yüzeyel. Karın Oskültasyonu: Bağırsaklarda bol sulu çalkantı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı"],
                "content": "Uygulanmadı / Negatif."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal"],
                "content": "Uygulanmadı / Negatif."
            },
            "LIPTAK_TESTI": {
                "name": "Liptak Testi (Abomasosentez)",
                "keywords": ["liptak", "abomasosentez"],
                "content": "Uygulanmadı / Negatif."
            },
            "GLUTARALDEHIT_TESTI": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Süresi: > 15 dakika (Negatif)."
            },
            "RUMEN_SIVISI_ANALIZI": {
                "name": "Dışkı Muayenesi & Mikroskopik İnceleme",
                "keywords": ["dışkı", "mikroskop"],
                "content": "Dışkı Fiziksel: Şeffaf-sarımsı bol sulu sekretuar ishal."
            },
            "MIKROBIYOLOJI_GRAM": {
                "name": "Dışkı Antigen ELISA / PCR Kit",
                "keywords": ["elisa", "pcr", "kit", "etec", "e. coli"],
                "content": "Dışkı Antigen ELISA / PCR: ETEC E. coli K99 (F5) Pozitif (+), Rotavirus Negatif (-), Cryptosporidium Negatif (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt"],
                "content": "Lökosit (WBC): 16.8 x10³/µL | Eritrosit (RBC): 10.4 x10⁶/µL | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %52 | MCV: 46.2 fL | MCH: 15.8 pg | MCHC: 33.1 g/dL | RDW: %17.5 | Plazma Fibrinojeni: 380 mg/dL | Total Protein: 8.4 g/dL | PP/F Oranı: 22.1 | Trombosit (PLT): 340 x10³/µL | Segmenteli Nötrofil: %64 | Çomak Nötrofil: %4 | Lenfosit: %28 | Monosit: %3 | Eozinofil: %1 | Bazofil: %0."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "glikoz", "bhba"],
                "content": "Albümin: 3.9 g/dL | Globülin: 4.5 g/dL | AST: 54 U/L | GGT: 32 U/L | ALT: 20 U/L | ALP: 160 U/L | CK: 210 U/L | LDH: 680 U/L | BUN: 58 mg/dL | Kreatinin: 2.8 mg/dL | Glikoz: 32 mg/dL | BHBA: 0.3 mmol/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "sodyum", "potasyum", "klor"],
                "content": "Kan pH: 6.98 | pO₂: 54 mmHg | pCO₂: 28 mmHg | HCO₃⁻: 6.2 mmol/L | Baz Açığı (BE): -22.4 mmol/L | L-Laktat: 8.2 mmol/L | D-Laktat: 1.2 mmol/L | Na⁺: 126 mEq/L | K⁺: 7.2 mEq/L | Cl⁻: 98 mEq/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Ultrasonografi",
                "keywords": ["ultrason", "usg"],
                "content": "Abdominal USG: Aşırı sıvı dolu ince bağırsaklar."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Sindirim & Metabolizma Vakaları)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde hazır şıklar yoktur. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi kelimelerinizle</b> yazınız 
        (Örn: <i>"Rasyon bilgisi ver"</i>, <i>"Ahır yapısı nasıl?"</i>, <i>"Ping sesi var mı?"</i>, <i>"Liptak testi sonucu"</i>, <i>"Rumen sıvısı pH"</i>, <i>"Ateşi kaç?"</i>, <i>"Hemogram tahlili"</i>, <i>"Kan gazı analizi"</i>).
    </div>
""", unsafe_allow_html=True)

# Sidebar Instructor Login
st.sidebar.title("🔐 Eğitmen Portalı")
admin_pass = st.sidebar.text_input("Eğitmen Parolası:", type="password")

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

active_case = CASES[selected_case_name]

st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case['sikayet']}")

if admin_pass == "vet401":
    st.sidebar.success("Eğitmen Girişi Başarılı!")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 📋 {selected_case_name} Tüm Tahliller")
    for ck, cv in active_case["categories"].items():
        st.sidebar.markdown(f"**{cv['name']}:**")
        st.sidebar.write(cv['content'])
        st.sidebar.markdown("---")

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
            if re.search(r'\b' + re.escape(kw_clean) + r'\b', text_clean) or (len(kw_clean) > 4 and kw_clean in text_clean):
                matched_cats.append(cat_key)
                break
                
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: Rasyon bilgisi?, Ahır yapısı nasıl?, Ping sesi?, Rumen pH?, Hemogram tahlili):",
        key="query_input",
        label_visibility="collapsed"
    )

with col_button:
    btn_search = st.button("🔍 Sorgula", use_container_width=True)

if btn_search and user_query:
    matches = match_query(user_query, active_case["categories"])
    
    if matches:
        st.session_state.history[selected_case_name].insert(0, {
            "query": user_query,
            "matched_keys": matches
        })
    else:
        st.session_state.history[selected_case_name].insert(0, {
            "query": user_query,
            "matched_keys": []
        })

# Display Results History
if st.session_state.history[selected_case_name]:
    st.markdown("---")
    st.markdown("### 📑 Sorgulama Geçmişiniz ve Laboratuvar / Muayene Yanıtları")
    
    for idx, item in enumerate(st.session_state.history[selected_case_name]):
        q_text = item["query"]
        m_keys = item["matched_keys"]
        
        if m_keys:
            st.markdown(f"**❓ Sorgunuz ({idx+1}):** *"{q_text}"*")
            for k in m_keys:
                cat_data = active_case["categories"][k]
                st.markdown(f"""
                    <div class='card-found'>
                        <span class='badge-category'>{cat_data['name']}</span>
                        <div class='card-content' style='margin-top:8px;'>
                            {cat_data['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"**❓ Sorgunuz ({idx+1}):** *"{q_text}"*")
            st.warning("⚠️ Bu klinik sorgu için bir kayıt bulunamadı veya klinik olarak anlamlı bir anahtar kelime tespit edilemedi. Lütfen sorunuzu farklı kelimelerle ifade ediniz (Örn: Rasyon, Ahır şartları, Vital bulgular, Ping sesi, Rumen pH, Liptak, Hemogram, Biyokimya, Kan gazı).")
