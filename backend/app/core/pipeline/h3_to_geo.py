import h3

def h3_to_geometry(h3_index: str):
    boundary = h3.cell_to_boundary(h3_index)

    polygon = {
        "type": "Polygon",
        "coordinates": [[[lng, lat] for lat, lng in boundary]]
    }

    center = h3.cell_to_latlng(h3_index)
    center = [center[1], center[0]]  # lng, lat

    return polygon, center