# simple-geograph

NB: This project is currently in alpha.

### Overview

- simple-geograph is a python library for converting geospatial network to graph networks
- Calculates the connections between Point and LineString geometries and converts them nodes and edges
- Maintins geometry information so it's not lost during conversion
- Can readily be integrated with geospatial databases (such as PostGIS, SpatialLite), geospatial libraries (such as GeoPandas), graph databases (Neo4j), and graph libraries (NetworkX)

If you use simple-geograph in your project please link this repo.

### Example script
```
from simplegeograph import GeoGraph

### Retreive geospatial data from source
### and structure as required
geo_data: list = query_data()

gtn = GeoGraph()

# transform to objects reprsenting nodes and edges
gtn.transform(geo_data)

# save data to neo4j
gtn.to_neo4j(db_config=NEO4J_CONFIG)
```
A more comprehensive example can be found. See [city subway_app](examples/city/)
