"""
Website URL helpers for chatbot responses.

The data modules stay focused on factual content. This file owns the
website routing layer so Webflow slugs can be updated in one place.
"""

from typing import Optional


SITE_BASE_URL = "https://www.1pax.com"


def absolute_url(path_or_url: str) -> str:
    """Return an absolute website URL for a path or URL."""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    if not path_or_url.startswith("/"):
        path_or_url = f"/{path_or_url}"
    return f"{SITE_BASE_URL}{path_or_url}"


MAIN_LINKS = {
    "home": "/",
    "about": "/about",
    "team": "/the-team",
    "projects": "/projects",
    "contact": "/contact",
    "patents": "/patents",
    "research": "/research",
    "ai": "/1pax-ai",
    "news": "/news-and-media",
}


SERVICE_URLS = {
    "services_list": "/projects",
    "airports": "/projects?category=airports-railstations",
    "urbanism": "/projects?category=urbanism-masterplan",
    "innovation": "/projects?category=innovation-research",
    "future_mobility": "/projects?category=future-of-mobility",
    "control_towers": "/projects?category=airports-railstations",
    "interior": "/projects?category=retail-and-interior-design",
    "working_living": "/projects?category=working-and-living",
    "bim": "/projects?category=bim",
}


COMPANY_URLS = {
    "overview": "/about",
    "name_meaning": "/about",
    "mission": "/about",
    "history": "/about",
    "founder": "/about",
    "offices": "/contact",
    "team": "/the-team",
    "expertise": "/about",
    "approach": "/about",
    "human_centered": "/about",
    "sustainability": "/about",
    "innovation": "/projects?category=innovation-research",
    "urbanism": "/projects?category=urbanism-masterplan",
    "methodology": "/about",
    "clients": "/about",
    "difference": "/about",
    "why_1pax": "/about",
    "careers": "/contact",
    "culture": "/the-team",
    "mentorship": "/the-team",
    "open_roles": "/contact",
    "values": "/about",
    "ethics": "/about",
    "social_commitment": "/about",
    "heritage": "/about",
    "people_values": "/about",
    "diversity": "/the-team",
    "governance": "/about",
    "suppliers": "/contact",
    "ip": "/patents",
    "ethics_plan": "/about",
    "pax_cart": "/projects/pax-cart-patent",
    "ecoport": "/projects/ecoport-patent",
}


PROJECT_URLS = {
    "sofia_airport": "/projects/sofia-airport-terminal-3-international-terminal-2-refurbishment",
    "belgrade_airport": "/projects/nikola-tesla-international-airport-phase-1-phase-2",
    "velana_airport": "/projects/velana-international-airport-new-terminal-building",
    "bordeaux_airport": "/projects/new-stainless-steel-and-glazed-facades-bordeaux-international-airport",
    "cayenne_terminal": "/projects/felix-eboue-airport-new-terminal",
    "nice_airport": "/projects/nice-cote-dazur-airport-terminal-boarding-gates-expansion",
    "pointe_a_pitre_t1": "/projects/pointe-a-pitre-international-airport-new-extension",
    "pointe_a_pitre_t2": "/projects/pointe-a-pitre-international-airport-t2-extension",
    "annecy_airport": "/projects/annecy-general-aviation-terminal",
    "conakry_airport": "/projects/conakry-international-airport-expansion",
    "papeete_airport": "/projects/papeete-faa-a-international-airport",
    "amilcar_cabral_airport": "/projects/cabo-verde-assistance-for-the-concession-of-7-airports",
    "nelson_mandela_airport": "/projects/cabo-verde-assistance-for-the-concession-of-7-airports",
    "aristides_pereira_airport": "/projects/cabo-verde-assistance-for-the-concession-of-7-airports",
    "lille_airport": "/projects/lille-international-airport",
    "fuzhou_airport": "/projects/fuzhou-airport-international-airport-terminal-rail-integration-",
    "euroairport_modernization": "/projects/euroairport-terminal-modernization",
    "lanzhou_airport": "/projects/lanzhou",
    "mashhad_airport": "/projects/new-mashad-international-airport-extension-terminal",
    "almaty_airport": "/projects/almaty-international-airport-masterplanning-new-terminal-design",
    "euroairport_south_gates": "/projects/euroairport-extension-terminal-south-gates",
    "kigali_airport": "/projects/kigali-new-passenger-terminal-building-consultancy-for-redesign-construction",
    "tocumen_airport": "/projects/tocumen-international-airport-consultancy-fire-safety-strategy-review",
    "cusco_airport": "/projects/alejandro-velasco-astete-airport-rehabilitation-extension-diagnostic-",
    "jaipur_airport": "/projects/jaipur-international-airport",
    "ahmedabad_airport": "/projects/ahmedabad-airport-consultancy",
    "pachacamac_metro_station": "/projects/intermodal-metro-station-pachacamac-line-1-extension",
    "belgrade_metro_line1": "/projects/belgrade-metro-network-line-1-phase-1",
    "cergy_vertiport": "/projects/first-european-taxidrone-vertiport",
    "singapore_vertiport": "/projects/vertiport-in-singapore",
    "paris_heliport": "/projects/heliport-de-paris-issy-les-molineaux",
    "cabo_verde_airports": "/projects/cabo-verde-assistance-for-the-concession-of-7-airports",
    "belgrade_nikola_tesla_landside": "/projects/nikola-tesla-airport-landside-design-vehicles-simulation",
    "lima_metro_line1_stations": "/projects/lima-metro-line-1-multimodal-station-sizing-urban-insertion--1w2pu",
    "cayenne_airport_masterplan": "/projects/feliz-eboue-airport-masterplan",
    "doha_metro_depot": "/projects/qatar-railways-alwakrah-metro-depot-masterplan",
    "chateauroux_atct_mro": "/projects/chateauroux-atct-mro",
    "riga_control_tower": "/projects/riga-international-airport-new-control-tower-offices",
    "belgrade_fire_station": "/projects/belgrade-airport-main-fire-station-architectural-design",
    "cdg_baggage_building": "/projects/design-building-for-baggage-handling-charles-de-gaulle-airport",
    "le_bourget_fire_station": "/projects/new-fire-station-paris-le-bourget-airport",
    "air_guyane_hangar": "/projects/hangar-for-air-guyanne-cayenne-airport",
    "belgrade_admin_building": "/projects/belgrade-airport-administration-building",
    "tokyo_eu_delegation": "/projects/european-commission-building-new-delegation-building-architectural-design",
    "french_embassy_bangkok": "/projects/french-embassy-in-bangkok-architectural-design",
    "cayenne_airport_offices": "/projects?category=working-and-living",
    "qatar_railways_hq": "/projects/qatar-railways-headquarters",
    "greyfoot_paris": "/projects?category=urbanism-masterplan",
    "montijo_airport_commercial": "/projects/montijo-airport-passenger-experience-design-commercial-areas",
    "jorge_chavez_food_hall": "/projects/food-hall-design-jorge-chavez-international-airport",
    "lima_peru_plaza_food_court": "/projects/peru-airport-food-court-look-and-feel",
    "marseille_commercial_assistance": "/projects/aeroport-de-marseille-provence-architectural-assistance-for-the-commercial-facilities-implementation",
    "belgrade_wayfinding": "/projects/nikola-tesla-international-airport-wayfinding-signage-design",
    "nantes_commercial_zone": "/projects/nantes-atlantique-airport-development-of-the-commercial-zone",
    "lyon_retail_shell": "/projects/retail-shell-lyon-airport-commercial-design",
    "aik_bank_design": "/projects/aik-bank-branches-atm-network-design",
    "cayenne_interior_design": "/projects/felix-eboue-cayenne-airport",
    "santiago_wayfinding": "/projects/santiago-international-airport-wayfinding-design-signage",
}


PROJECT_COVER_IMAGE_URLS = {
    "sofia_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b731a42dd546d2c4ab4c40_Sofia_2.webp",
    "belgrade_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72d78c81fa27714a14af9_Belgrade_1.webp",
    "velana_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d620e795a4130c5cac9436_velana_night.webp",
    "bordeaux_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d64a0bd611f475c8bec76c_Bordeaux%204.webp",
    "cayenne_terminal": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72cb5619866dcc244016a_Cayenne-Exterior-02.webp",
    "nice_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b731f435af8d0cca357cb3_Nice_2.webp",
    "pointe_a_pitre_t1": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72f97ec7dba6c9452347e_Vue%203D%201%20-%20Hall%20D%C3%A9parts.webp",
    "pointe_a_pitre_t2": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d610336cab42ba47db2676_guadeloupe_aerial_render.webp",
    "annecy_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72e5180d08e6d6e510972_Annecy_2.webp",
    "conakry_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72dbae6d9b9532301b1e7_Conakrys_2.webp",
    "papeete_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7316fdb6fe97935439f29_Papeete_4.webp",
    "amilcar_cabral_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b727a49925d9a7b373b7e0_Amilcar_1%20(1).webp",
    "nelson_mandela_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b727a49925d9a7b373b7e0_Amilcar_1%20(1).webp",
    "aristides_pereira_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b727a49925d9a7b373b7e0_Amilcar_1%20(1).webp",
    "lille_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72f688d878d06e00234dc_Lille_2.webp",
    "fuzhou_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72a8988365294c2f38404_Fuzhou_1.webp",
    "euroairport_modernization": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72a5a8f681919e0a217b6_Mulhouse_6.webp",
    "lanzhou_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7301579e21070d9c173a3_lanzhou1.webp",
    "mashhad_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b731c5e1292ea5e551606c_Mashad-01.webp",
    "almaty_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72e724700d7158543d179_Almaty.webp",
    "euroairport_south_gates": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72a6f069714d69034a913_Euroair_2.webp",
    "kigali_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2be542976bbd777155517_Kigali_1.jpg",
    "tocumen_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b3fafbf3969991400e90d7_Tocumen_2.jpg",
    "cusco_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d7b4449f60716e22551587_google_earth_cusco.webp",
    "jaipur_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d6ac4e0dd895bc1d0da1a5_google_earth_jaipur.webp",
    "ahmedabad_airport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d6acb773d69e3bc4a7f594_google_earth_ahmedabad.webp",
    "pachacamac_metro_station": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d8b2a87755f2a8d574c03b_Metro_Per_1%20(1).webp",
    "belgrade_metro_line1": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7343bb732de7af410ceb5_bgmetro.webp",
    "cergy_vertiport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d4dfccb94d9642209085d5_vertiport_4.webp",
    "singapore_vertiport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b44d9cd3afdad6dce9a72e_singapore1.png",
    "paris_heliport": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d76245f8aabbfab1b6b5df_issy-heliport.webp",
    "cabo_verde_airports": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b727a49925d9a7b373b7e0_Amilcar_1%20(1).webp",
    "belgrade_nikola_tesla_landside": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d615b56c1e2de287a3369f_Belgrade_Landside_2.webp",
    "lima_metro_line1_stations": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d8b295f2040f9d17241d8f_google_earth_pachacamac.webp",
    "cayenne_airport_masterplan": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69dcf4f2db67f97b2d5459be_google_earth_cayenne.webp",
    "doha_metro_depot": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69de74420ca661665cea20ad_al-whakra.webp",
    "chateauroux_atct_mro": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2afe492addfb0541456e2_chateroux-02.png",
    "riga_control_tower": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69c552917361e01b677045ae_Riga_1.webp",
    "belgrade_fire_station": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2ba7de00d9e5080393719_Belgrade_1.jpg",
    "cdg_baggage_building": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2afa3621256fe7061c72d_Baggage_1.jpg",
    "le_bourget_fire_station": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2b9ddc150ff948a740ce0_Paris_3.jpg",
    "air_guyane_hangar": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72bf63ca1a998b25176fe_Cayenne-Hangar-01.webp",
    "belgrade_admin_building": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b733d28c80a0d49cb846ed_Belgrade_Adm_4.webp",
    "tokyo_eu_delegation": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b733a7646bd86ef340abda_Europe_Comm_3.webp",
    "french_embassy_bangkok": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b733809925d9a7b374c1cb_Ambassy_1.webp",
    "qatar_railways_hq": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7334adf2e8e3a6210d367_hqqatar.webp",
    "montijo_airport_commercial": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7366186bba992b516bd74_Montijo%203.webp",
    "jorge_chavez_food_hall": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d7832fed48e1679fac071b_perufood.webp",
    "lima_peru_plaza_food_court": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b737d507c7d17ce8c931e6_Plaza%2010.webp",
    "marseille_commercial_assistance": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7368dd93944d5c17044c5_Marseille%203.webp",
    "belgrade_wayfinding": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7376c20d86875e8bbc19d_Nikola%201.webp",
    "nantes_commercial_zone": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7363e2dd546d2c4abb90f_Nantes%205.webp",
    "lyon_retail_shell": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b735152e926afdfcea29ee_Retail%201.webp",
    "aik_bank_design": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b735673d3153253073c288_Bank%203.webp",
    "cayenne_interior_design": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72aae415b59c2d80a939c_Int%C3%A9rieures%205.webp",
    "santiago_wayfinding": "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b737fb18420a09e87493df_Santiago%201.webp",
}


CATEGORY_COVER_IMAGE_URLS = {
    "Airports and Transportation": "https://cdn.prod.website-files.com/6983bc668441027a79467328/699725e2cc83eb4a557787d5_Airports.jpg",
    "Urbanism and Masterplan": "https://cdn.prod.website-files.com/6983bc668441027a79467328/699726563f6abc816052d700_masterplan.webp",
    "Innovation and Research": "https://cdn.prod.website-files.com/6983bc668441027a79467328/6a0332c7fb59828f87489a05_pax_category_dropdown_crop.webp",
    "Future of Mobility": "https://cdn.prod.website-files.com/6983bc668441027a79467328/699726a67f7abfa1b05a1a8a_Future-of-Mobility.webp",
    "Industrial Buildings": "https://cdn.prod.website-files.com/6983bc668441027a79467328/69972714995d682f63deb686_Buildings.jpg",
    "Interior Design": "https://cdn.prod.website-files.com/6983bc668441027a79467328/699727463b3c8206c163270e_Interior-Design.jpg",
    "Working and Living": "https://cdn.prod.website-files.com/6983bc668441027a79467328/6997277402239147f840311e_Working-and-Living.webp",
    "BIM": "https://cdn.prod.website-files.com/6983bc668441027a79467328/699727a03addcb335360a644_BIM.webp",
}


CATEGORY_URLS = {
    "Airports and Transportation": "/projects?category=airports-railstations",
    "Urbanism and Masterplan": "/projects?category=urbanism-masterplan",
    "Innovation and Research": "/projects?category=innovation-research",
    "Future of Mobility": "/projects?category=future-of-mobility",
    "Industrial Buildings": "/projects?category=industrial-buildings",
    "Interior Design": "/projects?category=retail-and-interior-design",
    "Working and Living": "/projects?category=working-and-living",
    "BIM": "/projects?category=bim",
}


def project_url(project_key: str, category: Optional[str] = None) -> str:
    """Return the best website URL for a project."""
    path = PROJECT_URLS.get(project_key)
    if not path and category:
        path = CATEGORY_URLS.get(category)
    return absolute_url(path or MAIN_LINKS["projects"])


def project_cover_image_url(project_key: str, category: Optional[str] = None) -> str:
    """Return the best website-hosted cover image for a project."""
    return PROJECT_COVER_IMAGE_URLS.get(project_key) or (
        CATEGORY_COVER_IMAGE_URLS.get(category or "")
    ) or ""


def company_url(data_key: str) -> str:
    """Return the best website URL for a company info key."""
    return absolute_url(COMPANY_URLS.get(data_key, MAIN_LINKS["about"]))


def service_url(data_key: str) -> str:
    """Return the best website URL for a service info key."""
    return absolute_url(SERVICE_URLS.get(data_key, MAIN_LINKS["projects"]))


def team_url() -> str:
    """Return the website URL for team queries."""
    return absolute_url(MAIN_LINKS["team"])


def append_site_link(text: str, label: str, url: str) -> str:
    """Append a consistent website navigation link to a response."""
    if not url:
        return text
    return f"{text}\n\nView on the 1PAX website: [{label}]({url})"
