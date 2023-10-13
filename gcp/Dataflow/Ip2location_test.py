import os
import IP2Location

from google.cloud import storage

destination_file_name = "IP-COUNTRY.BIN"

# Initialise a client
storage_client = storage.Client()
# Create a bucket object for our bucket
bucket = storage_client.get_bucket("data-engineer-393307-cloud-data-lake")
# Create a blob object from the filepath
blob = bucket.blob("glamira/location/IP-COUNTRY.BIN")
# Download the file to a destination
blob.download_to_filename(destination_file_name)

database = IP2Location.IP2Location("IP-COUNTRY.BIN")

rec = database.get_all("19.5.10.1")

print("Country Code          : " + rec.country_short)
print("Country Name          : " + rec.country_long)
print("Region Name           : " + rec.region)
print("City Name             : " + rec.city)
print("ISP Name              : " + rec.isp)
print("Latitude              : " + rec.latitude)
print("Longitude             : " + rec.longitude)
print("Domain Name           : " + rec.domain)
print("ZIP Code              : " + rec.zipcode)
print("Time Zone             : " + rec.timezone)
print("Net Speed             : " + rec.netspeed)
print("Area Code             : " + rec.idd_code)
print("IDD Code              : " + rec.area_code)
print("Weather Station Code  : " + rec.weather_code)
print("Weather Station Name  : " + rec.weather_name)
print("MCC                   : " + rec.mcc)
print("MNC                   : " + rec.mnc)
print("Mobile Carrier        : " + rec.mobile_brand)
print("Elevation             : " + rec.elevation)
print("Usage Type            : " + rec.usage_type)
print("Address Type          : " + rec.address_type)
print("Category              : " + rec.category)
print("District              : " + rec.district)
print("ASN                   : " + rec.asn)
print("AS                    : " + rec.as_name)