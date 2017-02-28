
def snap2road(pts_lon_lat, timestamps=[], return_confidence=False):
    """
    params:
        pts_lon_lat: [[lon, lat], [], ...]
        timestamps: ['2015-10-15T12:06:50Z', ...]
    return:
        new_gps: [[lon, lat], [], ...], len(new_gps) not necessarily equals to len(pts_lon_lat)
        confidences: [ (which batch, # origin pts, # snapped pts, confidence), (), ..]
    """
    import mapbox as mp
    access = "pk.eyJ1Ijoic3VyYWpuYWlyIiwiYSI6ImNpdWoyZGQzYjAwMXkyb285b2Q5NmV6amEifQ.WBQAX7ur2T3kOLyi11Nybw"
    service = mp.MapMatcher(access_token=access)
    new_gps = []
    confidences = []
    for num_batch, (s, e) in enumerate(even_chunks(pts_lon_lat, 100, indices=True)):
        batch_pts = pts_lon_lat[s:e]
        batch_tss = timestamps[s:e]
        geojson = {'type': 'Feature',
                   'properties': {'coordTimes': batch_tss},
                   'geometry': {'type': 'LineString',
                                'coordinates': batch_pts}}
        response = service.match(geojson, profile='mapbox.cycling')
        var = response.geojson()
        features = var['features']
        for f in features:
            coords = f['geometry']['coordinates']            
            properties = f['properties']
            if return_confidence:
                confidences.append({'#batch': num_batch, '#origin_pts': len(batch_pts),
                                    '#snap_pts': len(coords), 'confidence': properties['confidence']})
                new_gps.append(coords)
            else:
                new_gps.extend(coords)

    if return_confidence:
        return new_gps, confidences
    return new_gps
