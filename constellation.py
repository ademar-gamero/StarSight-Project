from skyfield.api import Star, load, wgs84, load_constellation_map
from skyfield.data import hipparcos, stellarium
from skyfield.projections import build_stereographic_projection
from datetime import date

class ConstellationCalculator():
    def __init__(self, loc):
        self.loc_lat = loc[0]
        self.loc_lng = loc[1]
        self.date = date.today()

    def find_constellations(self):
        with load.open(hipparcos.URL) as f:
            stars = hipparcos.load_dataframe(f)

        constellation_map = load_constellation_map() 

        ts = load.timescale()
        time = ts.utc(self.date.year,self.date.month,self.date.day)
        location = wgs84.latlon(self.loc_lat,self.loc_lng)

        eph = load('de421.bsp')
        earth = eph['earth']

        observer = earth + location

        bright_stars =  Star.from_dataframe(stars[stars.magnitude >= 4])
        above_horizon = observer.at(time).observe(bright_stars).apparent()
        alt, az, distance = above_horizon.altaz()
        above_horizon_mask = alt.degrees > 0

        visible_stars = stars[above_horizon_mask]

        visible_constellations = set()

        for star in visible_stars.iteruples():
            star_pos = Star(ra_hours=star.ra_hours,dec_degrees=star.dec_degrees)
            constellation = constellation_map(observer.at(time).observe(star_pos).apparent())
            if constellation:
                visible_constellations.add(constellation)

        return list(visible_constellations)
        
