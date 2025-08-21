
class Prefix:

    short: str
    long: str


    def __init__(self, short: str, url: str) -> None:
        self.short = short
        self.long = url


    def to_sparql(self) -> str:
        """Return a SPARQL ready string for the prefix."""
        return f"PREFIX {self.short}: <{self.long}>"
    

    def to_turtle(self) -> str:
        """Return a Turtle ready string for the prefix."""
        return f"@prefix {self.short}: <{self.long}> ."


    def shorten(self, uri: str) -> str:
        """Replace the given long uri by its short prefix, if present."""
        if self.long in uri:
            if uri.startswith('<'): uri = uri[1:]
            if uri.endswith('>'): uri = uri[:-1]
            return uri.replace(self.long, self.short + ':')
        return uri
    

    def lengthen(self, short: str) -> str:
        """Replace the given short uri by its explicit version."""
        return str(short).replace(self.short + ':', self.long)
    

    def to_dict(self) -> dict[str, str]:
        """Convert the Prefix instance to a dictionary."""
        return {
            "short": self.short,
            "long": self.long
        }
    

    @staticmethod
    def from_dict(obj: dict[str, str]) -> 'Prefix':
        """Create an Prefix instance from a dictionary."""
        return Prefix(obj['short'], obj['long'])
    

prefixes = [
    Prefix('sh', 'http://www.w3.org/ns/shacl#'),
    Prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'), 
    Prefix('rdfs', 'http://www.w3.org/2000/01/rdf-schema#'),
    Prefix('owl', 'http://www.w3.org/2002/07/owl#'),
    Prefix('crm', 'http://www.cidoc-crm.org/cidoc-crm/'),
    Prefix('frbroo', 'https://www.iflastandards.info/fr/frbr/frbroo#'),
    Prefix('geov', 'https://ontome.net/ontology/'),
    Prefix('sdh', 'https://sdhss.org/ontology/core/'),
    Prefix('sdh-slc', 'https://sdhss.org/ontology/social-life-core/'),
    Prefix('sdh-shacl', 'https://sdhss.org/shacl/profiles/'),
    Prefix('sdh-act', 'https://sdhss.org/ontology/human-activity/'),
    Prefix('crm-sup', 'https://sdhss.org/ontology/crm-supplement/'),
]