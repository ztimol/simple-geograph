from .core import Transformer
from .controllers import Neo4jController


class GeoGraph:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.network_node_labels = []

    def transform(self, geo_data):
        t = Transformer()
        t.transform(geo_data)

        self.nodes = t.nodes
        self.edges = t.edges

    def to_neo4j(self, **kwargs):

        db_config = kwargs["db_config"]

        nc = Neo4jController(
            **db_config,
            nodes=self.nodes,
            edges=self.edges,
            network_node_labels=self.network_node_labels,
        )
        nc.to_neo4j()
