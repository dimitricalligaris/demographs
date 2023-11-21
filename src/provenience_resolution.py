import pandas as pd
import configparser

class ProvenienceResolutor():
    
    CONFIG_FILE_PATH = 'platforms.ini'

    @staticmethod
    def isSupported(df: pd.DataFrame):
        config = configparser.ConfigParser()
        config.read(ProvenienceResolutor.CONFIG_FILE_PATH)

        for platform_name in config.sections():
            platform_column_names = set(config[platform_name].keys())
            if len(df.columns) == len(set(config[platform_name].keys())) and set(map(str.lower, set(df.columns))) == platform_column_names:
                return True, platform_name
        return False, None



