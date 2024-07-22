from skyfield.api import Star, load, wgs84, load_constellation_map, load_constellation_names
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

        bright_stars = stars[stars.magnitude <= 4].copy()
        bright_star_objects = Star.from_dataframe(bright_stars)

        above_horizon = observer.at(time).observe(bright_star_objects).apparent()
        alt, az, distance = above_horizon.altaz()
        above_horizon_mask = alt.degrees > 0


        visible_constellations = {}
        constellation_full_names = dict(load_constellation_names())

        for i, is_visible in enumerate(above_horizon_mask):
            if is_visible:
                star = bright_stars.iloc[i]
                star_pos = Star.from_dataframe(star)
                constellation = constellation_map(observer.at(time).observe(star_pos).apparent())
                if constellation:
                    constellation_abrev = str(constellation)
                    constellation_name = constellation_full_names.get(constellation_abrev,constellation_abrev)
                    if constellation_name in visible_constellations:
                        visible_constellations[constellation_name] += 1
                    else:
                        visible_constellations[constellation_name] = 1

        '''
        for star in visible_stars.iteruples():
            star_pos = Star(ra_hours=star.ra_hours,dec_degrees=star.dec_degrees)
            constellation = constellation_map(observer.at(time).observe(star_pos).apparent())
            if constellation:
                if constellation not in visible_constellations:
                    visible_constellations[constellation] = 1
                else:
                    visible_constellations[constellation] += 1
        
        '''
        sorted_constellations = dict(sorted(visible_constellations.items(),key=lambda x:x[1], reverse=True))


        return sorted_constellations
        
