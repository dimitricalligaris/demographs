from normalizer import *

class NormalizerFactory:

    @staticmethod
    def create_normalizer(input_dataframe, platform):
        if platform == 'Prolific' or platform == 'Prolific_dec2023':
            return ProlificNormalizer(input_dataframe)


