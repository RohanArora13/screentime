import logging
import logging.config
import time
import loggly.handlers

logging.config.fileConfig('loggly.conf')
logging.Formatter.converter = time.gmtime
logger = logging.getLogger('newlog')



logger.info('Test log')
logger.debug('Test log')