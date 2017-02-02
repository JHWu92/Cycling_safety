from src.constants import fn_segments_dc_raw, fn_segments_dc
import geopandas as gp
from shapely.ops import linemerge
data_dir = 'data/'
segs_dc_raw = gp.read_file(data_dir + fn_segments_dc_raw)
segs_dc_raw.geometry = segs_dc_raw.geometry.apply(lambda x: x if x.type!='MultiLineString' else linemerge(x))
with open(data_dir+fn_segments_dc, 'w') as f:
    f.write(segs_dc_raw.to_json())