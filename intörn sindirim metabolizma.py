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
    "Vaka 1 (Yıldız)": {
        "kod": "VAKA_1",
        "sikayet": "Şiddetli nefes darlığı, yüksek ateş (41.2 °C), burundan mukopürülan iltihaplı akıntı, iştahsızlık ve belirgin düşkünlük.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "yarı açık", "kapalı", "bağlı", "serbest", "ortam", "hijyen", "toz", "nakil"],
                "content": "Nakil sonrası kapalı besi padoğuna alınmıştır. Yetersiz havalandırma, basık ve yüksek nemli hava, yoğun amonyak kokusu, tozlu ve ıslak kirli saman altlık."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "saman", "kaba", "kesif", "kg"],
                "content": "Nakil sonrası ani rasyon değişimi yapılmıştır. Günlük rasyon: 12 kg mısır silajı, 4 kg buğday samanı, 8 kg besi büyütme yemi (kesif yem)."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "stres"],
                "content": "3 gün önce 400 km uzaklıktaki başka bir işletmeden kamyonla nakledilmiştir. Şiddetli nakil ve ortam değişimi stresi mevcuttur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "aşı", "aşılama", "geçirdi", "önce"],
                "content": "İşletmeye girişte viral respiratory aşılaması yapılmamıştır. Geçmişinde solunum yolu enfeksiyonu kaydı yoktur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "deri", "vital", "öksürük", "burun"],
                "content": "Vücut Sıcaklığı: 41.2 °C | Kalp Frekansı: 112 atım/dk | Solunum Frekansı: 64 nefes/dk | Mukoza: Şiddetli hiperemik / siyanotik | CRT: 3.5 saniye | Dehidrasyon: %8 | Bol mukopürülan iltihaplı burun akıntısı, hassas ağrılı trakeal refleks, ağız açık nefes alma."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer", "sessiz alan", "konsolidasyon", "krepitasyon"],
                "content": "Kalp Oskültasyonu: Taşikardik, ek ses veya üfürüm saptanmadı. Akciğer Oskültasyonu: Kranio-ventral akciğer loblarında (lobus cranialis) solunum sesleri kaybolmuş (sessiz alanlar / parankimal konsolidasyon), kaudo-dorsal alanlarda kaba raller ve yaş krepitasyon sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "hassasiyet", "interkostal", "göğüs"],
                "content": "Göğüs duvarı bilateral interkostal aralık palpasyonunda şiddetli ağrı reaksiyonu pozitif (+). Sopa, Kama ve Withers pinch testleri negatif (-)."
            },
            "PING_LIPTAK": {
                "name": "Ping Akustik Muayenesi & Liptak Testi",
                "keywords": ["ping", "liptak", "abomasosentez", "çınlama", "steel band"],
                "content": "Sağ ve sol abdominal duvar boyunca akustik ping sesi veya metallic çınlama saptanmadı. Liptak testi yapılmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen", "ponksiyon", "sıvı", "protozoa", "hareket"],
                "content": "pH: 6.5 | Renk: İnce zeytin yeşili | Koku: Normal aromatik | Protozoa Hareketliliği: Orta canlılıkta."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Kültür & Sitoloji",
                "keywords": ["kültür", "bakteri", "gram", "bal", "sürüntü", "nazofarenks", "mannheimia", "pasteurella"],
                "content": "Nazofaringeal sürüntü ve BAL (Bronkoalveoler Lavaj) Sıvısı Gram Boyama: Gram-negatif bipolar basiller hakim. Bakteriyolojik Kültür: Mannheimia haemolytica pür kültür olarak üredi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal", "mıknatıs"],
                "content": "Retikulum ve sifoid bölgede Metal Dedektör (Ferroskop) Muayenesi: Negatif (-), metalik sinyal alınmadı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "rdw", "mcv", "plt"],
                "content": "Lökosit (WBC): 28.5 x10³/µL | Eritrosit (RBC): 6.2 x10⁶/µL | Hemoglobin (Hb): 11.5 g/dL | Hematokrit (PCV): %38 | RDW: %14.2 | MCV: 52 fL | MCH: 18.5 pg | MCHC: 30.2 g/dL | Nötrofil (Segmenteli): %68 | Nötrofil (Çomak/Band): %14 | Lenfosit: %12 | Monosit: %4 | Eozinofil: %2 | Bazofil: %0 | Trombosit (PLT): 280 x10³/µL | Plazma Fibrinojeni: 1150 mg/dL | PP/F Oranı: 6.5."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "troponin", "glikoz", "bhba"],
                "content": "Albümin: 2.6 g/dL | Total Protein: 7.5 g/dL | Globülin: 4.9 g/dL | AST: 95 U/L | GGT: 22 U/L | BUN: 32 mg/dL | Kreatinin: 1.3 mg/dL | Kardiyak Troponin I (cTnI): 0.18 ng/mL | Glikoz: 72 mg/dL | BHBA: 0.6 mmol/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "oksijen", "hipoksi"],
                "content": "Kan pH: 7.22 | pO₂: 52 mmHg | pCO₂: 58 mmHg | HCO₃⁻: 21.5 mmol/L | Baz Açığı (BE): -4.8 mmol/L | L-Laktat: 3.8 mmol/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Torakal USG",
                "keywords": ["ultrason", "usg", "toraks", "akciğer usg", "konsolidasyon", "comet tail", "plevra"],
                "content": "Torakal Ultrasonografi: Kranio-ventral akciğer sahalarında doku yapısında hepatizasyon (dokulaşma), komanlı kuyruğu (comet-tail) artifaktları ve plevral boşlukta 2.5 cm fibrinli anekoik sıvı birikimi."
            }
        }
    },
    "Vaka 2 (Güneş)": {
        "kod": "VAKA_2",
        "sikayet": "Yüksek ateş (41.5 °C), koyu çay/port şarabı renginde idrar (hemoglobinüri), göz ve mukozalarda şiddetli sarılık (ikterus) ve aşırı halsizlik.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "yarı açık", "mera", "kene", "otlatma"],
                "content": "Meralık otlatma sonrası yarı açık barınakta barındırılmaktadır. Mera dönüşü kenelerle (Rhipicephalus / Boophilus spp.) yoğun bulaşık ortam."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "saman", "kaba", "kesif", "kg"],
                "content": "Günlük mera otlaması ilave olarak işletmede: 8 kg mısır silajı, 2 kg yonca kuru otu, 4 kg süt yemi."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "mera", "kene"],
                "content": "Kene popülasyonunun yüksek olduğu alçak rakımlı nemli mera bölgesinde otlatılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "kene", "bulaşıcı"],
                "content": "Bölgede daha önce keneyle bulaşan kan paraziti salgınları bildirilmiştir. Kene ilaçlaması 3 aydır yapılmamıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "deri", "vital", "idrar", "ikterus", "sarılık"],
                "content": "Vücut Sıcaklığı: 41.5 °C | Kalp Frekansı: 124 atım/dk | Solunum Frekansı: 52 nefes/dk | Mukoza: Şiddetli ikterik (parlak sarı) ve soluk | CRT: 4.0 saniye | Dehidrasyon: %7 | İdrar: Koyu çay / port şarabı renginde köpüklü idrar (Hemoglobinüri)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik, anemiye bağlı sol ventrikül bazalinde Grade II/VI anemik sistolik üfürüm. Akciğer Oskültasyonu: Sert veziküler solunum sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa, Kama ve Withers pinch testleri tamamı negatif (-)."
            },
            "PING_LIPTAK": {
                "name": "Ping Akustik Muayenesi & Liptak Testi",
                "keywords": ["ping", "liptak", "abomasosentez"],
                "content": "Abdominal ping veya çınlama sesi saptanmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen", "ponksiyon", "sıvı", "protozoa"],
                "content": "pH: 6.8 | Renk: Normal zeytin yeşili | Protozoa: Canlı ve hareketli."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Kan Yayması & İdrar Sedimantasyonu",
                "keywords": ["kültür", "bakteri", "giemsa", "yayma", "babesia", "armut", "hemoglobinüri"],
                "content": "Periferik Kulak Ven Kan Yayması (Giemsa): Eritrositler içinde çiftler halinde armut biçimli (paired pyriform) Babesia bovis merozoitleri saptandı (%12 enfekte eritrosit). İdrar Santrifüj Analizi: Santrifüj sonrası tüp tabanında eritrosit peleti oluşmadı, üst sıvı kırmızı kaldı (İntravasküler Hemoglobinüri doğrulaması)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Negatif (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "rdw", "mcv", "plt"],
                "content": "Eritrosit (RBC): 2.4 x10⁶/µL | Hemoglobin (Hb): 4.8 g/dL | Hematokrit (PCV): %14 | MCV: 58 fL | MCH: 20.0 pg | MCHC: 34.2 g/dL | RDW: %19.5 | Lökosit (WBC): 16.8 x10³/µL | Nötrofil: %62 | Lenfosit: %28 | Monosit: %8 | Eozinofil: %2 | Trombosit (PLT): 95 x10³/µL | Plazma Fibrinojeni: 620 mg/dL | PP/F Oranı: 11.2."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "bilirubin", "hemoglobinemia"],
                "content": "Total Bilirubin: 6.8 mg/dL | İndirekt Bilirubin: 5.4 mg/dL | Direkt Bilirubin: 1.4 mg/dL | AST: 245 U/L | LDH: 850 U/L | GGT: 34 U/L | Albümin: 2.7 g/dL | Total Protein: 6.9 g/dL | Globülin: 4.2 g/dL | BUN: 38 mg/dL | Kreatinin: 1.6 mg/dL | Serbest Plazma Hemoglobini: 180 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.28 | pO₂: 60 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 18.2 mmol/L | Baz Açığı (BE): -6.5 mmol/L | L-Laktat: 4.5 mmol/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Abdominal USG",
                "keywords": ["ultrason", "usg", "dalak", "splenomegali", "karaciğer"],
                "content": "Abdominal Ultrasonografi: Dalak boyutlarında belirgin artış (Masif Splenomegali), parankim ekojenitesinde homojen azalma. Karaciğer boyutlarında hafif artış (Hepatomegali)."
            }
        }
    },
    "Vaka 3 (Benli)": {
        "kod": "VAKA_3",
        "sikayet": "İştahsızlık, süt veriminde aşırı düşüş, mukozalarda solukluk/sarılık, kuru sert mukuslu dışkılama ve doku hipoksisine bağlı huzursuzluk/saldırganlık.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "mera", "sineklik", "tabanidae"],
                "content": "Açık mera ve padoğa erişimli yarı kapalı ahır. Taban saman altlık. Otlatma merasında mermer sinekleri (Tabanidae) ve keneler yoğun."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "saman", "kaba", "kesif", "kg"],
                "content": "Mera otlaması ilave olarak: 10 kg mısır silajı, 3 kg buğday samanı, 5 kg kesif yem."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Mera otlatması yapılan ova tesisi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "sinek", "kene"],
                "content": "Sürüye dışarıdan kontrolsüz hayvan alımı öyküsü vardır. Vektör mücadelesi yetersizdir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "deri", "vital", "idrar", "sarılık"],
                "content": "Vücut Sıcaklığı: 40.2 °C | Kalp Frekansı: 116 atım/dk | Solunum Frekansı: 48 nefes/dk | Mukoza: İkterik (soluk limon sarısı) | CRT: 3.5 saniye | Dehidrasyon: %6 | İdrar: Berrak ve sarı renkli (Hemoglobinüri YOKTUR). Dışkı: Kuru, mukus kaplı, siyahımsı."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik, anemiye bağlı sistolik üfürüm. Akciğer Oskültasyonu: Polypnea sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch"],
                "content": "Retikulum ağrı testleri negatif (-)."
            },
            "PING_LIPTAK": {
                "name": "Ping Akustik Muayenesi & Liptak Testi",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi saptanmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen", "ponksiyon", "sıvı"],
                "content": "pH: 6.7 | Renk: Normal yeşil."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji, Kan Yayması & İdrar Analizi",
                "keywords": ["kültür", "bakteri", "giemsa", "yayma", "anaplasma", "marjin", "nokta"],
                "content": "Periferik Kulak Ven Kan Yayması (Giemsa): Eritrositlerin marjinlerinde (çeperinde) koyu noktasal Anaplasma marginale inklüzyon cisimcikleri saptandı (%35 enfekte eritrosit). İdrar Analizi: Dipstick testinde Hemoglobin NEGATİF, Bilirubin POZİTİF (+2)."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal"],
                "content": "Ferroskop testi negatif (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "rdw", "mcv", "plt"],
                "content": "Eritrosit (RBC): 2.8 x10⁶/µL | Hemoglobin (Hb): 5.2 g/dL | Hematokrit (PCV): %16 | RDW: %18.8 | MCV: 57 fL | MCH: 18.5 pg | MCHC: 32.5 g/dL | Lökosit (WBC): 12.4 x10³/µL | Nötrofil: %58 | Lenfosit: %34 | Monosit: %6 | Eozinofil: %2 | Trombosit (PLT): 140 x10³/µL | Plazma Fibrinojeni: 480 mg/dL | PP/F Oranı: 14.5."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "bilirubin"],
                "content": "Total Bilirubin: 5.2 mg/dL | İndirekt Bilirubin: 4.1 mg/dL | Direkt Bilirubin: 1.1 mg/dL | AST: 185 U/L | GGT: 28 U/L | LDH: 620 U/L | Albümin: 2.9 g/dL | Total Protein: 7.0 g/dL | Globülin: 4.1 g/dL | BUN: 26 mg/dL | Kreatinin: 1.1 mg/dL | Serbest Plazma Hemoglobini: 15 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.34 | pO₂: 64 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 20.8 mmol/L | Baz Açığı (BE): -3.8 mmol/L | L-Laktat: 3.1 mmol/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Abdominal USG",
                "keywords": ["ultrason", "usg", "dalak", "splenomegali"],
                "content": "Abdominal Ultrasonografi: Dalak boyutlarında masif büyüme (Splenomegali) ve parankimal kongestiyon."
            }
        }
    },
    "Vaka 4 (Karakız & Fırtına)": {
        "kod": "VAKA_4",
        "sikayet": "Karakız (Tip I Ketozis): Pik süt döneminde ani iştahsızlık, kesif yemi reddetme, süt veriminde 15 L düşüş, nefeste aseton kokusu. Fırtına (Tip II Ketozis): Doğum sonrası 10. günde çökmüş obez inek, insülin direnci ve yeme karşı tam isteksizlik.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "yarı açık", "serbest", "obezite"],
                "content": "Karakız: Yarı açık serbest duraklı modern havadar ahır. Fırtına: Kapalı duraklı ahır, kuru dönemde aşırı yemlemeyle obezleştirilmiş (BCS: 4.25) sürü ortamı."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "saman", "kaba", "kesif", "kg"],
                "content": "Karakız (Tip I): 15 kg mısır silajı, 4 kg yonca, 10 kg süt yemi (kesif yemi reddediyor). Fırtına (Tip II): Kuru dönemde yüksek enerjili rasyonla obezleştirilmiş."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil"],
                "content": "Entansif süt tesisi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "doğum", "kuru dönem", "bcs"],
                "content": "Karakız: Laktasyonun 4. haftasında. Fırtına: Doğum sonrası 10. gün, kuru dönemde BCS > 4.0 aşırı kondüsyon."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "deri", "vital", "aseton", "keton", "idrar", "süt"],
                "content": "Karakız (Tip I): T: 38.5 °C | HR: 78 atım/dk | RR: 24 nefes/dk | Mukoza: Pembe | CRT: 2.0 sn | Dehidrasyon: %4 | Nefeste ve sütte aseton kokusu. Süt ve İdrar Keton Testi (Nitroprussid): Şiddetli Pozitif (+3). Fırtına (Tip II): T: 38.2 °C | HR: 86 atım/dk | RR: 28 nefes/dk | İdrar Keton: Pozitif (+2)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Normal veziküler solunum sesleri, kalp sesleri normal."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch"],
                "content": "Ağrı testleri negatif (-)."
            },
            "PING_LIPTAK": {
                "name": "Ping Akustik Muayenesi & Liptak Testi",
                "keywords": ["ping", "liptak"],
                "content": "Abdominal ping sesi saptanmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen", "ponksiyon", "sıvı"],
                "content": "pH: 6.6 | Renk: Yeşil-kahve | Protozoa: Hareketli."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "Mikrobiyoloji & Keton Testleri",
                "keywords": ["kültür", "bakteri", "keton", "nitroprussid", "bhba"],
                "content": "Süt ve İdrar Nitroprussid Keton Testi: Karakız'da +3 Pozitif, Fırtına'da +2 Pozitif."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal"],
                "content": "Ferroskop negatif (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "rdw", "mcv", "plt"],
                "content": "Karakız (Tip I): WBC: 7.2 x10³/µL | RBC: 6.1 x10⁶/µL | PCV: %32 | Fibrinojen: 350 mg/dL | PP/F: 21.0. Fırtına (Tip II): WBC: 8.5 x10³/µL | PCV: %34 | Fibrinojen: 420 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası, Enzimler & Keton Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "glikoz", "bhba", "nefa", "gldh"],
                "content": "Karakız (Tip I Ketozis): Kan Glikozu: 24 mg/dL | Beta-Hidroksibütirat (BHBA): 3.6 mmol/L | NEFA: 0.65 mmol/L | AST: 82 U/L | GGT: 22 U/L | Albümin: 3.2 g/dL | Total Protein: 7.1 g/dL. Fırtına (Tip II Ketozis / Yağlı Karaciğer): Kan Glikozu: 38 mg/dL | BHBA: 2.8 mmol/L | NEFA: 1.45 mmol/L | AST: 280 U/L | GGT: 88 U/L | GLDH: 65 U/L | Albümin: 2.2 g/dL | Total Protein: 5.8 g/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Karakız: pH: 7.35 | pO₂: 75 mmHg | pCO₂: 41 mmHg | HCO₃⁻: 22.0 mmol/L | BE: -1.2 mmol/L | L-Laktat: 1.2 mmol/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Hepatik USG",
                "keywords": ["ultrason", "usg", "karaciğer", "yağlanma", "hiperekojen"],
                "content": "Karakız (Tip I): Karaciğer USG normal ekojenitede. Fırtına (Tip II): Karaciğer parankiminde masif hiperekojenite (Yağlı Karaciğer Sendromu) ve portal venizasyon hatlarında silinme."
            }
        }
    },
    "Vaka 5 (Ceylan)": {
        "kod": "VAKA_5",
        "sikayet": "Kesikli ve ağrılı idrar yapma (strangüri/disüri), idrar sonunda taze kan pıhtıları ve irin gelmesi, sırtı kamburlaştırma (lordosis) ve sol böbrek bölgesinde ağrı.",
        "categories": {
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "durak", "havalandırma", "koku", "amonyak", "altlık", "temiz", "kirli", "ıslak", "kapalı", "bağlı", "hijyen"],
                "content": "Kapalı bağlı beton zeminli ahır. Altlık ıslak gübreli saman, hijyen yetersiz, amonyak kokulu basık ortam."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "saman", "kaba", "kesif", "kg"],
                "content": "12 kg mısır silajı, 3 kg buğday samanı, 6 kg kesif yem."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil"],
                "content": "Sabit süt tesisi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "doğum", "metritis", "idrar"],
                "content": "1 ay önce pürülan metritis ve üriner sistem asendans enfeksiyon öyküsü mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Rektal Muayene Bulguları",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "deri", "vital", "idrar", "rektal", "böbrek", "üreter"],
                "content": "Vücut Sıcaklığı: 39.9 °C | Kalp Frekansı: 98 atım/dk | Solunum Frekansı: 36 nefes/dk | Mukoza: Soluk pembe | CRT: 2.5 saniye | Dehidrasyon: %5 | Rektal Muayene: Sol böbrek belirgin ağrılı, lobulasyonları şişkin ve kalınlaşmış; sol üreter parmak kalınlığında sertleşmiş ve ağrılı."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer sesleri normal sınırlar içerisinde."
            },
            "AGRI_TESTLERI": {
                "name": "Ağrı & Provokasyon Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "lumbar"],
                "content": "Sol lumbar / böbrek bölgesine yumrukla vurulduğunda (Renal Perküsyon) şiddetli ağrı ve inleme reaksiyonu pozitif (+)."
            },
            "PING_LIPTAK": {
                "name": "Ping Akustik Muayenesi & Liptak Testi",
                "keywords": ["ping", "liptak"],
                "content": "Ping sesi saptanmadı."
            },
            "RUMEN_SIVISI": {
                "name": "Rumen Ponksiyon Sıvısı Analizi",
                "keywords": ["rumen", "ponksiyon", "sıvı"],
                "content": "pH: 6.7 | Protozoa canlı."
            },
            "MIKROBIYOLOJI_KULTUR": {
                "name": "İdrar Analizi, Sedimantasyon & Kültür",
                "keywords": ["kültür", "bakteri", "idrar", "sedimantasyon", "gram", "corynebacterium", "renale", "lökositüri", "hematüri"],
                "content": "İdrar Makroskobisi: Bulanık, kırmızımsı-kahverengi, amonyak kokulu, irinli fibrin pıhtıları içeren idrar. İdrar Dansitesi: 1.015 | Protein: +3 | Lökositüri ve Hematüri masif pozitif. İdrar Sedimantasyon Gram Boyamada: Gram-pozitif çomaklar ve difteroid basiller (Corynebacterium renale) saptandı. İdrar Bakteriyolojik Kültürü: Corynebacterium renale pür kültür üredi."
            },
            "DEDEKTOR_FERROSKOP": {
                "name": "Metal Dedektör (Ferroskop) Muayenesi",
                "keywords": ["dedektör", "ferroskop", "metal"],
                "content": "Ferroskop testi negatif (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "rdw", "mcv", "plt"],
                "content": "Lökosit (WBC): 24.2 x10³/µL | Nötrofil (Segmenteli): %62 | Nötrofil (Çomak/Band): %10 | Lenfosit: %18 | Monosit: %6 | Eozinofil: %4 | Eritrosit (RBC): 4.5 x10⁶/µL | PCV: %26 | Plazma Fibrinojeni: 980 mg/dL | PP/F Oranı: 7.2."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Böbrek Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "azotemi"],
                "content": "BUN: 68 mg/dL | Kreatinin: 3.8 mg/dL | Albümin: 2.5 g/dL | Total Protein: 7.8 g/dL | Globülin: 5.3 g/dL | AST: 85 U/L | GGT: 24 U/L | Sodyum (Na⁺): 132 mEq/L | Potasyum (K⁺): 5.6 mEq/L | Klor (Cl⁻): 92 mEq/L."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.26 | pO₂: 78 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 16.5 mmol/L | Baz Açığı (BE): -8.2 mmol/L | L-Laktat: 2.2 mmol/L."
            },
            "GORUNTULEME_USG": {
                "name": "Görüntüleme & Renal USG",
                "keywords": ["ultrason", "usg", "böbrek usg", "pyelonefrit", "üreter"],
                "content": "Renal Ultrasonografi: Sol böbrek korteks ve medulla yapısında genişleme, renal pelvis alanında hiperekojen irin/ürolit çökeltileri ve üreter duvarında masif kalınlaşma."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Solunum, Kan Parazitleri, Metabolizma, Üriner)</h3>", unsafe_allow_html=True)

# Instructor Password Feature in Sidebar
st.sidebar.markdown("### 🔑 Eğitmen Portalı")
hoca_pass = st.sidebar.text_input("Eğitmen Parolası:", type="password", key="hoca_pass_key")
is_hoca = (hoca_pass == "vet401")

if is_hoca:
    st.sidebar.success("🔓 Eğitmen Modu Aktif! Tüm tahliller açık.")

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde şıklar veya hazır yönlendirmeler <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya tıbbi terimlerinizle</b> yazınız 
        (Örn: <i>"Ahır havalandırması nasıl?"</i>, <i>"Rasyonda verilen yem miktarları nedir?"</i>, <i>"Trakeal refleks var mı?"</i>, <i>"Kan yaymasında babesia var mı?"</i>, <i>"Kan gazı pO2 kaç?"</i>, <i>"İdrar kültüründe ne üredi?"</i>, <i>"Renal USG sonucu nedir?"</i>).
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

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    matched_cats = []
    
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\b' + re.escape(kw_clean) + r'\b', text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
                
    return matched_cats

if is_hoca:
    st.markdown("---")
    st.markdown("## 🔓 EĞİTMEN KONTROL PANELİ — TÜM BULGULAR VE TAHLİLLER")
    for c_key, c_info in active_case["categories"].items():
        st.markdown(f"""
            <div class='card-found'>
                <div class='card-title'><span class='badge-category'>{c_info['name']}</span></div>
                <div class='card-content'>{c_info['content']}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")
    
    col_input, col_button = st.columns([4, 1])
    
    with col_input:
        user_query = st.text_input(
            "Sorunuzu Buraya Yazınız (Örn: Ahır şartları nedir?, Kan yayması sonucu?, Burun akıntısı var mı?, Renal USG?):",
            key="query_input"
        )
    
    with col_button:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        submit_btn = st.button("🔎 Sorgula", use_container_width=True)

    if submit_btn and user_query:
        matched = match_query(user_query, active_case["categories"])
        
        st.session_state.history[selected_case_name].insert(0, {
            "query": user_query,
            "matched_categories": matched
        })

    # Display History
    if st.session_state.history[selected_case_name]:
        st.markdown("---")
        st.markdown("### 📜 Sorgu Geçmişiniz ve Laboratuvar / Muayene Yanıtları:")
        
        for idx, item in enumerate(st.session_state.history[selected_case_name]):
            st.markdown(f"**🔍 Sorduğunuz Soru ({idx+1}):** *"{item['query']}"*")
            
            if item["matched_categories"]:
                for cat_key in item["matched_categories"]:
                    cat_info = active_case["categories"][cat_key]
                    st.markdown(f"""
                        <div class='card-found'>
                            <div class='card-title'><span class='badge-category'>{cat_info['name']}</span></div>
                            <div class='card-content'>{cat_info['content']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Bu vaka için yazdığınız arama terimiyle doğrudan eşleşen özel bir muayene veya tahlil kaydı bulunamadı. Lütfen tıbbi teriminizi veya arama cümlenizi kontrol ediniz.")
            st.markdown("---")
