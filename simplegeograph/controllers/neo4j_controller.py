from collections import defaultdict
from neomodel import db
from neomodel import config as neo_config


class Neo4jController:

    def __init__(self, **kwargs):
        db_user = kwargs["db_user"]
        db_password = kwargs["db_password"]
        db_uri = kwargs["db_uri"]

        self.nodes = kwargs["nodes"]
        self.edges = kwargs["edges"]
        self.network_node_labels = kwargs["network_node_labels"]

        neo_config.DATABASE_URL = f"bolt://{db_user}:{db_password}@{db_uri}"

    def to_neo4j(self):
        self.create_line_nodes()
        self.create_line_node_edges()

    def create_line_nodes(self):

        for node in self.nodes:
            point = node.pop("geom")
            node["geom_x"] = point.x
            node["geom_y"] = point.y

        query = f"""UNWIND $nodes AS node
         MERGE (n:NetworkNode {{node_key: node.node_key}})
         ON CREATE
             SET n.createdAt = timestamp()
             {self.set_node_labels()}
         SET
         n.node_key = node.node_key
         RETURN n
         """

        db.cypher_query(query, {"nodes": self.nodes})

    def set_node_labels(self):
        subquery = ""
        for node_label in self.network_node_labels:
            subquery += f"""FOREACH (ignoreMe IN CASE
            WHEN '{node_label}' IN node.node_labels
            THEN [1] ELSE [] END |
            SET n:{node_label})\n"""

        return subquery

    def create_line_node_edges(self):

        for edge in self.edges:
            line_segment_geom = edge.pop("line_segment_geom")
            # edge["line_segment_wkb_hex"] = line_segment_geom.wkb_hex

        edges_by_label = defaultdict(list)
        for edge in self.edges:
            edges_by_label[edge["edge_label"]].append(edge)

        for label, edges_subset in edges_by_label.items():
            query = f"""
            UNWIND $edges AS edge
            MATCH (from:NetworkNode {{node_key: edge.from_node_key}})
            MATCH (to:NetworkNode {{node_key: edge.to_node_key}})
            MERGE (from)-[r:{label}]->(to)
            ON CREATE SET r.createdAt = timestamp()
            SET r += edge.attributes
            RETURN count(r) AS relationships_created
            """
            db.cypher_query(query, {"edges": edges_subset})
