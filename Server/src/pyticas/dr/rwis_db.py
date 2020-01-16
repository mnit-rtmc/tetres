__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

try:
    from pyticas_rwis import rwis as _rwis_db
except ImportError:
    raise Exception('pyticas_rwis is required to use this module')

get_weather = _rwis_db.get_weather
find_nearby_sites = _rwis_db.find_nearby_sites
get_site_by_id = _rwis_db.get_site_by_id
get_all_rwis_sites = _rwis_db.get_all_rwis_sites