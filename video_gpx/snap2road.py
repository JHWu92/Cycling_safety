def snap2road(pts_lon_lat, timestamps=(), pause=False):
    """
    params:
        pts_lon_lat: [[lon, lat], [], ...]
        timestamps: ['2015-10-15T12:06:50Z', ...]
    return:
        new_gps: [[lon, lat], [], ...], len(new_gps) not necessarily equals to len(pts_lon_lat)
        confidences: [ (which batch, # origin pts, # snapped pts, confidence), (), ..]
    """
    import mapbox as mp
    from utils import even_chunks, work_every_sec
    access = "pk.eyJ1Ijoic3VyYWpuYWlyIiwiYSI6ImNpdWoyZGQzYjAwMXkyb285b2Q5NmV6amEifQ.WBQAX7ur2T3kOLyi11Nybw"
    service = mp.MapMatcher(access_token=access)
    snapped = []
    raw = []
    for bidx, (s, e) in enumerate(even_chunks(pts_lon_lat, 100, indices=True)):
        batch_pts = pts_lon_lat[s:e]
        batch_tss = timestamps[s:e]
        raw.append({'batch': bidx, 'raw_len': len(batch_pts), 'raw': batch_pts})
        
        # request service for snapped
        geojson = {'type': 'Feature',
                   'properties': {'coordTimes': batch_tss},
                   'geometry': {'type': 'LineString',
                                'coordinates': batch_pts}}
        response = service.match(geojson, profile='mapbox.cycling')
        var = response.geojson()
        features = var['features']
        
        # parse response
        for fidx, f in enumerate(features):
            coords = f['geometry']['coordinates']            
            properties = f['properties']
            snapped.append({'batch': bidx, 'sub_batch': fidx, 'snapped_len': len(coords), 
                                'confidence': properties['confidence'], 'snapped': coords})
        if pause:
            work_every_sec(sec=0.5)
    return {'snapped': snapped, 'raw': raw}
