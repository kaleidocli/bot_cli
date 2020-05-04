

class varItem:
    def __init__(self, reloader=None):

        # Base
        if reloader: self.reloader = reloader

        # ITEM: Origin-Stats conversion table ===========================
        self.originStatsConversion = {
            'weight': [('weight', -2)],
            'str': [('str', 0.1), ('sta', 5)],
            'int': [('int', 0,1), ('sta', 5)],
            'sta': [('sta', -5), ('int', -0.1)],
            'mul': [('mul', 0.05), ('weight', 10)],
            'def': [('def', 5), ('str', -0.1), ('spd', -0.1)],
            'spd': [('spd', 0.1), ('def', -5)]
        }
        self.statsNameConversion = {            # For the database
            'weight': 'weight',
            'str': 'str',
            'int': 'intt',
            'sta': 'sta',
            'mul': 'multiplier',
            'def': 'defend',
            'spd': 'speed',
            'rng': 'range',
            'rng_min': 'range_min',
            'ste': 'stealth',
            'fir': 'firing_rate'
        }


