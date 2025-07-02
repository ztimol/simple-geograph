import psycopg2
from simplegeograph import GeoGraph


NYC_SUBWAY_SQL_FILE = "nyc_subway.sql"

POSTGIS_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": 5432,
}

NEO4J_CONFIG = {
    "db_user": "neo4j",
    "db_password": "password",
    "db_uri": "localhost:7687",
}


def main() -> None:

    geo_data: list = query_data()

    gtn = GeoGraph()
    gtn.transform(geo_data)
    gtn.to_neo4j(db_config=NEO4J_CONFIG)


def query_data() -> list:

    with open(NYC_SUBWAY_SQL_FILE, "r") as f:
        sql_query = f.read()

    try:
        with psycopg2.connect(**POSTGIS_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                rows = cur.fetchall()
                column_names = [desc[0] for desc in cur.description]
    except Exception as e:
        raise Exception(f"Error executing SQL: {e}") from e

    geo_data = []
    for row in rows:
        record = dict(zip(column_names, row))
        data = extract_line_data(record)
        geo_data.append(data)

    return geo_data


def extract_line_data(row):

    row["geom"] = to_pg_wkb_hex(row["geom"])
    row["start_point_geom"] = to_pg_wkb_hex(row["start_point_geom"])
    row["end_point_geom"] = to_pg_wkb_hex(row["end_point_geom"])

    data = {
        "line_tag": int(row.pop("id")),
        "line_geom": row.pop("geom"),
        "line_srid": int(row.pop("geom_srid")),
        "start_point_geom": row.pop("start_point_geom").replace("\\x", ""),
        "end_point_geom": row.pop("end_point_geom").replace("\\x", ""),
        "line_start_intersections": row.pop("line_start_intersections"),
        "line_end_intersections": row.pop("line_end_intersections"),
        "line_junctions": row.pop("line_junctions"),
        "intersect_points": row.pop(
            "subway_station"
        ),  # merge all intersecting points into a single list. In this case there is only one type of point so we can add it directly.
        **row,  # all other values are added as attributes
    }

    return data


def to_pg_wkb_hex(memview_obj):
    return memview_obj.tobytes().hex()


if __name__ == "__main__":
    main()
