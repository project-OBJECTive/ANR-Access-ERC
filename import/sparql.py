import requests, os
from typing import List, Callable
from requests.auth import HTTPBasicAuth

from errors import HTTPError
from prefix import Prefix


class SPARQL:

    name: str
    url: str
    username: str
    password: str
    prefixes: List[Prefix]


    def __init__(self, url: str, username: str, password: str) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.prefixes = []

    def get_prefixes(self) -> List[Prefix]:
        return [prefix for prefix in self.prefixes if prefix.short != 'base']

    def prepare_uri(self, supposed_uri: str) -> str:

        # If it is a string with language
        if (supposed_uri.startswith("'") and "'@" in supposed_uri):
            return supposed_uri

        # If None is given, make the call transparent
        if not supposed_uri: return None
        
        # Make it a string 
        supposed_uri = str(supposed_uri)

        # Make it work when we have a real URI
        if supposed_uri.startswith('http'):
            return f"<{supposed_uri}>"

        # Check if the given URI has a known prefix: if yes, nothing to do
        if ":" in supposed_uri:
            if self.is_known_prefix(supposed_uri[0:supposed_uri.index(':')]):
                return supposed_uri

        # Check if it is a value: if yes, nothing to do
        if (supposed_uri.startswith("'") and supposed_uri.endswith("'")) or (supposed_uri.startswith('"') and supposed_uri.endswith('"')):
            return supposed_uri
        
        # Check if it is the "a" keyword: if yes, nothing to do 
        if supposed_uri == "a": 
            return supposed_uri

        # Check if it is a variable: if yes, nothing to do
        if supposed_uri.startswith('?'):
            return supposed_uri

        # Finally, it then should be a real URI, adds the "<" and ">" if needed
        uri = supposed_uri.strip()
        if not uri.startswith("<"): uri = "<" + uri
        if not uri.endswith(">"): uri = uri + ">"
        return uri


    def prepare_triple(self, triple: tuple[str, str, str]) -> str:
        try:
            return f"{self.prepare_uri(triple[0])} {self.prepare_uri(triple[1])} {self.prepare_uri(triple[2])} ."
        except Exception:
            raise Exception(f'Failed to prepare triple: {triple}')


    def is_known_prefix(self, supposed_prefix: str) -> bool:
        all_prefixes_short = list(map(lambda p: p.short, self.prefixes))
        return supposed_prefix in all_prefixes_short


    def unroll_uri(self, short_uri: str) -> str:
        long_uri = short_uri
        for prefix in self.prefixes:
            long_uri = prefix.lengthen(long_uri)
        return long_uri

    def run(self, query: str) -> None | list[dict]:
        """Make a HTTP POST request with all needed params to the SPARQL endpoint."""

        if os.getenv('MODE') == "debug":
            # Prettifying query: un-tab to the right the query in case of debug mode
            query_lines = query.split('\n')
            for line in query_lines:
                if line.strip() == '': continue
                index = len(line) - len(line.lstrip())
                break
            query = '\n'.join(list(map(lambda line: line[index:], query_lines)))

            # Add prefixes
            query = '\n'.join(list(map(lambda prefix: prefix.to_sparql(), self.prefixes))) + '\n' + query

            # DEBUG
            print('==============')
            print(query)
        else:
            # Add prefixes
            query = '\n'.join(list(map(lambda prefix: prefix.to_sparql(), self.prefixes))) + '\n' + query
            # Strip all lines
            query = '\n'.join(list(map(lambda line: line.strip(), query.split('\n'))))

        # Prepare the request
        data = {'query': query}
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/sparql-results+json'}
        auth = HTTPBasicAuth(self.username, self.password) if self.username else None

        # Execute the request
        response = requests.post(self.url, data=data, headers=headers, auth=auth)
        try:
            response.raise_for_status()  # Raise error for bad responses
        except requests.exceptions.HTTPError as error:
            msg = f"HTTP code {str(error)}.\n"
            msg += error.response.text
            raise HTTPError(msg)


        # If there is a response, parse and transform into a list of dict
        response_json = response.json()
        if 'results' in response_json and 'bindings' in response_json['results']:
            rows = []
            for row in response_json['results']['bindings']:
                obj: dict = {}
                for key in row.keys(): # For Each columns
                    type = row[key].get('type')
                    datatype = row[key].get('datatype')
                    value = row[key].get('value')
                    if type == 'uri':
                        for prefix in self.prefixes: # For each saved prefix, replace by its short version
                            value = prefix.shorten(value)
                    elif type == 'literal' and datatype == 'http://www.w3.org/2001/XMLSchema#integer':
                        value = int(value)
                    obj[key] = value
                rows.append(obj)

            return rows


    def insert(self, triples: List[tuple] | tuple, graph_uri: str | None = None, eta_fct: Callable = None, with_inverse=True) -> None:
        """From a list (or unique) of triples, insert them (it) in the endpoint, in the given graph."""

        # If only a single triple is given, transform it into a list
        if isinstance(triples, tuple):
            triples = [triples]

        # Since inserts can be pretty huge, here we split them
        # in "smaller insert" of maximum 1k triples.

        # Add-on to make them visible on Geovistory
        if with_inverse:
            blacklist = ['rdf:type', 'rdfs:label', 'rdfs:comment']
            all_triples = []
            for triple in triples:
                if triple[1] not in blacklist and not triple[2].startswith("'"): 
                    all_triples.append((triple[2], triple[1], triple[0]))
                all_triples.append(triple)
        else:
            all_triples = triples

        # Chunked all triples
        chunk_size = 1000
        chunked_triples = [all_triples[i: i + chunk_size] for i in range(0, len(all_triples), chunk_size)]

        # Prepare the query
        graph_sparql_open = "GRAPH " + self.prepare_uri(graph_uri) + " {" if graph_uri else ""
        graph_sparql_close = "}" if graph_uri else ""
        
        for small_triples in chunked_triples:
            # Transform the triples into strings
            triples_str = '\n                        '.join(map(lambda triple: self.prepare_triple(triple), small_triples))

            # Prepare the query
            text = """
                # SPARQL.insert()
                INSERT DATA {
                    """ + graph_sparql_open + """
                        """ + triples_str + """
                    """ + graph_sparql_close + """
                }
            """

            # Insert the triples in the endpoint
            self.run(text)

            # Eta Feedback
            if eta_fct:
                eta_fct()


    def delete(self, triples: List[tuple] | tuple, graph_uri: str | None = None) -> None:
        """
        From a list (or unique) of triples, delete them (it) from the endpoint, from the given graph.
        Triples can here be either full URIs, or variables (to make deletion rules)
        """

        # If only a single triple is given, transform is into a list
        if isinstance(triples, tuple):
            triples = [triples]

        # Transform the triples into strings
        triples_str = '\n                    '.join(map(lambda triple: self.prepare_triple(triple), triples))

        # Prepare query
        graph_sparql_open = "GRAPH " + graph_uri + " {" if graph_uri else ""
        graph_sparql_close = "}" if graph_uri else ""
        text = """
            # SPARQL.delete()
            DELETE WHERE {
                """ + graph_sparql_open + """
                    """ + triples_str + """
                """ + graph_sparql_close + """
            }
        """

        # Execute
        self.run(text)

    
    def dump(self) -> str:
        """Make a full endpoint dump as a n-Quads file."""

        # Prepare the request
        url = self.url + '/statements'
        headers = {"Accept": "application/n-quads"}
        auth = HTTPBasicAuth(self.username, self.password) if self.username else None

        # Make the request
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise error for bad responses

        # Return n-quads as string
        return response.text
    

    def upload_nquads(self, nquad_content: str) -> None:
        line_number = 10000
        lines = nquad_content.splitlines()
        chunks = ['\n'.join(lines[i:i + line_number]) for i in range(0, len(lines), line_number)]

        for i, chunk in enumerate(chunks):
            print(f"> Uploading ({line_number * i} / {len(lines)})")
            self.upload_nquads_chunk(chunk)


    def upload_turtle(self, turtle_content: str, named_graph_uri: str) -> None:

        line_number = 10000
        lines = turtle_content.splitlines()

        # Extract prefixes
        prefixes = []
        triples = []
        for line in lines:
            if line.strip().startswith('@prefix'):
                prefixes.append(line)
            else:
                triples.append(line)
        
        prefixes = '\n'.join(prefixes) + "\n"
        chunks = ['\n'.join(triples[i:i + line_number]) for i in range(0, len(triples), line_number)]

        for i, chunk in enumerate(chunks):
            print(f"> Uploading {line_number} ({line_number * i } / {len(triples)})", end=' ')
            self.upload_turtle_chunk(prefixes + chunk, named_graph_uri)
            print('Done')



    def upload_nquads_chunk(self, nquad_content: str) -> None:
        """
        Function to import raw n-Quads data (as string) into the endpoint.
        As n-quads already include the graph, data can't be imported into a specified graph.
        """
        raise Exception(f'Method <upload_nquads> not implemented in {self.name}')
    

    def upload_turtle_chunk(self, turtle_content: str, named_graph_uri: str) -> None:
        """
        Function to import raw turtle data (as string) into the given graph.
        Specifying the graph is mandatory, otherwise import it into default graph.
        """
        raise Exception(f'Method <upload_turtle> not implemented in {self.name}')
    