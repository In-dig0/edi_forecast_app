import logging
from utils.config import LOG_FILE, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT

def setup_logger(name):
    """
    Configura e restituisce un logger con il nome specificato.
    Tutti i logger scrivono sullo stesso file applog.log.
    
    Args:
        name (str): Nome del logger (es. "login_page", "auth", ecc.)
    
    Returns:
        logging.Logger: Logger configurato
    """
    logger = logging.getLogger(name)
    
    # Evita di aggiungere handler duplicati
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # Handler per file
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    
    # Handler per console (opzionale, utile per debug)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Aggiungi handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

