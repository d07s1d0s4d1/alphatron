import itertools
import importlib
import db_handler
import json
import logging

logger = logging.getLogger(__name__)

class GeneratorHandelr(object):
    def __init__(self):
        self.db = db_handler.DBHandler()

    def generate(self, generator_name, n = 1):
        generator = importlib.import_module(generator_name)
        i = 0
        logger.info('Begin')
        for alpha in itertools.islice(generator.get(), int(n)):
            self.db.add_code(alpha['code'], params_info = json.dumps(alpha['params_info']), comment = '{} {}'.format(generator.short_name, n))
            i += 1
            logger.info('{} of {} done'.format(i, n))

