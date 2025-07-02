from copy import deepcopy
from collections import defaultdict
from sqids import Sqids
from shapely import Point, line_locate_point, ops
from .models import GeoTransformListModel
from .constants import (
    NETWORK_NODE__LABEL,
    POINT_ASSET_NODE__LABEL,
    LINE_NODE__LABEL,
    LINE_JUNCTION__LABEL,
    LINE_END__LABEL,
)


class Transformer:
    def __init__(self):

        self.nodes = []
        self.edges = []
        self.network_node_labels = [
            NETWORK_NODE__LABEL,
            POINT_ASSET_NODE__LABEL,
            LINE_NODE__LABEL,
            LINE_JUNCTION__LABEL,
            LINE_END__LABEL,
        ]
        self.unique_point_asset_names = []
        self.sqids = Sqids(alphabet="abcdefghijklmnop0123456789")

    def transform(
        self,
        geo_data: dict,
    ):

        gtlm: GeoTransformListModel = GeoTransformListModel(geo_data)

        for base_line in gtlm.root:
            asset_intersects = self.get_intersects(base_line)

            normalised_points_on_line = self.order_points_on_line(
                base_line,
                asset_intersects,
            )

            aggregated_points_on_line = self.aggregate_points_on_line(
                normalised_points_on_line
            )

            nodes_ordered = self.create_nodes(base_line, aggregated_points_on_line)

            edges = self.create_edges(base_line, nodes_ordered)

            self.nodes.extend(nodes_ordered)
            self.edges.extend(edges)

    def flush_nodes_edges(self):
        self.nodes = []
        self.edges = []

    def get_intersects(self, base_line):

        all_line_intersects = self.get_asset_intersects(
            base_line.line_geom_shapely, base_line.line_junctions
        )
        all_point_intersects = self.get_asset_intersects(
            base_line.line_geom_shapely, base_line.intersect_points
        )

        return all_line_intersects + all_point_intersects

    def get_asset_intersects(self, base_line_geom_shapely, assets):
        all_intersects = []

        for intersecting_asset in assets:

            if intersecting_asset.asset_name not in self.unique_point_asset_names:
                self.unique_point_asset_names.append(intersecting_asset.asset_name)

            if intersecting_asset.geom_shapely.geom_type == "LineString":
                intersect_geoms: list = self.get_line_intersect_geoms(
                    base_line_geom_shapely,
                    intersecting_asset.geom_shapely,
                    intersecting_asset.asset_name,
                )
            elif intersecting_asset.geom_shapely.geom_type == "Point":
                intersect_geoms: list = self.get_point_intersect_geoms(
                    base_line_geom_shapely, intersecting_asset
                )
            else:
                raise Exception(
                    "Invalid geometry type. Allowed types are Point and LineString."
                )

            all_intersects.extend(intersect_geoms)

        return all_intersects

    @staticmethod
    def get_line_intersect_geoms(line_geom_shapely, geom_shapely, asset_name) -> list:
        """
        base_line_tag: tag of the base line
        line_geom_shapely: geom of the base line
        geom_shapely: geometry of the intersecting line
        intersect_asset_name: name of the asset
        """

        intersection_geom = line_geom_shapely.intersection(geom_shapely)

        if intersection_geom.geom_type == "Point":
            return [
                {
                    "geom": intersection_geom,
                    "asset_name": asset_name,
                    "node_labels": [NETWORK_NODE__LABEL, LINE_NODE__LABEL],
                }
            ]

        elif intersection_geom.geom_type == "MultiPoint":
            line_intersections = []
            for coords in intersection_geom.coords:
                line_intersections.append(
                    {
                        "geom": Point((coords[0], coords[1])),
                        "asset_name": asset_name,
                        "node_labels": [NETWORK_NODE__LABEL, LINE_NODE__LABEL],
                    }
                )
            return line_intersections

        else:
            raise Exception(
                "Invalid geometry types for intersection. Allowed types are Point and MultiPoint"
            )

    @staticmethod
    def get_point_intersect_geoms(line_geom_shapely, intersect_asset) -> list:
        """
        line_geom_shapely: geom of the base line
        geom_shapely: geometry of the intersecting point
        intersect_asset_tag: tag of the interesecting line
        intersect_asset_name: name of the asset
        """

        geom = intersect_asset.geom_shapely
        if geom.geom_type != "Point":
            raise Exception(
                "Invalid geometry types for intersection. Allowed types are point and multipoint"
            )
        # end

        if geom.intersects(line_geom_shapely):
            return [
                {
                    "asset_name": intersect_asset.asset_name,
                    "asset_label": intersect_asset.asset_label,
                    "asset_tag": intersect_asset.tag,
                    "geom": intersect_asset.geom_shapely,
                    "node_labels": [NETWORK_NODE__LABEL, POINT_ASSET_NODE__LABEL],
                }
            ]

        else:
            # Project the point onto the line and get the projected point
            distance_along_line = line_geom_shapely.project(geom)
            projected_point = line_geom_shapely.interpolate(distance_along_line)
            return [
                {
                    "asset_name": intersect_asset.asset_name,
                    "asset_label": intersect_asset.asset_label,
                    "asset_tag": intersect_asset.tag,
                    "geom": projected_point,
                    "node_labels": [NETWORK_NODE__LABEL, POINT_ASSET_NODE__LABEL],
                }
            ]
        # end

    def order_points_on_line(
        self,
        base_line,
        asset_intersects: list,
    ):

        normalised_points_on_line = self.distance_from_start_of_line(
            base_line.line_geom_shapely, asset_intersects
        )

        normalised_points_on_line.insert(
            0,
            {
                "normalised_position_on_line": 0,
                "asset_name": base_line.asset_name,
                "geom": base_line.start_point_geom_shapely,
                "node_labels": [NETWORK_NODE__LABEL, LINE_NODE__LABEL],
            },
        )

        normalised_points_on_line.append(
            {
                "normalised_position_on_line": 1,
                "asset_name": base_line.asset_name,
                "geom": base_line.end_point_geom_shapely,
                "node_labels": [NETWORK_NODE__LABEL, LINE_NODE__LABEL],
            }
        )

        ordered_points_on_line = sorted(
            normalised_points_on_line, key=lambda x: x["normalised_position_on_line"]
        )

        return ordered_points_on_line

    def distance_from_start_of_line(self, line_geom_shapely, asset_intersects):
        normalised_asset_intersects = []
        for asset in asset_intersects:
            normalised_position_on_line = self.get_normalised_point_on_line(
                line_geom_shapely, asset["geom"]
            )

            normalised_asset_intersects.append(
                {
                    "normalised_position_on_line": normalised_position_on_line,
                    **asset,
                }
            )

        return normalised_asset_intersects

    @staticmethod
    def get_normalised_point_on_line(line_geom_shapely, point_geom_shapely):

        distance_from_line_start = line_locate_point(
            line_geom_shapely, point_geom_shapely
        )

        line_length = line_geom_shapely.length

        normalised_position_on_line = 1 - (
            (line_length - distance_from_line_start) / line_length
        )

        return normalised_position_on_line

    def aggregate_points_on_line(self, data):

        grouped = defaultdict(
            dict
        )  # key: norm_pos_rounded, value: dict of asset_name -> item

        for item in data:
            norm_pos_rounded = round(item["normalised_position_on_line"], 3)
            asset_name = item["asset_name"]

            if asset_name not in grouped[norm_pos_rounded]:
                grouped[norm_pos_rounded][asset_name] = item

        # Flatten directly into a sorted flat list
        sorted_groups = []
        for key in sorted(grouped.keys()):
            sorted_groups.extend(grouped[key].values())

        aggregated_points_on_line = self.add_point_keys(sorted_groups)

        return aggregated_points_on_line

    def add_point_keys(self, aggregated_points_on_line):

        for point in aggregated_points_on_line:
            point["node_key"] = self.encode_node_key(
                point["geom"], self.unique_point_asset_names.index(point["asset_name"])
            )

        # end

        return aggregated_points_on_line

    def create_nodes(self, base_line, aggregated_points_on_line):
        nodes_ordered = self.update_node_labels(base_line, aggregated_points_on_line)

        for node in nodes_ordered:
            if POINT_ASSET_NODE__LABEL in node["node_labels"]:
                attributes = next(
                    (
                        p.asset_label
                        for p in base_line.intersect_points
                        if p.tag == node["asset_tag"]
                    ),
                    {},  # default if not found
                )

                node["attributes"] = attributes

        return nodes_ordered

    def create_edges(self, base_line, nodes_ordered):

        edges = []

        from_node_key = nodes_ordered[0]["node_key"]
        for node in nodes_ordered[1:]:
            to_node_key = node["node_key"]

            distance_from_line_start = line_locate_point(
                base_line.line_geom_shapely, node["geom"]
            )

            line_segment_geom = ops.substring(
                base_line.line_geom_shapely,
                start_dist=0,
                end_dist=distance_from_line_start,
            )

            edge = {
                "from_node_key": from_node_key,
                "to_node_key": to_node_key,
                "line_segment_geom": line_segment_geom,
                "attributes": base_line.attributes,
            }

            if POINT_ASSET_NODE__LABEL in node["node_labels"]:
                edge["edge_label"] = "HAS_ASSET"
            else:
                edge["edge_label"] = base_line.asset_label
                from_node_key = to_node_key

            edges.append(edge)

        return edges

    def update_node_labels(self, base_line, aggregated_points_on_line):

        nodes_ordered = []

        first_node = self._label_terminus(
            aggregated_points_on_line[0],
            is_junction=bool(base_line.line_start_intersections.get("tags")),
        )
        nodes_ordered.append(first_node)

        non_termini_nodes = aggregated_points_on_line[1:-1]
        for node in non_termini_nodes:
            nt_node = deepcopy(node)
            nt_node["node_labels"].append(self._get_non_termini_label(nt_node))
            nodes_ordered.append(nt_node)

        last_node = self._label_terminus(
            aggregated_points_on_line[-1],
            is_junction=bool(base_line.line_end_intersections.get("tags")),
        )
        nodes_ordered.append(last_node)

        return nodes_ordered

    @staticmethod
    def _label_terminus(node, is_junction):
        """Return a copy of the node with the appropriate terminus label."""
        node = deepcopy(node)
        label = LINE_JUNCTION__LABEL if is_junction else LINE_END__LABEL
        node["node_labels"].append(label)
        return node

        # add additional labels
        # add attributes

    def _get_non_termini_label(self, nt_node):

        if POINT_ASSET_NODE__LABEL in nt_node["node_labels"]:
            if nt_node["asset_label"] not in self.network_node_labels:
                self.network_node_labels.append(nt_node["asset_label"])
            return nt_node["asset_label"]
        elif LINE_NODE__LABEL in nt_node["node_labels"]:
            return LINE_JUNCTION__LABEL
        else:
            raise ValueError("Invalid node label(s) detected for non-termini node.")

    def encode_node_key(self, point: Point, encode_index: int) -> str:
        """
        Round and cast Point x,y to str to remove '.'
        then return back to int to make coords sqid compatible.

        Note these are not coordinates but int representations of the
        coordinates to ensure a unique node_key.
        """

        coord1_repr = int(str(round(point.x, 4)).replace(".", ""))
        coord2_repr = int(str(round(point.y, 4)).replace(".", ""))

        return self.sqids.encode([coord1_repr, coord2_repr, encode_index])
