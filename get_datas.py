import requests
import time
import os

urls = [
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-01.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-01.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-01.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-02.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-02.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-02.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-03.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-03.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-03.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-04.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-04.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-04.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-05.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-05.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-05.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-06.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-06.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-06.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-07.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-07.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-07.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-08.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-08.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-08.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-09.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-09.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-09.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-10.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-10.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-10.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-11.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-11.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-11.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2015-12.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2015-12.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2015-12.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-01.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-01.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-01.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-02.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-02.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-02.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-03.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-03.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-03.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-04.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-04.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-04.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-05.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-05.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-05.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-06.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-06.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-06.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-07.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-07.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-07.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-08.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-08.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-08.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-09.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-09.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-09.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-10.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-10.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-10.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-11.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-11.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-11.parquet",
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2016-12.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2016-12.parquet", 
        "https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2016-12.parquet",
        ]

headers = {
    # Bir Fedora Linux sistemindeki Firefox tarayıcısını taklit eden başlık
    "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"
}

for url in urls:
    filename = url.split("/")[-1]   # / e göre ayırır en sondakini isim kabul ederim
    target_directory = "datas"
    save_path = os.path.join(target_directory, filename)    # combine the target directory and filename like target_directory/filename
    print(f"{filename} downloading...")

    try:
        response = requests.get(url, headers=headers)   # GET Request
        print("Response code", response.status_code)
        response.raise_for_status()     # Eğer 200 başarılı dışında bir kod gelirse (403 ya da 404) except bloğuna düş.

        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"File saved: {save_path}")
    except requests.exceptions.RequestException as e:
        print("Response code", response.status_code)
        print(f"An error occured: {e}")

    print("Wait for 15 seconds")
    time.sleep(15)

print("All datas downloaded :)")