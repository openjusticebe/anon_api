import re
from collections import namedtuple
import logging
logger = logging.getLogger(__name__)

Mask = namedtuple('Mask', 'name mask replace')

MASKS = [
    # Yes, this is not optimal, but it works for now
    # Mask('email', r'\b[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}\b', '[ email@example.com ]'),
    Mask('email', r'\b[a-z0-9][a-z0-9._\-+]+[a-z0-9][@][\w\-._\-+]+[.]\w{2,3}\b', '[ email@example.com ]'),
    Mask('RN', r'\b[0-9]{2}[.\-]{0,1}[0-9]{2}[.\-]{0,1}[0-9]{2}[.\-]{0,1}[0-9]{3}[.\-]{0,1}[0-9]{2}\b', '[ XXXX ]'),
    Mask('IBAN', r'\b[A-Z]{2}[0-9]{2}(?:[ ]?[0-9]{4}){3,4}(?:[ ]?[0-9]{1,2})?\b', '[ BE03 1111 2222 3333 5555 ]'),
    Mask('company', r'\b(BE)?0?\d{3}[.\- ]?\d{3}[.\- ]?\d{3}\b', '[ XXXX ]'),
    Mask('phonenumber', r'\b04?(?:[ \/]?\d{2,3}){3,5}\b', '[ XXXX ]'),
    # Mask('phonenumber', r'0\d{1}[\.\/\\ ][\.\/\\ 0-9]', '[ XXXX ]'),
    # Mask('mobilenumber', r'04\d{8}', '[ XXXX ]'),
    # Mask('mobilenumber', r'\+\d{8,9}', '[ XXXX ]'),
    # Matches too much
    # Mask('VAT', r'[A-Za-z]{2,4}(?=.{2,12}$)[-_ 0-9]*(?:[a-zA-Z][-_ 0-9]*){0,2}', '[ BE0123456789 ]'),
    # tel mask : (\+|00)?(32\d{2,3}|0\d{2}|0\d)(?:[ \/\\\-]?[0-9]*){2,3}
]


def run(text, _params):
    """
    Run and replace directly
    """
    for m in MASKS:
        text = re.sub(m.mask, m.replace, text, flags=re.IGNORECASE)
    return text, ['Mask replacement OK']


def parse(text, _params):
    """
    Find and return possible matches
    """
    matches = {}
    log = []
    idx = 0
    for m in MASKS:
        match = re.finditer(m.mask, text, flags=re.IGNORECASE)
        idx += 1
        if match:
            words = [x.group(0) for x in match]
            if len(words) == 0:
                continue
            msg = f"Found value type {m.name} : {words}"
            log.append(msg)
            el_id = re.sub(r'[\W_]+', '-', ''.join(words))
            matches[el_id] = {
                'words': ' '.join(words),
                'text': [x for x in words if x],
                'id': idx,
                'type': m.name,
            }
            # check.append(match.group(0))
        else:
            print(f"{m.name} did not match")

    return matches, log
