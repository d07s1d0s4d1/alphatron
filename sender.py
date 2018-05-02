import click
import time
import db_handler
import top_handler
import websim
import config
import traceback
import numpy as np
import logging
import telegram_handler
import submitter

logger = logging.getLogger(__name__)

class Sender(object):
    def __init__(self, accountID):
        self.accountID = accountID
        self.db = db_handler.DBHandler()

        self.tops = top_handler.AllTopHandler(accountID)

        account = self.db.get_websim_account(accountID)
        self.ws = websim.WebSim(login = account[0], password = account[1])
        self.ws.authorise()
        self.sb = submitter.Submitter(accountID)

    def process_sending(self, sending, accountID):
        sendingID = sending[3]

        res = self.ws.send_alpha(sending[0], delay = sending[4], decay = sending[5],
                opneut = sending[6], backdays = sending[7], univid = sending[8], optrunc = sending[9])
        #print res
        if res == 'CANCEL':
            self.db.set_process_status(sendingID, accountID, 'skipped')
            return

        self.db.save_result(sendingID, res)
        self.db.set_process_status(sendingID, accountID, 'done')
        self.tops.try_to_add_to_all_tops(sendingID)
        self.sb.submit_alpha(sendingID)

    def loop(self):
        sending = self.db.get_sending_to_exec(self.accountID)
        logger.info('Sending to do: {}'.format(sending))
        if not sending:
            return 'idle'
        self.process_sending(sending, self.accountID)
        return 'done'


@click.command()
@click.option('--accountID', default = '1', help = 'websim account id for simulating alphas')
def main(accountid):
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
                time.sleep(np.random.rand() * config.sender_sleep_time)
                n += 1
                if n >= config.sender_reset_sender_after:
                    sender = None
        except Exception as e:
            logger.critical('Got an exception: {}'.format(e))
            traceback.print_exc()
            sender = None

if __name__ == "__main__":
    main()
