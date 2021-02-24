import re
from collections import namedtuple
import logging
logger = logging.getLogger(__name__)

Mask = namedtuple('Mask', 'name mask replace')

MASKS = [
    # Yes, this is not optimal, but it works for now
    Mask('email', r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}', '[ email@example.com ]'),
    Mask('RN', r'[0-9]{2}[.\- ]{0,1}[0-9]{2}[.\- ]{0,1}[0-9]{2}[.\- ]{0,1}[0-9]{3}[.\- ]{0,1}[0-9]{2}', '[ XXXX]'),
    Mask('IBAN', r'([A-Z]{2}[ \-]?[0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30}$)((?:[ \-]?[A-Z0-9]{3,5}){2,7})([ \-]?[A-Z0-9]{1,3})?', '[ BE03 A11A B2B2 3C3C D44D ]'),
    Mask('Company Registration', r'(BE)?0?\d{3}[.\- ]?\d{3}[.\- ]?\d{3}', '[ XXXX ]'),
    Mask('Phone_national', r'0[0-9\-\\\/ \.]{6,15}\d{2}', '[ XXXX ]'),
    Mask('Phone_international', r'00[0-9\-\\\/ \.]{6,15}\d{2}', '[ XXXX ]'),
    Mask('Phone_international2', r'\+[0-9\-\\\/ \.]{6,15}\d{2}', '[ XXXX ]'),
    # Matches too much
    # Mask('VAT', r'[A-Za-z]{2,4}(?=.{2,12}$)[-_ 0-9]*(?:[a-zA-Z][-_ 0-9]*){0,2}', '[ BE0123456789 ]'),
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
    check = []
    matches = []
    log = []
    idx = 0
    for m in MASKS:
        match = re.search(m.mask, text, flags=re.IGNORECASE)
        idx += 1
        if match and match.group(0) not in check:
            msg = f"Found value type {m.name} : {match.group(0)}"
            log.append(msg)
            matches.append({
                'words': match.group(0),
                'text': match.group(0),
                'id': idx,
                'type': m.name,
            })
            check.append(match.group(0))
        else:
            print(f"{m.name} did not match")

    return matches, log
