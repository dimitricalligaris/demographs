from abc import ABC, abstractmethod
import configparser
import pandas as pd
from enum import Enum


NULL_VALUE = pd.NA

def is_null_value(value):
    return pd.isna(value)


class StandardColumns(Enum):
    STATUS = 'status'
    STARTED_AT = 'started_at'
    COMPLETED_AT = 'completed_at'
    TIME_SPENT = 'time_spent_seconds'
    TOTAL_APPROVALS = 'total_approvals'
    AGE = 'age'
    SEX = 'sex'
    NATIONALITY = 'nationality'
    LANGUAGE = 'language'


class Normalizer(ABC):
    """
    Associa i nomi degli attributi, calcola quelli derivati, elimina i null
    """

    CONFIG = configparser.ConfigParser()
    CONFIG.optionxform = str  # per rendere il configparser case sensitive
    CONFIG.read('platforms.ini')

    def __init__(self, input_dataframe):
        self.input_dataframe = input_dataframe

        self.output_dataframe = pd.DataFrame({name.value: [] for name in StandardColumns})

        self.platform_name = None
        self.associationDictionary = None

    def normalize(self):
        self.associateAttributes() if self.associationDictionary is not None else None
        self.convertNulls()
        self.fillRemainingColumns()
        self.additionalProcessing()
        self.convertNulls()     # per convertire eventuali valori nulli generati in fase di calcolo delle colonne mancanti
        return self.output_dataframe

    def associateAttributes(self):
        """
        Riporta i dati di input nelle colonne corrispondenti in base alle associazioni definite
        """
        for input_column, output_column in self.associationDictionary.items():
            if any(output_column == attribute.value for attribute in StandardColumns):   # se il nome colonna è presente in uno di quelli previsti da StandardColumns
                self.output_dataframe[output_column] = self.input_dataframe[input_column].copy()

    @abstractmethod
    def fillRemainingColumns(self):
        """
        Calcola i valori non associabili direttamente
        """
        pass

    @abstractmethod
    def convertNulls(self):
        """
        Converte in null i valori indefiniti
        """
        pass

    @abstractmethod
    def additionalProcessing(self):
        pass


class ProlificNormalizer(Normalizer):

    def __init__(self, input_dataframe):
        super().__init__(input_dataframe)
        platform_name = 'Prolific'
        self.associationDictionary = dict(Normalizer.CONFIG[platform_name])

    def convertNulls(self):
        old_values = ['DATA_EXPIRED','','CONSENT_REVOKED',pd.NaT, None]
        self.output_dataframe.replace(old_values, NULL_VALUE, inplace=True)
        self.output_dataframe[StandardColumns.AGE.value] = pd.to_numeric(self.output_dataframe[StandardColumns.AGE.value], errors='coerce')
        
    def fillRemainingColumns(self):
        self.output_dataframe[StandardColumns.STARTED_AT.value] = pd.to_datetime(self.output_dataframe[StandardColumns.STARTED_AT.value],format='ISO8601')
        self.output_dataframe[StandardColumns.COMPLETED_AT.value] = pd.to_datetime(self.output_dataframe[StandardColumns.COMPLETED_AT.value],format='ISO8601')

        time_spent_values = []
        for i, row in self.output_dataframe.iterrows():
            completed_at = row[StandardColumns.COMPLETED_AT.value]
            started_at = row[StandardColumns.STARTED_AT.value]

            if is_null_value(completed_at) or is_null_value(started_at):
                time_spent_values.append(NULL_VALUE)
            else:
                time_spent = (completed_at - started_at).seconds
                time_spent_values.append(time_spent)
        self.output_dataframe[StandardColumns.TIME_SPENT.value] = time_spent_values

    def additionalProcessing(self):
        self.output_dataframe[StandardColumns.SEX.value].replace(("Male","Female"), ("M","F"), inplace=True)