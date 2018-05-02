import logging

logger = logging.getLogger(__name__)

config_type = next(open('config_type')).lower().strip()
logger.info('Config_type: {}'.format(config_type))
if config_type == 'first':
# DB
    db_dbname = 'your_db_name'
    db_user = 'your_user_name'
    db_port = 'your_port'
    db_host = 'your_host'
    db_password = 'your_password'
else:
    raise ValueError('Incorrect config type: {}'.format(config_type))

#
sender_sleep_time = 1
sender_idle_sleep_time = 15
sender_reset_sender_after = 30

#
websim_corr_sleeptime = 1 # sec
websim_send_sleeptime = 3 # sec
websim_job_time = 1200 # sec
websim_concurrent_sleeptime = 60 # sec
websim_corr_progress_sleeptime = 30 # sec

#
stream_sleep_time = 20 # sec
max_alpha_length = 1500

#
telegram_token = 'your_token'
telegram_chat_id = 'your_chat_id'

#
import logging.config
logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'telegram': {
            'class': 'telegram_handler.TelegramHandler',
            'token': telegram_token,
            'chat_id': telegram_chat_id,
            'level': 'CRITICAL',
            'formatter': 'telegram',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
    },
    "loggers": {
        "": {
            #"level": "INFO",
            "level": "DEBUG",
            "handlers": ["telegram", 'console'],
            "propagate": "no"
        }
    },
    'formatters': {
        'console': {
            'format': '%(levelname)s: %(asctime)s ::: %(name)-13s: %(message)s (%(filename)s:%(lineno)d)',
        },
        'telegram': {
            'format': '%(message)s',
        }
    }
})
