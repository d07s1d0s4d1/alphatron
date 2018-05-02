import click
import json
import copy
import time
import db_handler
import config
import logging

logger = logging.getLogger(__name__)

class CodeToSending(object):
    def __init__(self):
        self.db = db_handler.DBHandler()

    def apply_params(self, code, params):
        self.db.add_sending(code[0], **params)

    def process(self, code):
        logger.info('Processing: {}'.format(code))

        if not code[2]:
            self.apply_params(code, {})
            return

        params_info = json.loads(code[2])
        result = []
        def extract_param(params, used, priority = -10):
            if len(used) == len(params_info):
                params_ = copy.deepcopy(params)
                params_['priority'] = priority
                result.append(params_)
            for param in params_info:
                if param in used:
                    continue
                for i, value in enumerate(params_info[param]):
                    params_ = copy.deepcopy(params)
                    params_[param] = value
                    extract_param(params_, used + [param], priority + i)
                break
        extract_param(dict({}), [])
        logger.info('Params variants: {}'.format(len(result)))
        for params in result:
            self.apply_params(code, params)

    def loop(self):
        code = self.db.get_code_to_sending()
        if not code:
            return 'idle'
        self.process(code)
        return 'done'


@click.command()
@click.option('--accountID', default = '1', help = 'websim account id for simulating alphas')
def main2(accountid):
    sender = None
    n = 0
    while True:
        if not sender:
            sender = Sender(accountid)
            n = 0

        try:
            res = sender.loop()

            if res == 'idle':
                time.sleep(config.sender_idle_sleep_time)
            else: # 'done'
                time.sleep(config.sender_sleep_time)
                n += 1
                if n >= config.sender_reset_sender_after:
                    sender = None
        except Exception as e:
            logging.critical('Got an exception: {}'.format(e))
            sender = None

@click.command()
def main():
    code_to_sending = CodeToSending()
    while True:
        code_to_sending.loop()
        time.sleep(1)

if __name__ == "__main__":
    main()
