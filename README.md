# simple-geograph

NB: This project is currently in alpha.

### Overview

- simple-geograph is a python library for converting geospatial network to graph networks
- Calculates the connections between Point and LineString geometries and converts them nodes and edges
- Maintins geometry information so it's not lost during conversion
- Can readily be integrated with geospatial databases (such as PostGIS, SpatialLite), geospatial libraries (such as GeoPandas), graph databases (Neo4j), and graph libraries (NetworkX)

If you use simple-geograph in your project please link this repo.

### The Transform algorithm

The approach for transforming a geospatial LineString and Points to a graph network has several steps:

1. Identify the LineString layer that should be converted to edges This should only be a LineString and not a MultiLineString
2. Identify the Point layers(s) that should be converted to nodes

_**with a geospatial query**_

3. For each LineString find every other LineString that intersects with the _start_ Point of the LineString of interest (dWithin can be used)
4. For each LineString find every other LineString that intersects with the _end_ Point of the LineString of interest (dWithin can be used)
5. For each LineString find every other LineString that intersects with a non-termini point LineString of interest (dWithin can be used)
6. For each LineString find every Point that intersects with the LineString of interest (dWithin can be used)

_**in code**_

7. For each LineString find the start and end Point geometries
8. For each LineString find the Points of intersection of every other intersecting LineString
9. For each LineString find the Points of of intersection of every other intersecting Point
10. For each LineString order the Points of intersection from the start Point of the LineString
11. For each LineString add a unique `node_key` to each Point and create an ordered array. Each element in this array can be a node
12. For each LineString, iterate over the ordered array of element. Create a new array with each element containing a `from_node_key` and a `to_node_key`. Each element in this array can be an edge.

_**create graph**_
    
13. Create the graph network using the arrays of nodes and edges

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
