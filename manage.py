import click
import db_handler
import generator_handler
import websim
import top_handler
import getpass
import datetime
import top_configs
import logging
import alpha_stream_generator_handler

logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

@cli.command()
def reset_process():
    print 'resetting..'
    db = db_handler.DBHandler()
    db.reset_process()
    print 'done'

@cli.command()
def reset_sending():
    print 'resetting..'
    db = db_handler.DBHandler()
    db.reset_sending()
    print 'done'

@cli.command()
def reset_non_prior_sending():
    print 'resetting..'
    db = db_handler.DBHandler()
    db.reset_non_prior_sending()
    print 'done'

@cli.command()
@click.option('--top', required = True)
def top_reset(top):
    t = top_handler.TopHandler(1, top_configs.get_top_config(top))
    t.reset()
    print 'done'

@cli.command()
def reset_code():
    print 'resetting..'
    db = db_handler.DBHandler()
    db.reset_code()
    print 'done'

@cli.command()
def results():
    db = db_handler.DBHandler()
    db.view_results()

@cli.command()
def good_results():
    db = db_handler.DBHandler()
    db.view_good_results()

@cli.command()
@click.option('--top', required = True)
def top(top):
    db = db_handler.DBHandler()
    db.view_top_results(top_configs.get_top_config(top)['top_table_name'])

@cli.command()
def processing_status():
    db = db_handler.DBHandler()
    db.get_processing_status()

@cli.command()
@click.argument('code')
@click.option('--comment', default = '')
@click.option('--author', default = getpass.getuser())
def add_alpha(code, comment, author):
    db = db_handler.DBHandler()
    codeID = db.add_code(code, comment, author)
    db.add_sending(codeID)
    print 'done'

@cli.command()
@click.option('--accountID', default = '1')
def get_random_websim(accountid):
    db = db_handler.DBHandler()
    account = db.get_websim_account(accountid)
    ws = websim.WebSim(login = account[0], password = account[1])
    ws.authorise()
    print ws.get_random()

@cli.command()
@click.option('--accountID', default = '1')
@click.option('--n', default = '1')
def add_random_websim(accountid, n):
    db = db_handler.DBHandler()
    account = db.get_websim_account(accountid)
    ws = websim.WebSim(login = account[0], password = account[1])
    ws.authorise()
    comment = 'N:{} acc:{} '.format(n, accountid)
    for i in xrange(int(n)):
        code = ws.get_random()
        codeID = db.add_code(code, comment, 'websim random')
        db.add_sending(codeID)

@cli.command()
@click.option('--gen', required = True)
@click.option('--n', default = '1')
def add_gen_alpha(gen, n):
    gh = generator_handler.GeneratorHandelr()
    gh.generate(gen, n)

@cli.command()
@click.option('--n', default = 1)
def run_stream_generator(n):
    sh = alpha_stream_generator_handler.AlphaStreamGeneratorHandler()
    for _ in range(n):
        sh.add_stream()
    sh.loop()

@cli.command()
@click.option('--sid', required = True)
def detailed(sid):
    db = db_handler.DBHandler()
    db.detailed(sid)

@cli.command()
def reset_db():
    logger.info('Data Base resetting...')
    db = db_handler.DBHandler()
    db.reset()
    f = open('generators/iter0alphas','r')
    for code in f:
        codeID = db.add_code(code[:-1], 'iter0alphas', 'iter0alphas')
        logger.info(codeID[0])
        db.add_sending(codeID)
    f.close()
    logger.info('Done')

@cli.command()
@click.option('--accid', required = True)
def state(accid):
    db = db_handler.DBHandler()
    account = db.get_client_account(accid)
    ws = websim.WebSim(login = account[0], password = account[1])
    ws.authorise()
    state = ws.get_state()
    count = ws.get_my_alphas_count()
    logger.critical('Total Alphas: {}; Total Alphas in Out of Sample: {}; Rank: {}; Score: {}; Level: {}.'.format(
        count['result']['NumAlphas']['NumTotalAlphas'],
        count['result']['NumAlphas']['NumOSAlphas'],
        state['result']['userData']['OverallRank'],
        state['result']['userData']['TotalScore'],
        state['result']['userData']['Level']))

@cli.command()
def log_test():
    logger.critical('Telegram logging test')

if __name__ == '__main__':
    cli()
