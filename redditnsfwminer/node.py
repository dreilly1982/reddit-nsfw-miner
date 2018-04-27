import bs4
import logging
import json
import requests
import re

from minemeld.ft.basepoller import BasePollerFT

LOG = logging.getLogger(__name__)

class Miner(BasePollerFT):
    def configure(self):
        super(Miner, self).configure()

        self.polling_timeout = self.config.get('polling_timeout', 20)
        self.verify_cert = self.config.get('verify_cert', True)

        self.url = 'https://www.reddit.com/r/NSFW411/wiki/index'

    def _build_iterator(self, item):
        rkwargs = dict(
                stream = False,
                verify = self.verify_cert,
                timeout = self.polling_timeout,
                cookies = {'over18': '1'}
        )

        s = requests.Session()

        s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})

        r = s.get(
                self.url,
                **rkwargs
        )

        try:
            r.raise_for_status()
        except:
            LOG.debug('%s - exception in request: %s %s',
                    self.name, r.status_code, r.content)
            raise
        result = []
        pattern = re.compile("\/r\/.*")
        soup = bs4.BeautifulSoup(r.content, 'lxml')
        for tr in soup.find_all('tr'):
            a = tr.find('a')
            if a and pattern.match(a.text):
                result.append(a.text)

        return result

    def _process_item(self, item):
        retval = []
        if item is None:
            LOG.error('%s - no subreddit', self.name)
            return retval
        indicator = 'www.reddit.com{}/*'.format(item)
        value = {
                'type': 'URL',
                'confidence': '100'
                }
        retval.append([indicator, value])
        indicator = 'www.reddit.com{}'.format(item)
        retval.append([indicator, value])

        return retval
