#!/bin/bash

echo "Startinig neo4j and postgis ..."
echo

docker compose -f ../docker/docker-compose-postgis.yml -f ../docker/docker-compose-neo4j.yml up -d --build

echo
echo "Neo4j and postgis server setup complete."
