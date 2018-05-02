import click
import db_handler
import websim
import top_configs
import logging
import telegram_handler

logger = logging.getLogger(__name__)

class Submitter(object):
    def __init__(self, accountID, top_config = None):
        self.db = db_handler.DBHandler()
        self.accountID = accountID
        self.top_config = top_config

        account = self.db.get_client_account(accountID)
        self.ws = websim.WebSim(login = account[0], password = account[1])
        self.ws.authorise()

    def submit_alpha(self, sendingID):
        logger.info('Submitting sendingID: {}'.format(sendingID))
        alphaID = self.db.sendingID_to_alphaID(sendingID)
        logger.info(alphaID)
        res = self.ws.check_submission(alphaID)
        if not res['status']:
            self.db.set_submit_status(sendingID, self.accountID, 'false', res['error'])
            logger.info(res['error'])
        else:
            res = self.ws.submit(alphaID)
            if not res['status']:
                self.db.set_submit_status(sendingID, self.accountID, 'false', res['error'])
                logger.info(res['error'])
            else:
                self.db.set_submit_status(sendingID, self.accountID, 'true', res['result']['response'])
                logger.critical('One more alpha was submitted!!!; Code: {}; Comment: {}'.format(self.db.get_sending_result(sendingID)['code'], \
                    res['result']['response']))

    def submit_top(self):
        top = self.db.get_unsubmit_top_alphas(self.top_config['top_table_name'])
        for i, sendingID in enumerate(top):
            logger.info('Status: {} of {} done;'.format(i, len(top)))
            self.submit_alpha(sendingID)

@click.command()
@click.option('--accountID', default = '1', help = 'websim account id for submitting alphas')
def main(accountid):
    logger.info('Submit processing..')
    submitter = Submitter(accountid, top_configs.get_top_config('top'))
    submitter.submit_top()
    logger.info('Done')

if __name__ == "__main__":
    main()