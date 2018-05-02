import click
import time
import db_handler
import websim
import logging
import telegram_handler

logger = logging.getLogger(__name__)

@click.command()
@click.option('--accid', required = True)
@click.option('--hour', required = True)
def main(accid, hour):
    db = db_handler.DBHandler()
    account = db.get_client_account(accid)
    ws = websim.WebSim(login = account[0], password = account[1])
    ws.authorise()
    while True:
        state = ws.get_state()
        count = ws.get_my_alphas_count()
        logger.critical('Total Alphas: {}; Total Alphas in Out of Sample: {}; Rank: {}; Score: {}; Level: {}.'.format(
            count['result']['NumAlphas']['NumTotalAlphas'],
            count['result']['NumAlphas']['NumOSAlphas'],
            state['result']['userData']['OverallRank'],
            state['result']['userData']['TotalScore'],
            state['result']['userData']['Level']))
        time.sleep(float(hour) * 60 * 60)

if __name__ == "__main__":
    main()