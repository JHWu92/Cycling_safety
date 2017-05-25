# how features are computed

feature|data source|downloaded date|match segment|time|features|code
-|-
segment attributes|[street segment](http://opendata.dc.gov/datasets/street-segments)|02/02/2017|index as primary key and foreign keys to other features|no time|keep columns:'DIRECTIONALITY', 'STREETTYPE', 'SHAPE_Length', 'SEGMENTTYPE'|FTR-dc-seg-bklane-311-crash-vision0-crime.ipynb
bike facilities from dc.gov|[Street Right of Way for Bicycle](http://opendata.dc.gov/datasets/street-right-of-way-for-bicycle-lanes)|09/14/2016|using existing STREETSEGID|No TIME|dummy features of FACILITY |FTR-dc-seg-bklane-311-crash-vision0-crime.ipynb
311|[cityworks-service-requests](http://opendata.dc.gov/datasets/cityworks-service-requests) |05/20/2017|pts2seg(0.5% no match)|INITIATEDDATE column->YEAR, MONTH|total count + total count without PAKRING METER REQUES+ dummy on description |FTR-dc-seg-bklane-311-crash-vision0-crime.ipynb
crashes|[crashes](http://opendata.dc.gov/datasets/crashes-in-the-district-of-columbia)|05/19/2017| pts2seg(~50%, 70k no match); STREETSEGID for the rest(30k no segid)|SOURCEADDTIME -> YEAR, MONTH|total count + dummy on CRASHEVENTTYPES(comma split) + FIRSTHARMFULEVENTSPECIFICS|FTR-dc-seg-bklane-311-crash-vision0-crime.ipynb
crime incidences|[yearly crime](http://opendata.dc.gov/datasets?q=crime%20incidents)|05/23/2017| pts2seg(0.3% no match)|START_DATE column->YEAR, MONTH|total count + dummy on METHOD and OFFENSE|FTR-dc-seg-bklane-311-crash-vision0-crime.ipynb
vision zero|[vision zero](http://opendata.dc.gov/datasets/vision-zero-safety)|05/19/2017| pts2seg(1/5329 no match)|REQUESTDATE column->YEAR, MONTH|total count + dummy on USERTYPE and REQUESTTYPE|FTR-dc-seg-bklane-311-crash-vision0-crime.ipynb
moving violation|[monthly mov violation](http://opendata.dc.gov/datasets/moving-violations-issued-in-february-2016)|04/11/2017|using existing STREETSEGID|month and year in data file name|total count + dummy on VIOLATIONDESC|FTR-DC-crime, moving, parking violation by Suraj.ipynb
parking violation|[monthly park violation](http://opendata.dc.gov/datasets/parking-violations-issued-in-march-2016)|04/11/2017|using existing STREETSEGID|month and year in data file name|total count + dummy on VIOLATION_DESCRIPTION|FTR-DC-crime, moving, parking violation by Suraj.ipynb
bike facilities from OSM|[OSM](www.openstreetmap.org)|10/25/2016|
poi|[frsq venues search api](https://developer.foursquare.com/docs/venues/search)<br>[OSM](www.openstreetmap.org)|frsq: 02/02/2017<br>OSM: 10/25/2016|
network, seg as node|[street segment](http://opendata.dc.gov/datasets/street-segments)|02/02/2017|
network, seg as edge|[street segment](http://opendata.dc.gov/datasets/street-segments)|02/02/2017|
