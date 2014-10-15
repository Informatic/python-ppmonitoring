import requests
import bs4

g_session = None


class ParcelLookupError(LookupError):
    pass


class Parcel(object):
    """
    An object depicting parcel stored in PP E-Monitoring system

    Attributes:
        number     Parcel tracking number provided during instantiation
        attributes Dictionary of parcel attributes
        events     List of dictionary objects representing events associated
                   with the parcel

        language   Language to fetch data in

    Fetched data (attributes and events) are simply parsed tables, so keep in
    mind it may break in any unspecified way at any time. Attributes keys are
    lowercased headers with whitespaces replaced into underscores.
    """
    number = None
    attributes = None
    events = None

    session = None
    base_url = 'http://emonitoring.poczta-polska.pl'
    language = 'en'

    def __init__(self, number, language=None, fetch=True):
        """Create new parcel object and automatically fetch the data, if not
        specified otherwise.
        """
        if language:
            self.language = language

        self.number = number

        if fetch:
            self.fetch()

    def fetch(self):
        """Do actual data fetch filling self.attributes and self.events."""
        global g_session

        # By default one session for all requests is preferred
        if not self.session:
            if not g_session:
                g_session = self.prepare_session()
            self.session = g_session

        if not 'PHPSESSID' in self.session.cookies:
            self.session.get(self.base_url, params={
                'numer': self.number,
                'lang': self.language
                })

        sessid = self.session.cookies['PHPSESSID']

        resp = self.session.post(self.base_url + '/wssClient.php', {
            's': sessid,
            'n': self.number,
            'l': self.language
            })

        soup = bs4.BeautifulSoup(resp.text)

        try:
            trs = soup.find('table', id='sledzenie_td').find_all('tr')
        except:
            raise ParcelLookupError()

        self.attributes = dict((
            t.find_all('td')[0].text.lower().strip()
                               .replace(':', '').replace(' ', '_'),
            t.find_all('td')[1].text.strip()
            ) for t in trs if len(t.find_all('td')) == 2)

        # yip, zadarzenia.
        trs = soup.find('table', id='zadarzenia_td').find_all('tr')
        self.events = [
            dict(zip(['description', 'time', 'location'],
                     map(lambda o: o.text.strip(), t.find_all('td'))
                     )) for t in trs if len(t.find_all('td')) == 3]

    def prepare_session(self):
        """Return new requests Session instance to be used while making
        requests."""
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Intel Mac OS X 10.6; '
                          'rv:7.0.1) Gecko/20100101 Firefox/7.0.1'})

        return s

if __name__ == '__main__':
    #p = Parcel('<parcel tracking number>')
    p = Parcel('')
    print p.attributes
    print p.events
