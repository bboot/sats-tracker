from environs import Env
import json
try:
    from lxml import etree, html
except:
    print("If `pip install lxml` doesn't work, then you won't"
          " be able to use Bitcoin Explorer in place of Electrum")
import requests

class Explorer:
    url = ''
    def __init__(self, url=None):
        if url:
            self.url = url
        if not self.url:
            env = Env()
            env.read_env()
            Explorer.url = env.str('EXPLORER', 'http://umbrel.local:3002')

    def lookup(self, query):
        '''
        For now, we only lookup addresses, transactions, and
        block heights
        '''
        if not (1 <= len(query) <= 200):
            return None
        if ((query.startswith('bc1') and (
            len(query) == 42 or len(query) == 62)) or (query[0] in '31') and (
                 len(query) <= 34 and len(query) >= 26)):
            return self.query("/address/" + query)
        elif len(query) <= 7:
            return self.query("/api/block/" + query)
        elif len(query) == 64:
            # assume it's a hash of block or txn
            return self.query("/api/tx/" + query)
        print(f"I don't know how to look up {query}")
        return None

    def query(self, endpoint):
        '''
        E.g.: /address/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
        '''
        #print(f'querying {self.url + endpoint}')
        response = requests.get(self.url + endpoint)
        if '/api/' in endpoint:
            return response.json()
        return self.extract_json(response.content)

    def extract_json(self, content):
        '''
        Returns <code class="json"> objects parsed into dicts
        XXX Does not check if the code element is actually of
        class "json"
        '''
        doc = html.fromstring(content)
        items = []
        for elt in doc.iter('code'):
            try:
                text = elt.text_content()
                items.append(json.loads(text))
            except:
                continue
        return items

    def dump_html(self, doc):
        return etree.tostring(doc, encoding='unicode', pretty_print=True)
