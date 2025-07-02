SELECT   "nyc_subway_line"."id",
         "nyc_subway_line"."route_id",
         "nyc_subway_line"."route_short",
         "nyc_subway_line"."route_long",
         "nyc_subway_line"."group",
         'subway_line'::varchar                                    AS "asset_name",
         'SubwayLine'::varchar                                     AS "asset_label",
         -- st_length("nyc_subway_line"."geom")                    AS "line_length",
         ST_AsBinary("nyc_subway_line"."geom")                     AS "geom",
         ST_SRID("nyc_subway_line"."geom")                         AS "geom_srid",
         ST_AsBinary(st_startpoint("nyc_subway_line"."geom"))      AS "start_point_geom",
         ST_AsBinary(st_endpoint("nyc_subway_line"."geom"))        AS "end_point_geom",
         to_jsonb(array
         (
                  SELECT   jsonb_build_object(('tag'), u0."id", ('route_long')::text, u0."route_long", ('geom')::text, ST_AsBinary(u0."geom"), ('start_point_geom')::text, ST_AsBinary(st_startpoint(u0."geom")), ('end_point_geom')::text, ST_AsBinary(st_endpoint(u0."geom")), ('asset_name')::text, 'subway_line', ('asset_label')::text, 'SubwayLine') AS "json"
                  FROM     "nyc_subway_line" u0
                  WHERE    st_touches(u0."geom", ("nyc_subway_line"."geom"))
                  ORDER BY u0."id" ASC
         )) AS "line_junctions",
         (
            SELECT jsonb_build_object('tags', array_agg(u0.id ORDER BY u0.id))
            FROM nyc_subway_line u0
            WHERE
            u0.id != nyc_subway_line.id AND
            st_dwithin(u0.geom, st_startpoint(nyc_subway_line.geom), 0.0)
         ) AS "line_start_intersections",
         (
            SELECT jsonb_build_object('tags', array_agg(u0.id ORDER BY u0.id))
            FROM nyc_subway_line u0
            WHERE
            u0.id != nyc_subway_line.id AND
            st_dwithin(u0.geom, st_endpoint(nyc_subway_line.geom), 0.0)
         ) AS "line_end_intersections",
         to_jsonb(array
         (
                  SELECT   jsonb_build_object(('tag'), v0."id"::int, ('geom')::text, ST_AsBinary(v0."geom"), ('srid')::text, ST_SRID(v0."geom"), ('line_touches_tags')::text, array
                           (
                                    SELECT   u0."id"
                                    FROM     "nyc_subway_line" u0
                                    WHERE    st_dwithin(u0."geom", (v0."geom"), 0.1)
                                    ORDER BY u0."id" ASC), ('asset_name')::text, 'subway_station', ('asset_label')::text, 'SubwayStation') AS "json"
                  FROM     "nyc_subway_station" v0
                  WHERE    st_dwithin(v0."geom", "nyc_subway_line"."geom", 0.1)
                  ORDER BY v0."id" ASC
         )) AS "subway_station"
FROM     "nyc_subway_line"
ORDER BY "nyc_subway_line"."id" ASC
