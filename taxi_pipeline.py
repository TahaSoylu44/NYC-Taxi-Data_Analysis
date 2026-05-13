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

def clean_yellow(df):
    """Yellow taksiler için veri temizliği"""
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])

    df.drop(columns=["VendorID", "store_and_fwd_flag", "congestion_surcharge", "payment_type", "airport_fee"], inplace=True)

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
    df = df[df["mta_tax"] >= 0]

    #! tip_amount
    df = df[df["tip_amount"] >= 0]
    df["bahsis_per_fare"] = df["tip_amount"] / df["fare_amount"]
    df["bahsis_per_fare_normalize"] = np.log1p(df["bahsis_per_fare"])
    df = df[apply_advanced_zscore(df["bahsis_per_fare_normalize"], 3.5)]
    df.drop(columns=["bahsis_per_fare", "bahsis_per_fare_normalize"], inplace=True)

    #! tolls_amount
    df = df[(df['tolls_amount'] >= 0) & (df['tolls_amount'] <= 30)]

    #! duration
    df["duration"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
    df = df[df["duration"] > 0]
    df["duration_normalize"] = np.log1p(df["duration"])
    df = df[apply_advanced_zscore(df["duration_normalize"], 3.5)]
    df.drop(columns=["duration_normalize"], inplace=True)

    #! passenger_count
    df = df[(df["passenger_count"] > 0) & (df["passenger_count"] <= 6)]
    
    #! trip_distance
    df = df[(df['trip_distance'] > 0) & (df["trip_distance"] <= 30)]

    #! RatecodeID
    df = df[df["RatecodeID"] != 99]

    #! speed
    df["speed"] = (df["trip_distance"] / df["duration"]) * 60 * 1.61    # km/h
    df = df[(df["speed"] > 0) & (df["speed"] <= 110)]

    df.drop_duplicates(inplace=True)
    
    return df

def aggregate_hourly_trips(df):
    df['pickup_hour'] = df["tpep_pickup_datetime"].dt.floor('h')    # saatlik gruplama yap
    df_aggregated = df.groupby(['pickup_hour', "PULocationID"]).size().reset_index(name='trip_count') # hangi saatte kaç yolculuk?
    
    return df_aggregated

def run_pipeline(input_folder, output_folder):
    """Klasördeki dosyaları tek tek okur, işler ve belleği temizleyerek kaydeder."""
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    file_paths = glob.glob(f"{input_folder}/*.parquet")
    
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        print(f"[*] İşleniyor: {file_name}")
        try:    
            df = pd.read_parquet(file_path)
            file_name_lower = file_name.lower()
            if "yellow" in file_name_lower:
                df = clean_yellow(df)
                df_agg = aggregate_hourly_trips(df)
            else:
                print(f"[-] Atlandı (Bilinmeyen tür): {file_name}")
                continue
                
            # Agrege edilmiş yeni dosyayı kaydet
            output_path = os.path.join(output_folder, f"agg_{file_name}")
            df_agg.to_parquet(output_path, index=False)
            print(f"[+] Kaydedildi: agg_{file_name}\n")
        except Exception as e:
            print(f"[!] HATA - {file_name}: {e}")
            continue

def concatanate():
    clear_files = glob.glob("./processed_taxi_data/agg_*.parquet")
    table_list = []

    for file in clear_files:
        small_table = pd.read_parquet(file)
        table_list.append(small_table)

    df_master = pd.concat(table_list, ignore_index=True)
    df_master.to_parquet("./final_time_split_data.parquet", index=False)

if __name__ == "__main__":
    INPUT_FOLDER = "./datas"
    OUTPUT_FOLDER = "./processed_taxi_data"
    
    print("Pipeline started...")
    run_pipeline(INPUT_FOLDER, OUTPUT_FOLDER)
    concatanate()
    print("The process is done :D")