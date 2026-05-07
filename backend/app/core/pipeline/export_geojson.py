import json

def export_geojson_stream(rows, output_file, build_feature):
    with open(output_file, "w") as f:
        f.write('{"type":"FeatureCollection","features":[')

        first = True

        for h3_index, value in rows:
            feature = build_feature(h3_index, value)

            if not first:
                f.write(",")
            first = False

            json.dump(feature, f)

        f.write("]}")