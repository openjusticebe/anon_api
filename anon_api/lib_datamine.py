import datetime
import re

dt = datetime.datetime.now().date()
YEAR_MIN = 1950
YEAR_MAX = int(dt.strftime("%Y"))

# List of language-exclusive stopwords
FR_STOPS = ['si', 'sans', 'pourquoi', 'mot', 'étions', 'dans', 'dehors', 'elle', 'quand', 'vont', 'notre', 'ça', 'état', 'tout', 'parce', 'étaient', 'où', 'maintenant', 'bon', 'début', 'avant', 'sien', 'elles', 'tous', 'être', 'mon', 'sur', 'donc', 'devrait', 'soyez \tsujet', 'ton', 'ils', 'est', 'il', 'car', 'que', 'tandis', 'mes', 'eu', 'été', 'par', 'son', 'avoir', 'là', 'pas', 'nommés', 'seulement', 'ces', 'ou', 'comme', 'dos', 'essai', 'les', 'vu', 'chaque', 'sa', 'votre', 'peu', 'faites', 'au', 'pour', 'ici', 'et', 'aucuns', 'le', 'mien', 'doit', 'depuis', 'sont', 'quels', 'quel', 'la', 'tes', 'alors', 'tellement', 'quelle', 'même', 'sous', 'autre', 'fait', 'trop', 'peut', 'plupart', 'aussi', 'tu', 'comment', 'juste', 'leur', 'ni', 'tels', 'vous', 'nous', 'encore', 'ce', 'qui', 'moins', 'ci', 'dedans', 'mais', 'cela', 'ta', 'très', 'avec', 'fois', 'ceux', 'font', 'quelles', 'hors', 'ses', 'voient', 'ma']
NL_STOPS = ['we', 'zou', 'wat', 'af', 'kan', 'hun', 'dat', 'zij', 'nog', 'uit', 'hem', 'ze', 'me', 'tot', 'wel', 'dit', 'te', 'nu', 'men', 'heb', 'ook', 'al', 'ons', 'een', 'hij', 'dan', 'is', 'met', 'of', 'bij', 'wij', 'hoe', 'had', 'zal', 'ik', 'zei', 'aan', 'zo', 'mij', 'het', 'van']
DE_STOPS = ['muß', 'wird', 'müßt', 'wir', 'und', 'sind', 'am', 'sonst', 'unter', 'eines', 'an', 'ein', 'ihr', 'mit', 'vom', 'werde', 'wohin', 'meine', 'weitere', 'einen', 'können', 'weiter', 'dass', 'euer', 'im', 'das', 'jeder', 'zur', 'mußt', 'es', 'nun', 'einem', 'der', 'sich', 'seid', 'einer', 'jedem', 'soweit', 'kannst', 'hier', 'deine', 'bin', 'über', 'vor', 'ist', 'müssen', 'wann', 'bei', 'kann', 'hattet', 'doch', 'eure', 'mein', 'dieser', 'ihre', 'den', 'hatten', 'sollt', 'unsere', 'warum', 'dieses', 'jeden', 'ja', 'machen', 'dies', 'auf', 'soll', 'sollst', 'wenn', 'sein', 'eine', 'jede', 'nach', 'dein', 'hinter', 'für', 'durch', 'aus', 'dort', 'musst', 'zum', 'bist', 'weshalb', 'da', 'sollen', 'auch', 'jedes', 'nicht', 'von', 'sie', 'werdet', 'bis', 'hatte', 'ich', 'oder', 'jenes', 'woher', 'werden', 'nein', 'jener', 'dadurch', 'deshalb', 'unser', 'wer', 'könnt', 'aber', 'sowie', 'wo', 'zu', 'seine', 'hattest', 'jetzt', 'dessen', 'darum', 'nachdem', 'wieder', 'wirst', 'daher', 'daß', 'wieso', 'dem', 'wie']


class DataMiner:
    year = None

    def __init__(self, text):
        self._text = text

    def enrich(self, obj):
        obj['year'] = self._getYear()
        obj['lang'] = self._getLang()

    def _getYear(self):
        m = re.findall(r"\d{4}", self._text)
        if not m:
            return None
        for y in m:
            y_int = int(y)
            if y_int > YEAR_MIN and y_int <= YEAR_MAX:
                return y

    def _getLang(self):
        scores = {
            'FR': self._langScore(FR_STOPS),
            'DE': self._langScore(DE_STOPS),
            'NL': self._langScore(NL_STOPS)
        }
        print(scores)
        return max(scores, key=lambda key: scores[key])

    def _langScore(self, stops):
        score = 0
        for s in stops:
            if re.search(fr"\W{s}\W", self._text):
                score += 1
        return score / len(stops)
