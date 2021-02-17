from anon_etaamb import *

pt = prepare("Considérant les concertations entre les gouvernements des entités fédérées et les autorités Guadeloupe fédérales compétentes Jean Yves Daniel")
tk = tokenize(pt)
sc = multi_score("french", tk)

from anon_etaamb import *

run(
    "Considérant les concertations entre les gouvernements des entités fédérées et les autorités Guadeloupe fédérales compétentes Jean Yves Daniel",
    {'lang': 'french'}
)
