from skyfield.api import Star, load, wgs84, load_constellation_map, load_constellation_names
from skyfield.data import hipparcos, stellarium
from skyfield.projections import build_stereographic_projection
from datetime import date


class ConstellationCalculator():
    def __init__(self, loc):
        self.loc_lat = loc["lat"]
        self.loc_lng = loc["lng"]
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
        
def populate_constellations_table(db, Constellation):
    constellations = [
                {   
                "name":"Orion",
                "description": "Orion is a prominent set of stars most visible during winter in the northern celestial hemisphere. It is one of the 88 modern constellations; it was among the 48 constellations listed by the 2nd-century astronomer Ptolemy. It is named for a hunter in Greek mythology.",
                "img":"orion.jpg"
                },
                {   
                "name":"Ursa Major",
                "description": "Ursa Major (also known as the Great Bear) is a constellation in the northern sky, whose associated mythology likely dates back into prehistory. Its Latin name means greater (or larger) bear, referring to and contrasting it with nearby Ursa Minor, the lesser bear.",
                "img":"UrsaMajor.jpg"
                },
                {   
                "name":"Hercules",
                "description": "Hercules is a constellation named after Hercules, the Roman mythological hero adapted from the Greek hero Heracles. Hercules was one of the 48 constellations listed by the second-century astronomer Ptolemy, and it remains one of the 88 modern constellations today. It is the fifth-largest of the modern constellations and is the largest of the 50 which have no stars brighter than apparent magnitude +2.5.",
                "img":"Hercules.jpg"
                },
                {   
                "name":"Cygnus",
                "description":"Cygnus is a northern constellation on the plane of the Milky Way, deriving its name from the Latinized Greek word for swan.[1] Cygnus is one of the most recognizable constellations of the northern summer and autumn, and it features a prominent asterism known as the Northern Cross (in contrast to the Southern Cross). Cygnus was among the 48 constellations listed by the 2nd century astronomer Ptolemy, and it remains one of the 88 modern constellations.",
                "img":"Cygnus.jpg"
                },
                {   
                "name":"Ophiuchus",
                "description":"Ophiuchus (/ˌɒfiˈjuːkəs/) is a large constellation straddling the celestial equator. Its name comes from the Ancient Greek ὀφιοῦχος (ophioûkhos), meaning 'serpent-bearer', and it is commonly represented as a man grasping a snake. The serpent is represented by the constellation Serpens. Ophiuchus was one of the 48 constellations listed by the 2nd-century astronomer Ptolemy, and it remains one of the 88 modern constellations. An old alternative name for the constellation was Serpentarius",
                "img":"Ophiuchus.jpg"
                },
                {   
                "name":"Hydra",
                "description":"Hydra is the largest of the 88 modern constellations, measuring 1303 square degrees, and also the longest at over 100 degrees. Its southern end borders Libra and Centaurus and its northern end borders Cancer.[1] It was included among the 48 constellations listed by the 2nd century astronomer Ptolemy. Commonly represented as a water snake, it straddles the celestial equator.",
                "img":"Hydra.jpg"
                },
                {   
                "name":"Leo",
                "description":"Leo /ˈliːoʊ/ is one of the constellations of the zodiac, between Cancer the crab to the west and Virgo the maiden to the east. It is located in the Northern celestial hemisphere. Its name is Latin for lion, and to the ancient Greeks represented the Nemean Lion killed by the mythical Greek hero Heracles as one of his twelve labors. Its old astronomical symbol is  (♌︎). One of the 48 constellations described by the 2nd-century astronomer Ptolemy, Leo remains one of the 88 modern constellations today, and one of the most easily recognizable due to its many bright stars and a distinctive shape that is reminiscent of the crouching lion it depicts.",
                "img":"Leo.jpg"
                },
                {   
                "name":"Draco",
                "description":"Draco is a constellation in the far northern sky. Its name is Latin for dragon. It was one of the 48 constellations listed by the 2nd century Greek astronomer Ptolemy, and remains one of the 88 modern constellations today. The north pole of the ecliptic is in Draco.[1] Draco is circumpolar from northern latitudes, meaning that it never sets and can be seen at any time of year.",
                "img":"Draco.jpg"
                },
                {   
                "name":"Scorpius",
                "description":"Scorpius is a zodiac constellation located in the Southern celestial hemisphere, where it sits near the center of the Milky Way, between Libra to the west and Sagittarius to the east. Scorpius is an ancient constellation whose recognition predates Greek culture;[1] it is one of the 48 constellations identified by the Greek astronomer Ptolemy in the second century.",
                "img":"Scorpius.jpg"
                },
                {   
                "name":"Virgo",
                "description":"Virgo is one of the constellations of the zodiac. Its name is Latin for maiden, and its old astronomical symbol is . Between Leo to the west and Libra to the east, it is the second-largest constellation in the sky (after Hydra) and the largest constellation in the zodiac. The ecliptic intersects the celestial equator within this constellation and Pisces. Underlying these technical two definitions, the sun passes directly overhead of the equator, within this constellation, at the September equinox. Virgo can be easily found through its brightest star, Spica.",
                "img":"Virgo.jpg"
                },
                {   
                "name":"Centaurus",
                "description":"Centaurus /sɛnˈtɔːrəs, -ˈtɑːr-/ is a bright constellation in the southern sky. One of the largest constellations, Centaurus was included among the 48 constellations listed by the 2nd-century astronomer Ptolemy, and it remains one of the 88 modern constellations. In Greek mythology, Centaurus represents a centaur; a creature that is half human, half horse (another constellation named after a centaur is one from the zodiac: Sagittarius). Notable stars include Alpha Centauri, the nearest star system to the Solar System, its neighbour in the sky Beta Centauri, and V766 Centauri, one of the largest stars yet discovered. The constellation also contains Omega Centauri, the brightest globular cluster as visible from Earth and the largest identified in the Milky Way, possibly a remnant of a dwarf galaxy.",
                "img":"Centaurus.jpg"
                },
                {   
                "name":"Cassiopeia",
                "description":"Cassiopeia is a constellation and asterism in the northern sky named after the vain queen Cassiopeia, mother of Andromeda, in Greek mythology, who boasted about her unrivaled beauty. Cassiopeia was one of the 48 constellations listed by the 2nd-century Greek astronomer Ptolemy, and it remains one of the 88 modern constellations today. It is easily recognizable due to its distinctive 'W' shape, formed by five bright stars."
                            "Cassiopeia is located in the northern sky and from latitudes above 34°N it is visible year-round. In the (sub)tropics it can be seen at its clearest from September to early November, and at low southern, tropical, latitudes of less than 25°S it can be seen, seasonally, low in the North.",
                "img":"Cassiopeia.jpg"
                },
                {
                "name":"Auriga",
                "description":"Auriga is a constellation in the northern celestial hemisphere. It is one of the 88 modern constellations; it was among the 48 constellations listed by the 2nd-century astronomer Ptolemy. Its name is Latin for '(the) charioteer', associating it with various mythological beings, including Erichthonius and Myrtilus. Auriga is most prominent during winter evenings in the northern Hemisphere, as are five other constellations that have stars in the Winter Hexagon asterism. Because of its northern declination, Auriga is only visible in its entirety as far south as -34°; for observers farther south it lies partially or fully below the horizon. A large constellation, with an area of 657 square degrees, it is half the size of the largest, Hydra.",
                "img":"Auriga.jpg"
                },
                {
                "name":"Gemini",
                "description":"Gemini is one of the constellations of the zodiac and is located in the northern celestial hemisphere. It was one of the 48 constellations described by the 2nd century AD astronomer Ptolemy, and it remains one of the 88 modern constellations today. Its name is Latin for twins, and it is associated with the twins Castor and Pollux in Greek mythology. Its old astronomical symbol is  (♊︎).",
                "img":"Gemini.jpg"
                },
                {
                "name":"Bootes",
                "description":"Boötes (/boʊˈoʊtiːz/ boh-OH-teez) is a constellation in the northern sky, located between 0° and +60° declination, and 13 and 16 hours of right ascension on the celestial sphere. The name comes from Latin: Boōtēs, which comes from Greek: Βοώτης, translit. Boṓtēs 'herdsman' or 'plowman' (literally, 'ox-driver'; from βοῦς boûs 'cow').",
                "img":"Bootes.jpg"
                },
                {
                "name":"Serpens",
                "description":"Serpens (Ancient Greek: Ὄφις, romanized: Óphis, lit. 'the Serpent') is a constellation in the northern celestial hemisphere. One of the 48 constellations listed by the 2nd-century astronomer Ptolemy, it remains one of the 88 modern constellations designated by the International Astronomical Union. It is unique among the modern constellations in being split into two non-contiguous parts, Serpens Caput (Serpent Head) to the west and Serpens Cauda (Serpent Tail) to the east. Between these two halves lies the constellation of Ophiuchus, the 'Serpent-Bearer'. In figurative representations, the body of the serpent is represented as passing behind Ophiuchus between Mu Serpentis in Serpens Caput and Nu Serpentis in Serpens Cauda.",
                "img":"Serpens.jpg"
                },
                {
                "name":"Perseus",
                "description":"Perseus is a constellation in the northern sky, named after the Greek mythological hero Perseus. It is one of the 48 ancient constellations listed by the 2nd-century astronomer Ptolemy,[1] and among the 88 modern constellations defined by the International Astronomical Union (IAU).[2] It is located near several other constellations named after ancient Greek legends surrounding Perseus, including Andromeda to the west and Cassiopeia to the north. Perseus is also bordered by Aries and Taurus to the south, Auriga to the east, Camelopardalis to the north, and Triangulum to the west. Some star atlases during the early 19th century also depicted Perseus holding the disembodied head of Medusa,[3] whose asterism was named together as Perseus et Caput Medusae;[4] however, this never came into popular usage.",
                "img":"Perseus.jpg"
                },
                {
                "name":"Aquila",
                "description":"Aquila is a constellation on the celestial equator. Its name is Latin for 'eagle' and it represents the bird that carried Zeus/Jupiter's thunderbolts in Greek-Roman mythology. Its brightest star, Altair, is one vertex of the Summer Triangle asterism. The constellation is best seen in the northern summer, as it is located along the Milky Way. Because of this location, many clusters and nebulae are found within its borders, but they are dim and galaxies are few.",
                "img":"Aquila.jpg"
                },
                {
                "name":"Libra",
                "description":"Libra /ˈliːbrə/ is a constellation of the zodiac and is located in the Southern celestial hemisphere. Its name is Latin for weighing scales. Its old astronomical symbol is  (♎︎). It is fairly faint, with no first magnitude stars, and lies between Virgo to the west and Scorpius to the east. Beta Librae, also known as Zubeneschamali, is the brightest star in the constellation. Three star systems are known to have planets.",
                "img":"Libra.jpg"
                },
                {
                "name":"Lupus",
                "description":"Lupus is a constellation of the mid-Southern Sky. Its name is Latin for wolf. Lupus was one of the 48 constellations listed by the 2nd-century astronomer Ptolemy, and it remains one of the 88 modern constellations but was long an asterism associated with the just westerly, larger constellation Centaurus.",
                "img":"Lupus.jpg"
                },
                {
                "name":"Cepheus",
                "description":"Cepheus is a constellation in the deep northern sky, named after Cepheus, a king of Aethiopia in Greek mythology. It is one of the 48 constellations listed by the second century astronomer Ptolemy, and it remains one of the 88 constellations in the modern times.",
                "img":"Cepheus.jpg"
                },
                {
                "name":"Corvus",
                "description":"Corvus is a small constellation in the Southern Celestial Hemisphere. Its name means 'crow' in Latin. One of the 48 constellations listed by the 2nd-century astronomer Ptolemy, it depicts a raven, a bird associated with stories about the god Apollo, perched on the back of Hydra the water snake. The four brightest stars, Gamma, Delta, Epsilon, and Beta Corvi, form a distinctive quadrilateral or cross-shape in the night sky.",
                "img":"Corvus.jpg"
                },
                {
                "name":"Andromeda",
                "description":"Andromeda is one of the 48 constellations listed by the 2nd-century Greco-Roman astronomer Ptolemy, and one of the 88 modern constellations. Located in the northern celestial hemisphere, it is named for Andromeda, daughter of Cassiopeia, in the Greek myth, who was chained to a rock to be eaten by the sea monster Cetus. Andromeda is most prominent during autumn evenings in the Northern Hemisphere, along with several other constellations named for characters in the Perseus myth. Because of its northern declination, Andromeda is visible only north of 40° south latitude; for observers farther south, it lies below the horizon. It is one of the largest constellations, with an area of 722 square degrees. This is over 1,400 times the size of the full moon, 55% of the size of the largest constellation, Hydra, and over 10 times the size of the smallest constellation, Crux.",
                "img":"Andromeda.jpg"
                },
                {
                "name":"Ursa Minor",
                "description":"Ursa Minor (Latin: 'Lesser Bear', contrasting with Ursa Major), also known as the Little Bear, is a constellation located in the far northern sky. As with the Great Bear, the tail of the Little Bear may also be seen as the handle of a ladle, hence the North American name, Little Dipper: seven stars with four in its bowl like its partner the Big Dipper. Ursa Minor was one of the 48 constellations listed by the 2nd-century astronomer Ptolemy, and remains one of the 88 modern constellations. Ursa Minor has traditionally been important for navigation, particularly by mariners, because of Polaris being the north pole star.",
                "img":"UrsaMinor.jpg"
                },
                {
                "name":"Lynx",
                "description":"Lynx is a constellation named after the animal, usually observed in the Northern Celestial Hemisphere. The constellation was introduced in the late 17th century by Johannes Hevelius. It is a faint constellation, with its brightest stars forming a zigzag line. The orange giant Alpha Lyncis is the brightest star in the constellation, and the semiregular variable star Y Lyncis is a target for amateur astronomers. Six star systems have been found to contain planets. Those of 6 Lyncis and HD 75898 were discovered by the Doppler method; those of XO-2, XO-4, XO-5 and WASP-13 were observed as they passed in front of the host star.",
                "img":"Lynx.jpg"
                },
                {
                "name":"Corona Borealis",
                "description":"Corona Borealis is a small constellation in the Northern Celestial Hemisphere. It is one of the 48 constellations listed by the 2nd-century astronomer Ptolemy, and remains one of the 88 modern constellations. Its brightest stars form a semicircular arc. Its Latin name, inspired by its shape, means 'northern crown'. In classical mythology Corona Borealis generally represented the crown given by the god Dionysus to the Cretan princess Ariadne and set by her in the heavens. Other cultures likened the pattern to a circle of elders, an eagle's nest, a bear's den or a smokehole. Ptolemy also listed a southern counterpart, Corona Australis, with a similar pattern.",
                "img":"CoronaBorealis.jpg"
                },
                {
                "name":"Lyra",
                "description":"Lyra (Latin for 'lyre', from Ancient Greek: λύρα; pronounced: /ˈlaɪrə/ LY-rə)[2] is a small constellation. It is one of the 48 listed by the 2nd century astronomer Ptolemy, and is one of the modern 88 constellations recognized by the International Astronomical Union. Lyra was often represented on star maps as a vulture or an eagle carrying a lyre, and hence is sometimes referred to as Vultur Cadens or Aquila Cadens ('Falling Vulture' or 'Falling Eagle'), respectively. Beginning at the north, Lyra is bordered by Draco, Hercules, Vulpecula, and Cygnus. Lyra is nearly overhead in temperate northern latitudes shortly after midnight at the start of summer. From the equator to about the 40th parallel south it is visible low in the northern sky during the same (thus winter) months.",
                "img":"Lyra.jpg"
                },
                {
                "name":"Cancer",
                "description":"Cancer is one of the twelve constellations of the zodiac and is located in the Northern celestial hemisphere. Its old astronomical symbol is  (♋︎). Its name is Latin for crab and it is commonly represented as one. Cancer is a medium-size constellation with an area of 506 square degrees and its stars are rather faint, its brightest star Beta Cancri having an apparent magnitude of 3.5. It contains ten stars with known planets, including 55 Cancri, which has five: one super-earth and four gas giants, one of which is in the habitable zone and as such has expected temperatures similar to Earth. At the (angular) heart of this sector of our celestial sphere is Praesepe (Messier 44), one of the closest open clusters to Earth and a popular target for amateur astronomers.",
                "img":"Cancer.jpg"
                },
                {
                "name":"Sagitta",
                "description":"Sagitta is a dim but distinctive constellation in the northern sky. Its name is Latin for 'arrow', not to be confused with the significantly larger constellation Sagittarius 'the archer'. It was included among the 48 constellations listed by the 2nd-century astronomer Ptolemy, and it remains one of the 88 modern constellations defined by the International Astronomical Union. Although it dates to antiquity, Sagitta has no star brighter than 3rd magnitude and has the third-smallest area of any constellation.",
                "img":"Sagitta.jpg"
                },
                {
                "name":"Delphinus",
                "description":"Delphinus (Pronounced /dɛlˈfaɪnəs/ or /ˈdɛlfɪnəs/) is a small constellation in the Northern Celestial Hemisphere, close to the celestial equator. Its name is the Latin version for the Greek word for dolphin (δελφίς). It is one of the 48 constellations listed by the 2nd century astronomer Ptolemy, and remains one of the 88 modern constellations recognized by the International Astronomical Union. It is one of the smaller constellations, ranked 69th in size. Delphinus' five brightest stars form a distinctive asterism symbolizing a dolphin with four stars representing the body and one the tail. It is bordered (clockwise from north) by Vulpecula, Sagitta, Aquila, Aquarius, Equuleus and Pegasus.",
                "img":"Delphinus.jpg"
                },
                {
                "name":"Leo Minor",
                "description":"Leo Minor is a small and faint constellation in the northern celestial hemisphere. Its name is Latin for 'the smaller lion', in contrast to Leo, the larger lion. It lies between the larger and more recognizable Ursa Major to the north and Leo to the south. Leo Minor was not regarded as a separate constellation by classical astronomers; it was designated by Johannes Hevelius in 1687.[2]",
                "img":"LeoMinor.jpg"
                },
                {
                "name":"Crater",
                "description":"Crater is a small constellation in the southern celestial hemisphere. Its name is the latinization of the Greek krater, a type of cup used to water down wine. One of the 48 constellations listed by the second-century astronomer Ptolemy, it depicts a cup that has been associated with the god Apollo and is perched on the back of Hydra the water snake.",
                "img":"Crater.jpg"
                },
                {
                "name":"Canes Venatici",
                "description":"Canes Venatici (/ˈkeɪniːz vɪˈnætɪsaɪ/) is one of the 88 constellations designated by the International Astronomical Union (IAU). It is a small northern constellation that was created by Johannes Hevelius in the 17th century. Its name is Latin for 'hunting dogs', and the constellation is often depicted in illustrations as representing the dogs of Boötes the Herdsman, a neighboring constellation.",
                "img":"CanesVenatici.jpg"
                },
                {
                "name":"Sagittarius",
                "description":"Sagittarius is one of the constellations of the zodiac and is located in the Southern celestial hemisphere. It is one of the 48 constellations listed by the 2nd-century astronomer Ptolemy and remains one of the 88 modern constellations. Its old astronomical symbol is  (♐︎). Its name is Latin for 'archer'. Sagittarius is commonly represented as a centaur drawing a bow. It lies between Scorpius and Ophiuchus to the west and Capricornus and Microscopium to the east.",
                "img":"Sagittarius.jpg"
                },
                {
                "name":"Scutum",
                "description":"Scutum is a small constellation. Its name is Latin for shield, and it was originally named Scutum Sobiescianum by Johannes Hevelius in 1684. Located just south of the celestial equator, its four brightest stars form a narrow diamond shape. It is one of the 88 IAU designated constellations defined in 1922.",
                "img":"Scutum.jpg"
                },
                {
                "name":"Lacerta",
                "description":"Lacerta is one of the 88 modern constellations defined by the International Astronomical Union. Its name is Latin for lizard. A small, faint constellation, it was defined in 1687 by the astronomer Johannes Hevelius. Its brightest stars form a 'W' shape similar to that of Cassiopeia, and it is thus sometimes referred to as 'Little Cassiopeia'. It is located between Cygnus, Cassiopeia and Andromeda on the northern celestial sphere. The northern part lies on the Milky Way.",
                "img":"Lacerta.jpg"
                }

            ]
    for entry in constellations:
        constellation = Constellation(name=entry["name"],description=entry["description"],img=entry["img"])
        db.session.add(constellation)
    db.session.commit()
