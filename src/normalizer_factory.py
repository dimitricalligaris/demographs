from normalizer import *

class NormalizerFactory:

    @staticmethod
    def create_normalizer(input_dataframe, platform):
        if platform == 'Prolific':
            return ProlificNormalizer(input_dataframe)


