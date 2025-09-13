import os
import sys

import certifi
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from networksecurity.entity.artifact_entity import DataIngestionArtifact

## configuration of the Data Ingestion Config
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

load_dotenv()

# Align with app.py's env var name
MONGO_DB_URL = os.getenv("MONGODB_URL_KEY") or os.getenv("MONGO_DB_URL")
ca = certifi.where()


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def export_collection_as_dataframe(self):
        """
        Read data from mongodb
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            # If no Mongo URL, fall back to local CSV
            if not MONGO_DB_URL:
                logging.warning(
                    "MongoDB URL not configured. Falling back to CSV: Network_Data/phisingData.csv"
                )
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                local_csv = os.path.join(project_root, "Network_Data", "phisingData.csv")
                return pd.read_csv(local_csv)

            # Try Mongo first
            try:
                self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tls=True, tlsCAFile=ca)
                collection = self.mongo_client[database_name][collection_name]

                df = pd.DataFrame(list(collection.find()))
                if "_id" in df.columns.to_list():
                    df = df.drop(columns=["_id"], axis=1)

                df.replace({"na": np.nan}, inplace=True)
                return df
            except Exception as mongo_err:
                logging.warning(
                    "MongoDB fetch failed (%s). Falling back to CSV: Network_Data/phisingData.csv",
                    mongo_err,
                )
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                local_csv = os.path.join(project_root, "Network_Data", "phisingData.csv")
                return pd.read_csv(local_csv)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            # creating folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train test split on the dataframe")

            logging.info("Exited split_data_as_train_test method of Data_Ingestion class")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)

            os.makedirs(dir_path, exist_ok=True)

            logging.info("Exporting train and test file path.")

            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)
            logging.info("Exported train and test file path.")

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path,
            )
            return dataingestionartifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
