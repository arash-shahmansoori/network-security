import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Align with app.py: prefer MONGODB_URL_KEY, fallback to legacy MONGO_DB_URL
MONGO_DB_URL = os.getenv("MONGODB_URL_KEY") or os.getenv("MONGO_DB_URL")

import certifi

ca = certifi.where()

import pandas as pd
import pymongo

from networksecurity.exception.exception import NetworkSecurityException


class NetworkDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def csv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def insert_data_mongodb(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            if not MONGO_DB_URL:
                raise ValueError("MongoDB URL not configured. Set MONGODB_URL_KEY in environment.")

            # Use certifi CA bundle for TLS (required for MongoDB Atlas and SRV URIs)
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            self.database = self.mongo_client[self.database]

            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)
            return len(self.records)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e


if __name__ == "__main__":
    # Resolve CSV path in a cross-platform way
    FILE_PATH = os.path.join("Network_Data", "phisingData.csv")
    DATABASE = "ArashML"
    Collection = "NetworkData"
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json_convertor(file_path=FILE_PATH)
    print(records)
    no_of_records = networkobj.insert_data_mongodb(records, DATABASE, Collection)
    print(no_of_records)
