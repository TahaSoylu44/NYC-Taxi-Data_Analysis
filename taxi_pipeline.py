import pandas as pd
import numpy as np
import os
import glob
import math

def apply_advanced_zscore(series, threshold=3.5):
    """Geliştirilmiş Z-Skor (MAD) ile uç değerleri yakalar."""
    median_val = series.median()
    mad = (series - median_val).abs().median()
    
    if mad == 0:
        return series == median_val
        
    z_scores = (0.6745 * (series - median_val)) / mad
    return z_scores.abs() <= threshold

def iqr_upperbound(series_string, df):
    """IQR hesabi ile upperbound bulacagim"""
    q1 = df[series_string].quantile(0.25)
    q3 = df[series_string].quantile(0.75)
    iqr = q3 - q1
    return (q3 + 1.5 * iqr)

# ==========================================
# 2. TEMİZLİK MODÜLLERİ
# ==========================================
def clean_yellow_green(df):
    """Yellow ve Green taksiler için ücret, bahşiş ve mesafe temizliği"""
    
    #! fare_amount
    df = df[df['fare_amount'] >= 1]
    df = df[df['trip_distance'] > 0]
    df["fare_per_distance"] = df["fare_amount"] / df["trip_distance"]
    df = df[~((df["fare_amount"] > 100) & (df["fare_per_distance"] > 70))]
    df = df[~((df["fare_amount"] > 400) & (df["trip_distance"] < 20))]
    df.drop(columns=["fare_per_distance"], inplace=True)  

    #! extra
    df = df[df["extra"] >= 0]
    upper_bound = math.ceil(iqr_upperbound("extra", df))
    df = df[df["extra"] <= upper_bound]

    #! mta_tax
    #? Burada kaldin

    # Orantısal Bahşiş Temizliği (Maksimum %55)
    df["bahsis_orani"] = df["tip_amount"] / df["fare_amount"]
    df = df[df["bahsis_orani"] <= 0.55]
    df.drop(columns=["bahsis_orani"], inplace=True) # RAM'den tasarruf
    
    # Gişe (Tolls) Temizliği
    df = df[(df['tolls_amount'] >= 0) & (df['tolls_amount'] <= 40)]
    
    # Süre Temizliği (Örn: 2 dakikadan uzun, 120 dakikadan kısa)
    # Not: Eğer duration sütunu hazır gelmiyorsa (tpep_dropoff - tpep_pickup) hesaplamalısın
    # df = df[(df['duration'] > 2) & (df['duration'] < 120)]
    
    # Mesafe Temizliği (MAD Z-Skor)
    df = df[df['trip_distance'] > 0]
    gecerli_mesafeler = apply_advanced_zscore(df['trip_distance'], threshold=3.5)
    df = df[gecerli_mesafeler]
    
    return df

def clean_fhv(df):
    """FHV (Uber/Lyft) verileri ücret içermez, sadece null değerler temizlenir."""
    # Sütun isimleri genelde 'Pickup_date' ve 'DropOff_datetime' şeklindedir
    df = df.dropna(subset=['Pickup_date', 'DropOff_datetime'])
    return df

# ==========================================
# 3. AGREGASYON (SIKIŞTIRMA) MODÜLÜ
# ==========================================
def aggregate_hourly_trips(df, pickup_col):
    """
    12 milyon satırlık ham veriyi, 'Saat -> Yolculuk Sayısı' formatına sıkıştırır.
    Modele girecek asıl hafif veri budur.
    """
    df[pickup_col] = pd.to_datetime(df[pickup_col])
    
    # Dakika ve saniyeleri atarak sadece "Saat" bazında grupla
    df['pickup_hour'] = df[pickup_col].dt.floor('h')
    
    # Hangi saatte kaç yolculuk yapılmış say
    df_aggregated = df.groupby('pickup_hour').size().reset_index(name='trip_count')
    
    return df_aggregated

# ==========================================
# 4. ANA DÖNGÜ (MOTOR)
# ==========================================
def run_pipeline(input_folder, output_folder):
    """Klasördeki dosyaları tek tek okur, işler ve belleği temizleyerek kaydeder."""
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    file_paths = glob.glob(f"{input_folder}/*.parquet")
    
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        print(f"[*] İşleniyor: {file_name}")
        
        # Dosyayı oku
        df = pd.read_parquet(file_path)
        
        # İsme göre strateji belirle
        file_name_lower = file_name.lower()
        if "yellow" in file_name_lower:
            df = clean_yellow_green(df)
            df_agg = aggregate_hourly_trips(df, pickup_col="tpep_pickup_datetime")
            
        elif "green" in file_name_lower:
            df = clean_yellow_green(df)
            df_agg = aggregate_hourly_trips(df, pickup_col="lpep_pickup_datetime")
            
        elif "fhv" in file_name_lower:
            df = clean_fhv(df)
            df_agg = aggregate_hourly_trips(df, pickup_col="Pickup_date")
        else:
            print(f"[-] Atlandı (Bilinmeyen tür): {file_name}")
            continue
            
        # Agrege edilmiş yeni dosyayı kaydet
        output_path = os.path.join(output_folder, f"agg_{file_name}")
        df_agg.to_parquet(output_path, index=False)
        print(f"[+] Kaydedildi: agg_{file_name}\n")

# ==========================================
# ÇALIŞTIRMA NOKTASI
# ==========================================
if __name__ == "__main__":
    # Klasör yollarını kendi sistemine göre ayarla
    GIRDI_KLASORU = "./raw_taxi_data"
    CIKTI_KLASORU = "./processed_taxi_data"
    
    print(">>> Veri Boru Hattı Başlatılıyor...")
    run_pipeline(GIRDI_KLASORU, CIKTI_KLASORU)
    print(">>> Tüm işlemler başarıyla tamamlandı.")