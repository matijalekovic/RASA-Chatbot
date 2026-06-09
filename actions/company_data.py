"""
1PAX Company Information — Structured Response Data
====================================================
All answers to customer/visitor questions about 1PAX as a studio.
Source: company_info_raw.txt

Each key maps to one or more chatbot response messages.
Multi-part responses are lists; single messages are strings.
"""


CLIENT_PROFILES = {
    "vinci_airports": {
        "display_name": "VINCI Airports",
        "kind": "global airport operator and private concessionaire",
        "geography": (
            "French-headquartered global airport network. In the 1PAX portfolio, VINCI-related work "
            "appears across France, Serbia, Portugal, Cabo Verde, French Polynesia, Iran, Peru, India, "
            "Kazakhstan, and airport retail contexts."
        ),
        "does": (
            "VINCI Airports operates and develops airports through concession, investment, capacity, "
            "commercial, and passenger-experience programs."
        ),
        "relationship": (
            "VINCI Airports is one of the most recurrent client ecosystems in the 1PAX portfolio. "
            "1PAX has supported concession bids, terminal concepts, masterplanning, landside design, "
            "commercial areas, feasibility studies, and operational diagnostics."
        ),
        "client_type": "Private concessionaire / airport operator",
        "sectors": ("airport", "aviation", "concessionaire", "private", "commercial"),
        "regions": ("Europe", "Africa", "Asia", "Latin America", "Oceania"),
        "aliases": (
            "VINCI Airports",
            "Vinci Airports",
            "Vinci",
            "VINCI",
            "Vinci Airports Serbia",
            "Vinci Airports concession",
            "Vinci Cabo Verde",
            "VINCI Airports / ANA Aeroportos",
            "VINCI Airports Serbia / Belgrade Airport",
            "Aéroport de Nantes Atlantique / Vinci Airports",
        ),
    },
    "sof_connect": {
        "display_name": "SOF Connect",
        "kind": "airport concession company",
        "geography": "Sofia, Bulgaria.",
        "does": "SOF Connect is the concession company behind Sofia Airport's transformation program.",
        "relationship": (
            "SOF Connect commissioned 1PAX for the Sofia Airport Terminal 3 International and Terminal 2 "
            "refurbishment program, a major 110,000 m² airport transformation targeting a 5-Star regional hub."
        ),
        "client_type": "Private airport concessionaire",
        "sectors": ("airport", "aviation", "concessionaire", "private"),
        "regions": ("Europe", "Balkans"),
        "aliases": ("SOF Connect", "Sofia Airport concession", "SOF", "Sofia concessionaire"),
        "project_keys": ("sofia_airport",),
    },
    "belgrade_airport": {
        "display_name": "Belgrade Airport",
        "kind": "airport operator and concession client",
        "geography": "Belgrade, Serbia.",
        "does": "Belgrade Airport operates Serbia's main international gateway under the VINCI Airports concession.",
        "relationship": (
            "1PAX has supported Belgrade Airport across terminal expansion, wayfinding, landside design, "
            "fire-station infrastructure, and administration-building work."
        ),
        "client_type": "Airport operator / concession client",
        "sectors": ("airport", "aviation", "public-private", "concessionaire"),
        "regions": ("Europe", "Balkans", "Serbia"),
        "aliases": (
            "Belgrade Airport",
            "Nikola Tesla Airport",
            "Belgrade Nikola Tesla Airport",
            "VINCI Airports Serbia",
            "Belgrade Airport concession",
            "BEG",
        ),
        "project_keys": (
            "belgrade_airport",
            "belgrade_nikola_tesla_landside",
            "belgrade_fire_station",
            "belgrade_admin_building",
            "belgrade_wayfinding",
        ),
    },
    "groupe_adp": {
        "display_name": "Groupe ADP",
        "kind": "airport operator, infrastructure owner, and mobility ecosystem partner",
        "geography": "Paris / France, with international airport and mobility operations.",
        "does": (
            "Groupe ADP operates major Paris airport infrastructure and participates in emerging mobility "
            "programs, including heliport and vertiport experimentation."
        ),
        "relationship": (
            "1PAX's ADP-linked work includes Paris Heliport, Cergy-Pontoise vertiport, Paris-CDG baggage "
            "infrastructure, and Paris-Le Bourget fire-station design competitions or commissions."
        ),
        "client_type": "Airport operator / public-private infrastructure group",
        "sectors": ("airport", "aviation", "future mobility", "industrial", "public-private"),
        "regions": ("Europe", "France"),
        "aliases": ("Groupe ADP", "ADP", "Paris ADP", "Aéroports de Paris", "Aeroports de Paris"),
        "project_keys": (
            "paris_heliport",
            "cergy_vertiport",
            "cdg_baggage_building",
            "le_bourget_fire_station",
        ),
    },
    "skyports": {
        "display_name": "Skyports",
        "kind": "advanced air mobility infrastructure company",
        "geography": "International advanced air mobility ecosystem, represented in 1PAX work in France and Singapore.",
        "does": (
            "Skyports develops infrastructure for eVTOL, drone, vertiport, and advanced air mobility operations."
        ),
        "relationship": (
            "1PAX worked with Skyports on future-mobility infrastructure including the first European "
            "Taxidrone Vertiport at Cergy-Pontoise and a Singapore VoloPort competition concept."
        ),
        "client_type": "Future-mobility infrastructure operator",
        "sectors": ("future mobility", "advanced air mobility", "aviation", "private"),
        "regions": ("Europe", "Asia"),
        "aliases": ("Skyports", "Skyports Infrastructure", "VoloPort", "Voloport"),
        "project_keys": ("cergy_vertiport", "singapore_vertiport"),
    },
    "qatar_railways": {
        "display_name": "Qatar Railways",
        "kind": "rail and metro infrastructure authority",
        "geography": "Doha, Qatar.",
        "does": "Qatar Railways develops and operates major rail and metro infrastructure in Qatar.",
        "relationship": (
            "1PAX's Qatar Railways-linked work appears through consortium and engineering relationships, "
            "including the Doha West Metro Depot masterplan and Qatar Railways Headquarters competition."
        ),
        "client_type": "Public transport authority / rail operator",
        "sectors": ("transport", "metro", "rail", "public", "government"),
        "regions": ("Middle East", "Gulf Region", "Qatar"),
        "aliases": (
            "Qatar Railways",
            "Qatar Rail",
            "Qatar Railways HQ",
            "Qatar Rail HQ",
            "Doha Metro",
            "Doha West Metro Depot",
        ),
        "project_keys": ("doha_metro_depot", "qatar_railways_hq"),
    },
    "setec_siemens_besix_tso": {
        "display_name": "SETEC / Siemens / BESIX / TSO",
        "kind": "engineering, technology, construction, and rail-infrastructure consortium partners",
        "geography": "Qatar project context, with international engineering and technology partners.",
        "does": (
            "These organizations support complex engineering, systems, construction, and rail-infrastructure "
            "delivery."
        ),
        "relationship": (
            "1PAX worked in this consortium context on Doha West Metro Depot and Qatar Railways Headquarters, "
            "bridging architectural, masterplanning, rail, and technical infrastructure requirements."
        ),
        "client_type": "Engineering / technology / construction partner group",
        "sectors": ("transport", "metro", "rail", "technology", "engineering", "private"),
        "regions": ("Middle East", "Qatar"),
        "aliases": (
            "SETEC",
            "SETEC BÂTIMENT",
            "SETEC BATIMENT",
            "SETEC TPI",
            "Siemens",
            "BESIX",
            "TSO",
            "SETEC BÂTIMENT / Siemens / BESIX / TSO",
            "SETEC TPI / Siemens",
        ),
        "project_keys": ("doha_metro_depot", "qatar_railways_hq"),
    },
    "lagardere_travel_retail": {
        "display_name": "Lagardère Travel Retail",
        "kind": "travel retail and airport commercial operator",
        "geography": "International travel retail group; 1PAX's highlighted work is in Callao / Lima, Peru.",
        "does": "Lagardère Travel Retail develops and operates retail, food, and commercial experiences in travel hubs.",
        "relationship": (
            "1PAX designed the Jorge Chávez International Airport Food Hall for Lagardère Travel Retail, "
            "focusing on passenger experience, dining identity, and airport commercial design."
        ),
        "client_type": "Private travel retail operator",
        "sectors": ("commercial", "retail", "airport", "private", "interior"),
        "regions": ("Latin America", "South America", "Peru"),
        "aliases": ("Lagardère Travel Retail", "Lagardere Travel Retail", "Lagardère", "Lagardere"),
        "project_keys": ("jorge_chavez_food_hall",),
    },
    "edeis_colas": {
        "display_name": "EDEIS COLAS",
        "kind": "airport infrastructure and operations client group",
        "geography": "French Guiana airport context.",
        "does": "EDEIS COLAS appears in the portfolio as the client group for Félix Eboué Cayenne Airport work.",
        "relationship": (
            "1PAX's EDEIS COLAS work spans a full airport ecosystem in French Guiana: terminal extension, "
            "masterplan, Air Guyane hangar, office buildings, and terminal interior design."
        ),
        "client_type": "Airport infrastructure client / operator context",
        "sectors": ("airport", "aviation", "industrial", "working and living", "interior"),
        "regions": ("Latin America", "South America", "French Guiana"),
        "aliases": ("EDEIS COLAS", "EDEIS", "COLAS", "Félix Eboué Airport", "Felix Eboue Airport"),
        "project_keys": (
            "cayenne_terminal",
            "cayenne_airport_masterplan",
            "air_guyane_hangar",
            "cayenne_airport_offices",
            "cayenne_interior_design",
        ),
    },
    "city_of_belgrade": {
        "display_name": "City of Belgrade",
        "kind": "municipal public authority",
        "geography": "Belgrade, Serbia.",
        "does": "The City of Belgrade leads city-scale public infrastructure and mobility development.",
        "relationship": (
            "1PAX worked on the Belgrade Metro Network Line 1 Phase 1 architectural design, giving the "
            "metro stations a unified identity and passenger-oriented spatial strategy."
        ),
        "client_type": "Municipality / public authority",
        "sectors": ("public", "government", "transport", "urban", "metro"),
        "regions": ("Europe", "Balkans", "Serbia"),
        "aliases": ("City of Belgrade", "Belgrade city", "Belgrade municipality", "Belgrade public authority"),
        "project_keys": ("belgrade_metro_line1",),
    },
    "atu": {
        "display_name": "ATU (Autoridad de Transporte Urbano)",
        "kind": "urban transport authority",
        "geography": "Lima, Peru.",
        "does": "ATU coordinates urban transport infrastructure for metropolitan Lima.",
        "relationship": (
            "1PAX designed the Intermodal Metro Station Pachacámac for the Lima Metro Line 1 Extension, "
            "including station programming and architectural design."
        ),
        "client_type": "Public transport authority",
        "sectors": ("public", "government", "transport", "metro", "urban"),
        "regions": ("Latin America", "South America", "Peru"),
        "aliases": ("ATU", "Autoridad de Transporte Urbano", "Lima transport authority"),
        "project_keys": ("pachacamac_metro_station",),
    },
    "aate": {
        "display_name": "AATE (Autonomous Authority for the Electric Train)",
        "kind": "electric train and metro authority",
        "geography": "Lima, Peru.",
        "does": "AATE is tied to electric train and metro infrastructure in Lima.",
        "relationship": (
            "1PAX worked on Lima Metro Line 1 multimodal station sizing and urban insertion, defining "
            "new station and intermodality scenarios."
        ),
        "client_type": "Public transport authority",
        "sectors": ("public", "government", "transport", "metro", "urban"),
        "regions": ("Latin America", "South America", "Peru"),
        "aliases": ("AATE", "Autonomous Authority for the Electric Train", "Electric Train Authority"),
        "project_keys": ("lima_metro_line1_stations",),
    },
    "macl": {
        "display_name": "Maldives Airport Company Limited (MACL)",
        "kind": "airport company",
        "geography": "Malé, Maldives.",
        "does": "MACL is the airport company associated with Velana International Airport.",
        "relationship": (
            "1PAX delivered architectural and interior design for Velana International Airport's new "
            "102,000 m² international terminal, developed with Saudi Binladin Group."
        ),
        "client_type": "Airport operator / airport company",
        "sectors": ("airport", "aviation", "public-private"),
        "regions": ("Asia", "South Asia", "Indian Ocean"),
        "aliases": (
            "Maldives Airport Company Limited",
            "MACL",
            "Maldives Airport Company",
            "Velana Airport",
            "Saudi Binladin Group",
        ),
        "project_keys": ("velana_airport",),
    },
    "cabo_verde_airports": {
        "display_name": "Cabo Verde Airports",
        "kind": "airport network operator / concession context",
        "geography": "Cabo Verde, West Africa / Macaronesia.",
        "does": "Cabo Verde Airports is tied to airport network development across the country's islands.",
        "relationship": (
            "1PAX supported concession and masterplanning work for Cabo Verde's airport network, including "
            "Sal, Santiago, Boa Vista, and seven-airport concession assistance."
        ),
        "client_type": "Airport operator / public-private concession context",
        "sectors": ("airport", "aviation", "concessionaire", "public-private"),
        "regions": ("Africa", "West Africa", "Macaronesia"),
        "aliases": ("Cabo Verde Airports", "Cape Verde Airports", "Cabo Verde airport network"),
        "project_keys": (
            "cabo_verde_airports",
            "amilcar_cabral_airport",
            "nelson_mandela_airport",
            "aristides_pereira_airport",
        ),
    },
    "airport_authority_india": {
        "display_name": "Airport Authority of India",
        "kind": "national airport authority",
        "geography": "India.",
        "does": "The Airport Authority of India oversees airport infrastructure and development across India.",
        "relationship": (
            "1PAX worked on Jaipur International Airport feasibility studies and terminal strategy, and "
            "also has India-related feasibility and territorial strategy experience at Ahmedabad Airport."
        ),
        "client_type": "Public airport authority",
        "sectors": ("airport", "aviation", "public", "government"),
        "regions": ("Asia", "South Asia", "India"),
        "aliases": ("Airport Authority of India", "AAI", "India airport authority"),
        "project_keys": ("jaipur_airport", "ahmedabad_airport"),
    },
    "lima_airport_partners": {
        "display_name": "Lima Airport Partners / OSITRAN",
        "kind": "airport operator and transport infrastructure regulator context",
        "geography": "Callao / Lima, Peru.",
        "does": (
            "Lima Airport Partners is associated with Jorge Chávez International Airport, while OSITRAN "
            "is tied to infrastructure supervision and regulation in Peru."
        ),
        "relationship": (
            "1PAX redesigned the Peru Plaza food court at Jorge Chávez International Airport, working on "
            "landside passenger experience and commercial interior design."
        ),
        "client_type": "Airport operator / infrastructure regulator context",
        "sectors": ("airport", "commercial", "retail", "public-private", "interior"),
        "regions": ("Latin America", "South America", "Peru"),
        "aliases": ("Lima Airport Partners", "OSITRAN", "Jorge Chávez Airport", "Jorge Chavez Airport", "LAP"),
        "project_keys": ("lima_peru_plaza_food_court",),
    },
    "nuevo_pudahuel": {
        "display_name": "Nuevo Pudahuel",
        "kind": "airport concession operator",
        "geography": "Santiago de Chile, Chile.",
        "does": "Nuevo Pudahuel operates and develops Santiago International Airport's concession program.",
        "relationship": (
            "1PAX designed wayfinding and signage for Santiago International Airport's 200,000 m² terminal."
        ),
        "client_type": "Airport concession operator",
        "sectors": ("airport", "aviation", "concessionaire", "interior"),
        "regions": ("Latin America", "South America", "Chile"),
        "aliases": ("Nuevo Pudahuel", "Pudahuel", "Santiago Airport concession"),
        "project_keys": ("santiago_wayfinding",),
    },
    "european_commission": {
        "display_name": "European Commission",
        "kind": "European public institution",
        "geography": "European institution; 1PAX's highlighted project was in Tokyo, Japan.",
        "does": "The European Commission represents the European Union's executive institution.",
        "relationship": (
            "1PAX delivered architectural design for the European Commission New Delegation Building in Tokyo, "
            "including headquarters, offices, and diplomatic-use spaces."
        ),
        "client_type": "Public / diplomatic institution",
        "sectors": ("public", "government", "diplomatic", "working and living"),
        "regions": ("Europe", "Asia", "Japan"),
        "aliases": ("European Commission", "EU Commission", "European Delegation", "EU Delegation"),
        "project_keys": ("tokyo_eu_delegation",),
    },
    "french_ministry_foreign_affairs": {
        "display_name": "French Ministry of Foreign Affairs",
        "kind": "national government ministry",
        "geography": "France, with 1PAX's highlighted project in Bangkok, Thailand.",
        "does": "The ministry manages French diplomatic facilities and international representation.",
        "relationship": (
            "1PAX worked on the French Embassy in Bangkok, transforming a 4,500 m² diplomatic compound "
            "through refurbishment and architectural design."
        ),
        "client_type": "Government ministry / diplomatic institution",
        "sectors": ("public", "government", "diplomatic", "working and living"),
        "regions": ("Europe", "Asia", "Thailand"),
        "aliases": (
            "French Ministry of Foreign Affairs",
            "Ministère des Affaires Étrangères",
            "Ministere des Affaires Etrangeres",
            "French Embassy Bangkok",
            "French Embassy",
        ),
        "project_keys": ("french_embassy_bangkok",),
    },
    "ai_bank": {
        "display_name": "AIK Bank",
        "kind": "banking client",
        "geography": "Serbia, nationwide branch and ATM network.",
        "does": "AIK Bank is a banking organization with customer-facing branch and ATM environments.",
        "relationship": (
            "1PAX developed interior and exterior concepts for AIK Bank's branch and ATM network, covering "
            "60+ offices and banking touchpoints."
        ),
        "client_type": "Private banking client",
        "sectors": ("private", "commercial", "interior", "banking"),
        "regions": ("Europe", "Serbia"),
        "aliases": ("AIK Bank", "AIK", "AIK Bank branches"),
        "project_keys": ("aik_bank_design",),
    },
    "unibail": {
        "display_name": "Unibail",
        "kind": "urban development and real-estate client",
        "geography": "Paris, France.",
        "does": "Unibail appears in the portfolio in a mixed-use urban development context.",
        "relationship": (
            "1PAX designed Greyfoot, a 17,400 m² mixed-use urban development near Espace Champerret in Paris."
        ),
        "client_type": "Private urban developer",
        "sectors": ("private", "urban", "masterplan", "commercial", "working and living"),
        "regions": ("Europe", "France"),
        "aliases": ("Unibail", "Greyfoot", "Espace Champerret"),
        "project_keys": ("greyfoot_paris",),
    },
    "dgac_region_centre": {
        "display_name": "DGAC / Région Centre-Val de Loire",
        "kind": "public aviation and regional authority context",
        "geography": "Centre-Val de Loire, France.",
        "does": "DGAC and regional authorities are tied to aviation infrastructure, regional development, and public oversight.",
        "relationship": (
            "1PAX designed the Châteauroux Airport air traffic control tower and MRO development, including "
            "a 400 m² ATCT as part of a larger aviation infrastructure program."
        ),
        "client_type": "Public aviation / regional authority",
        "sectors": ("public", "government", "aviation", "industrial"),
        "regions": ("Europe", "France"),
        "aliases": ("DGAC", "Région Centre-Val de Loire", "Region Centre-Val de Loire", "Châteauroux Airport"),
        "project_keys": ("chateauroux_atct_mro",),
    },
    "riga_airport": {
        "display_name": "Riga International Airport (RIX)",
        "kind": "airport operator",
        "geography": "Riga, Latvia.",
        "does": "Riga International Airport operates Latvia's main international airport infrastructure.",
        "relationship": (
            "1PAX worked on a competition design for Riga Airport's new air traffic control tower and offices."
        ),
        "client_type": "Airport operator",
        "sectors": ("airport", "aviation", "industrial", "public-private"),
        "regions": ("Europe", "Baltics", "Latvia"),
        "aliases": ("Riga International Airport", "RIX", "Riga Airport", "Latvia airport"),
        "project_keys": ("riga_control_tower",),
    },
    "fuzhou_airport_authority": {
        "display_name": "Fuzhou Airport Authority",
        "kind": "airport authority",
        "geography": "Fuzhou, China.",
        "does": "Fuzhou Airport Authority is tied to airport planning, terminal development, and rail integration.",
        "relationship": (
            "1PAX worked on the Fuzhou New International Airport passenger terminal and rail integration "
            "competition, receiving 2nd Prize."
        ),
        "client_type": "Public airport authority",
        "sectors": ("airport", "aviation", "public", "government", "transport"),
        "regions": ("Asia", "China"),
        "aliases": ("Fuzhou Airport Authority", "Fuzhou Airport", "Fuzhou Changle Airport"),
        "project_keys": ("fuzhou_airport",),
    },
    "lanzhou_airport_authority": {
        "display_name": "Lanzhou Airport Authority / ECADI",
        "kind": "airport authority and design institute context",
        "geography": "Lanzhou, China.",
        "does": "The authority and ECADI context relates to large-scale airport masterplanning and terminal design.",
        "relationship": (
            "1PAX worked on the Lanzhou New International Airport masterplan and terminal design competition, "
            "a 377,000 m² proposal that received 2nd Prize."
        ),
        "client_type": "Public airport authority / design institute context",
        "sectors": ("airport", "aviation", "public", "government", "transport"),
        "regions": ("Asia", "China"),
        "aliases": ("Lanzhou Airport Authority", "ECADI", "Lanzhou Airport", "Lanzhou New International Airport"),
        "project_keys": ("lanzhou_airport",),
    },
    "qatar_airways_investments": {
        "display_name": "Vinci Construction / Qatar Airways Investments",
        "kind": "construction and aviation investment client context",
        "geography": "Kigali, Rwanda project context, with Middle East-linked aviation investment.",
        "does": (
            "The client context combines major construction delivery with aviation investment for a new "
            "international airport terminal."
        ),
        "relationship": (
            "1PAX provided value-engineering consultation and design review for Kigali/Bugesera New "
            "International Airport's 12-million-passenger terminal."
        ),
        "client_type": "Construction / aviation investment client context",
        "sectors": ("airport", "aviation", "private", "engineering"),
        "regions": ("Africa", "Rwanda", "Middle East"),
        "aliases": ("Vinci Construction", "Qatar Airways Investments", "Qatar Airways", "Bugesera Airport"),
        "project_keys": ("kigali_airport",),
    },
}


CLIENT_SEGMENTS = {
    "airport": {
        "title": "Airport operators, authorities, and concessionaires",
        "summary": (
            "This is the largest part of the 1PAX client base: airport operators, concessionaires, "
            "airport authorities, and aviation infrastructure owners."
        ),
        "client_keys": (
            "vinci_airports",
            "sof_connect",
            "belgrade_airport",
            "groupe_adp",
            "macl",
            "cabo_verde_airports",
            "airport_authority_india",
            "edeis_colas",
            "lima_airport_partners",
            "nuevo_pudahuel",
            "riga_airport",
            "fuzhou_airport_authority",
            "lanzhou_airport_authority",
        ),
    },
    "public": {
        "title": "Public-sector, government, and authority clients",
        "summary": (
            "1PAX works with public authorities at several scales: national ministries, city governments, "
            "airport authorities, transport agencies, diplomatic institutions, and regional aviation bodies."
        ),
        "client_keys": (
            "city_of_belgrade",
            "atu",
            "aate",
            "qatar_railways",
            "airport_authority_india",
            "european_commission",
            "french_ministry_foreign_affairs",
            "dgac_region_centre",
            "fuzhou_airport_authority",
            "lanzhou_airport_authority",
        ),
    },
    "private": {
        "title": "Private-sector, concession, retail, banking, and developer clients",
        "summary": (
            "1PAX also works for private operators, concessionaires, investors, developers, and commercial "
            "brands when the project depends on passenger experience, operational clarity, or spatial identity."
        ),
        "client_keys": (
            "vinci_airports",
            "sof_connect",
            "lagardere_travel_retail",
            "ai_bank",
            "unibail",
            "skyports",
            "qatar_airways_investments",
        ),
    },
    "transport": {
        "title": "Transport, metro, rail, and urban mobility clients",
        "summary": (
            "Beyond airports, 1PAX works with transport authorities and rail/metro stakeholders on station, "
            "depot, headquarters, and intermodal mobility work."
        ),
        "client_keys": ("city_of_belgrade", "atu", "aate", "qatar_railways", "setec_siemens_besix_tso"),
    },
    "future_mobility": {
        "title": "Future-mobility and advanced air mobility clients",
        "summary": (
            "1PAX's future-mobility work includes vertiports, heliport reconfiguration, eVTOL test infrastructure, "
            "and advanced air mobility concepts."
        ),
        "client_keys": ("skyports", "groupe_adp"),
    },
    "commercial": {
        "title": "Commercial, retail, interiors, and passenger-experience clients",
        "summary": (
            "These clients ask 1PAX to shape the parts of infrastructure that passengers see, understand, "
            "buy from, navigate, and remember."
        ),
        "client_keys": (
            "lagardere_travel_retail",
            "lima_airport_partners",
            "vinci_airports",
            "ai_bank",
            "unibail",
            "nuevo_pudahuel",
        ),
    },
    "technology": {
        "title": "Technology, engineering, and specialist delivery partners",
        "summary": (
            "For technically complex projects, 1PAX works inside engineering, technology, and construction "
            "ecosystems rather than only as a standalone architect."
        ),
        "client_keys": ("setec_siemens_besix_tso", "groupe_adp", "skyports", "vinci_airports"),
    },
    "middle_east": {
        "title": "Middle East and Gulf-region client contexts",
        "summary": (
            "1PAX's Middle East experience is strongest around Qatar rail/metro work and aviation-linked "
            "investment contexts, with additional regional airport experience in Mashhad."
        ),
        "client_keys": ("qatar_railways", "setec_siemens_besix_tso", "qatar_airways_investments", "vinci_airports"),
    },
    "latin_america": {
        "title": "Latin America and South America clients",
        "summary": (
            "1PAX's Latin American client base includes airports, transport authorities, concession operators, "
            "and commercial airport stakeholders."
        ),
        "client_keys": ("edeis_colas", "atu", "aate", "lima_airport_partners", "lagardere_travel_retail", "nuevo_pudahuel", "vinci_airports"),
    },
    "europe": {
        "title": "European clients",
        "summary": (
            "Europe is a major base for 1PAX relationships, including France, Serbia, Bulgaria, Portugal, "
            "Latvia, and wider European public institutions."
        ),
        "client_keys": (
            "vinci_airports",
            "sof_connect",
            "belgrade_airport",
            "groupe_adp",
            "city_of_belgrade",
            "european_commission",
            "french_ministry_foreign_affairs",
            "dgac_region_centre",
            "riga_airport",
            "ai_bank",
            "unibail",
        ),
    },
    "africa": {
        "title": "African and island-airport clients",
        "summary": (
            "1PAX's Africa-related work includes Cabo Verde airport concessions, Guinea airport expansion, "
            "Rwanda terminal consultation, and Indian Ocean aviation work."
        ),
        "client_keys": ("cabo_verde_airports", "vinci_airports", "qatar_airways_investments", "macl"),
    },
    "asia": {
        "title": "Asian clients and project contexts",
        "summary": (
            "1PAX's Asia portfolio includes China, Japan, Thailand, India, Singapore, Maldives, Iran, "
            "Kazakhstan, and Qatar-linked mobility work."
        ),
        "client_keys": (
            "fuzhou_airport_authority",
            "lanzhou_airport_authority",
            "airport_authority_india",
            "macl",
            "european_commission",
            "french_ministry_foreign_affairs",
            "skyports",
            "qatar_railways",
            "vinci_airports",
        ),
    },
    "serbia": {
        "title": "Serbian clients",
        "summary": "In Serbia, 1PAX's client base spans airport, metro, banking, and public-infrastructure work.",
        "client_keys": ("belgrade_airport", "city_of_belgrade", "vinci_airports", "ai_bank"),
    },
    "france": {
        "title": "French clients and French airport contexts",
        "summary": (
            "France is one of the densest areas in the 1PAX portfolio, spanning airports, heliports, "
            "industrial airport buildings, commercial facilities, public aviation, and urban development."
        ),
        "client_keys": ("vinci_airports", "groupe_adp", "dgac_region_centre", "unibail"),
    },
    "peru": {
        "title": "Peruvian clients",
        "summary": (
            "Peru combines airport passenger-experience work and public urban-transport projects in the "
            "1PAX portfolio."
        ),
        "client_keys": ("atu", "aate", "lima_airport_partners", "lagardere_travel_retail", "vinci_airports"),
    },
    "qatar": {
        "title": "Qatar clients and project contexts",
        "summary": (
            "Qatar-related work is centered on metro, rail, headquarters, and large infrastructure "
            "collaboration."
        ),
        "client_keys": ("qatar_railways", "setec_siemens_besix_tso", "qatar_airways_investments"),
    },
}

COMPANY_INFO = {

    # ── Who we are ───────────────────────────────────────────────────────────

    "overview": [
        (
            "**1PAX** is a forward-thinking architectural and innovation studio dedicated to reshaping "
            "the future of mobility and the way people experience the world."
        ),
        (
            "Founded in 2016 by Mabel Miranda, we are an interdisciplinary firm uniting architects, "
            "planners, urbanists, interior designers, engineers, and innovators — collaborating with "
            "mission-driven clients worldwide to shape spaces that flow effortlessly, celebrate culture, "
            "and anticipate the needs of tomorrow.\n\n"
            "Our expertise spans airport design, masterplanning, urban and regional mobility networks, "
            "eVTOL and heliport facilities, and patented innovations that push the boundaries of what "
            "mobility can become."
        ),
        (
            "Curious about our **design approach**, **where we operate**, **who founded us**, or "
            "**how to join the team**? Just ask."
        ),
    ],

    "name_meaning": [
        (
            "Our name — **1PAX** — stands for *one passenger*.\n\n"
            "It's a constant reminder of what guides every design decision we make: every journey "
            "begins with a single person, and every solution must honor that human experience.\n\n"
            "Before infrastructure, before technology, before scale — there is always one person "
            "whose story we are designing for. That's our compass."
        ),
    ],

    "mission": [
        (
            "**Our mission** is to design with purpose — to transform the way people and communities "
            "move, and to promote a more sustainable, seamless relationship between people and their "
            "environments.\n\n"
            "We believe architecture and engineering should serve people and respond to the world's "
            "most urgent challenges. Our work is guided by a commitment to improve lives, foster equity, "
            "and champion sustainable practices — contributing to a smarter, greener, and more resilient tomorrow."
        ),
    ],

    "history": [
        (
            "**1PAX was founded in 2016** by Mabel Miranda, with a clear mission: to design with purpose "
            "and reshape the way people and communities move through the world.\n\n"
            "Since then, the studio has grown into a global practice with offices in Paris, Belgrade, "
            "Shanghai, Barcelona, and Lima — a team that collectively speaks 13 languages, working on "
            "airports, transportation hubs, urban mobility networks, and future mobility infrastructure "
            "across five continents."
        ),
    ],

    # ── People ────────────────────────────────────────────────────────────────

    "founder": [
        (
            "**1PAX was founded in 2016 by Mabel Miranda** — an architect whose journey is defined by "
            "resilience, curiosity, and an unwavering desire to contribute to society."
        ),
        (
            "Born in a developing country, Mabel transformed what others might have seen as limitations "
            "into pathways for growth and impact. Her early experiences gave her a deep sense of purpose "
            "and the conviction that design can be a powerful tool for positive change.\n\n"
            "Driven by that belief, she sought out new cultures and built a global perspective that "
            "today defines the spirit of 1PAX.\n\n"
            "Her path is an inspiration not just for women, minorities, or students — but for anyone "
            "who dreams of building a better future. Mabel's story shows that no barrier — social, "
            "economic, or geographical — can stop those determined to make a meaningful difference."
        ),
    ],

    "team": [
        (
            "**1PAX is an interdisciplinary team** of architects, planners, urbanists, interior designers, "
            "graphic designers, engineers, and innovators — all working under one shared vision.\n\n"
            "Our international team collectively speaks **13 languages**, bringing together diverse "
            "backgrounds, perspectives, and experiences from our offices in Paris, Belgrade, Shanghai, "
            "Barcelona, and Lima. That richness of perspective isn't just celebrated here — it's the "
            "engine of our design process."
        ),
    ],

    # ── Where we are ─────────────────────────────────────────────────────────

    "offices": [
        (
            "**1PAX operates from five offices worldwide:**\n\n"
            "• **Paris** — headquarters\n"
            "• **Belgrade**\n"
            "• **Shanghai**\n"
            "• **Barcelona**\n"
            "• **Lima**\n\n"
            "This global presence lets us operate near **24/7 across time zones**, ensuring rapid "
            "response and seamless collaboration with clients wherever they are. Our team collectively "
            "speaks **13 languages**, making 1PAX a truly borderless studio."
        ),
    ],

    # ── What we do ────────────────────────────────────────────────────────────

    "expertise": [
        (
            "**1PAX specializes in:**\n\n"
            "• **Airport design** — terminal architecture, passenger experience, 5-Star certification\n"
            "• **Transportation hubs** — multimodal infrastructure and integrated mobility\n"
            "• **Urban mobility** — metro stations, bus rapid transit, regional mobility networks\n"
            "• **Future mobility** — eVTOL terminals, vertiports, heliports\n"
            "• **Masterplanning** — urban development and regenerative urbanism\n"
            "• **Interior design** — commercial spaces, wayfinding, brand environments\n"
            "• **Innovation & patents** — proprietary solutions that push mobility boundaries\n\n"
            "Since our founding, airports and transportation hubs have been our core specialty — "
            "making us a recognized player in large-scale, complex infrastructure. This depth also "
            "enables us to excel wherever user experience is paramount and the challenge is demanding."
        ),
    ],

    # ── How we design ─────────────────────────────────────────────────────────

    "approach": [
        (
            "**Our design approach rests on five principles:**\n\n"
            "**1. Human-Centered** — Every project starts with a deep understanding of user needs. "
            "We embrace simplicity that removes friction, and we pursue beauty — because it invites "
            "interaction and leaves a lasting impression.\n\n"
            "**2. Sustainable by Nature** — Society and the environment are at the heart of our process. "
            "We prioritize local materials, renewable energy, and intelligent resource use. "
            "Sustainability is a principle we live by, not an add-on.\n\n"
            "**3. Designing for the Future** — We design with tomorrow in mind. We anticipate how "
            "expectations will evolve and help our clients stay ahead of what's next.\n\n"
            "**4. Architecture that Inspires** — Each project becomes a dialogue between culture, "
            "environment, and the human experience — spaces that invite interaction and leave stories "
            "that linger.\n\n"
            "**5. Functional Creativity** — Every solution must be functional first. Our creativity "
            "is expressed in design, but also in how we achieve efficiency, sustainability, and an "
            "optimal user experience."
        ),
    ],

    "human_centered": [
        (
            "**Human-centered design is the foundation of everything at 1PAX.**\n\n"
            "Our name says it: *1PAX* — one passenger. Every great journey begins with a single person, "
            "and that person is never an afterthought in our process.\n\n"
            "We start every project with a deep understanding of user needs. We embrace simplicity that "
            "removes friction and increases accessibility. And we pursue beauty — because beauty invites "
            "interaction, sparks emotion, and leaves a lasting impression on the people who move through "
            "our spaces."
        ),
    ],

    "sustainability": [
        (
            "**Sustainability is a principle 1PAX lives by — not a checkbox.**\n\n"
            "We solve problems by inventing or integrating solutions that reduce carbon impact, "
            "prioritizing local materials, renewable energy systems, and intelligent resource use "
            "at every stage of design.\n\n"
            "Beyond individual buildings, our **regenerative urbanism** methodology treats the city "
            "as a living ecosystem — designing to actively restore environmental systems, strengthen "
            "social dynamics, and generate long-term economic value. We aim to reduce humanity's "
            "carbon footprint and contribute to a more resilient and balanced future."
        ),
        (
            "**In practice, this means:**\n\n"
            "• **Energy efficiency and carbon neutrality** embedded from day one\n"
            "• **Water reuse, waste reduction, and circular design** at every project stage\n"
            "• **Local, low-impact materials** and clean energy systems prioritized\n"
            "• **Zero-paper policy** in our daily operations\n"
            "• **Remote work** to drastically reduce commuting emissions\n\n"
            "Our target: **100% of projects to meet internal sustainability criteria and achieve "
            "BREEAM certification by 2028.**"
        ),
    ],

    "innovation": [
        (
            "**Innovation is both our method and our ambition.**\n\n"
            "We approach every challenge as researchers and innovators — embracing problems as "
            "opportunities to rethink, improve, and elevate the systems that connect our world. "
            "We leverage cutting-edge technologies and advanced materials to design genuinely novel "
            "experiences, always with intention.\n\n"
            "This includes **patented innovations** that push the boundaries of what mobility "
            "infrastructure can become — from eVTOL terminals to proprietary passenger experience "
            "solutions. The three innovation projects to know are **Ecoport**, **PAX / Passenger "
            "Assisted Xperience**, and **Skylo**. We don't just respond to the future; we help define it."
        ),
        (
            "**Current innovation portfolio:**\n\n"
            "• **Ecoport** — a protected modular vertiport system for advanced air mobility, designed "
            "to scale from compact drone/eVTOL operations to multimodal regional mobility hubs.\n"
            "• **PAX / Passenger Assisted Xperience** — a protected all-in-one mobility product "
            "that shifts between seat, cart, stroller, and stackable storage modes.\n"
            "• **Skylo** — a strategic research and design framework for aerial logistics and the "
            "low-altitude economy, connecting cities, peri-urban zones, and rural landscapes through "
            "drones and eVTOL aircraft.\n\n"
            "Ask about **Ecoport**, **PAX**, or **Skylo** for product-specific details."
        ),
    ],

    "urbanism": [
        (
            "**Regenerative urbanism is a core part of 1PAX's methodology.**\n\n"
            "We approach the city as a living ecosystem — designing beyond mere sustainability to "
            "actively restore environmental systems, strengthen social dynamics, and generate "
            "long-term economic value.\n\n"
            "Through context-driven, human-centered design and circular use of resources, we "
            "transform urban development into a resilient framework that regenerates places, "
            "enhances quality of life, and creates lasting public value."
        ),
    ],

    # ── How we work ───────────────────────────────────────────────────────────

    "methodology": [
        (
            "**How 1PAX works:**\n\n"
            "**Long-term relationships** — We embrace our clients' goals as our own, working side "
            "by side and anticipating their future needs so we can grow together. Time is our material.\n\n"
            "**Borderless operations** — Five offices across Paris, Belgrade, Shanghai, Barcelona, "
            "and Lima allow us to operate near 24/7 and respond rapidly.\n\n"
            "**Global reach, agile spirit** — We combine the resources of a large firm with the "
            "flexibility and passion of a young, responsive studio.\n\n"
            "**Rigorous process** — Our methodology aligns with global best practices. Beyond design, "
            "we provide strategic insight that supports the long-term success of every project.\n\n"
            "**Power of synergy** — Large-scale projects demand diverse professionals. We bring "
            "architects, urbanists, designers, and engineers together under one shared vision."
        ),
    ],

    "clients": [
        (
            "**We collaborate with mission-driven clients worldwide** — airports, governments, transit "
            "authorities, urban developers, and private investors working on transformative infrastructure.\n\n"
            "Our geographic reach spans five continents — **Europe** (France, Serbia, Spain, Portugal, "
            "Belgium, Latvia), **Africa** (Guinea, Cabo Verde, Rwanda, Senegal), **Asia** (China, Iran, "
            "Kazakhstan, Singapore, Maldives, Japan, India), **Latin America / South America** "
            "(Peru, Panama, Chile, Bolivia), and the **Middle East** (Qatar, Doha metro, Mashhad).\n\n"
            "Our website highlights **50+ clients and partners** across diplomacy, engineering, airport "
            "operations, transport authorities, and private-sector development."
        ),
        (
            "**Representative clients and public authorities include:**\n\n"
            "• **Airport operators and concessionaires** — VINCI Airports, SOF Connect, Belgrade Airport, "
            "Cabo Verde Airports, Maldives Airport Company Limited (MACL), ANA Aeroportos, Nuevo Pudahuel, "
            "Lima Airport Partners, Marseille Provence Airport, Riga International Airport, Airport "
            "Authority of India, Fuzhou Airport Authority, Lanzhou Airport Authority, Conakry-Gbessia "
            "International Airport, Aéroport de Bordeaux Mérignac, Aéroport de la Côte d'Azur, "
            "Aéroport de Guadeloupe Pôle Caraïbes, Aéroport de Nantes Atlantique, and "
            "Aéroport de Bâle-Mulhouse.\n"
            "• **Public, transport, and diplomatic institutions** — European Commission, French Ministry "
            "of Foreign Affairs, City of Belgrade, DGAC / Région Centre-Val de Loire, AATE, ATU, and "
            "OSITRAN.\n"
            "• **Mobility, engineering, and private-sector partners** — Groupe ADP, EGIS, EDEIS COLAS, "
            "SETEC BÂTIMENT, SETEC TPI, Siemens, BESIX, TSO, VINCI Construction, Qatar Airways "
            "Investments, Skyports Infrastructure, Lagardère Travel Retail, AIK Bank, Unibail, Eiffage "
            "Concession, ECADI, Saudi Binladin Group, and VCGP."
        ),
        (
            "We are proud to maintain long-standing relationships built on genuine collaboration and "
            "shared goals, not just project delivery. We embrace our clients' ambitions as our own "
            "and anticipate their future needs so we can grow together."
        ),
    ],

    "contact": [
        (
            "**Contact 1PAX**\n\n"
            "For general inquiries, email **contact@1pax.com** or call **+33 9 67 72 55 89**.\n\n"
            "For careers and applications: **hr@1pax.com**\n"
            "For news and media questions: **communications@1pax.com**"
        ),
        (
            "**Global office network:**\n\n"
            "The public 1PAX contact page lists offices in **Paris, Belgrade, Lima, Shanghai, "
            "Barcelona, and the United States**. Use **contact@1pax.com** or the contact form "
            "on 1pax.com for routing to the right office or team. For applications, the contact "
            "page also includes a CV upload field.\n\n"
            "You can also ask me to help schedule a meeting."
        ),
    ],

    # ── What makes us different ───────────────────────────────────────────────

    "difference": [
        (
            "**What sets 1PAX apart:**\n\n"
            "• **Deep mobility expertise** — airports and transportation have been our specialty since "
            "day one. Few firms match this depth.\n"
            "• **Truly interdisciplinary** — architecture, planning, interior design, engineering, and "
            "innovation under one roof, not in silos.\n"
            "• **Agile at global scale** — five international offices, 13 languages, near 24/7 "
            "operations, but we move with the speed and care of a studio.\n"
            "• **Human-centered by conviction** — 1PAX means *one passenger*. The user is never an "
            "afterthought.\n"
            "• **Innovation with patents** — we develop proprietary solutions, not just best practices.\n"
            "• **Long-term partnerships** — we build relationships that span years and multiple projects.\n"
            "• **Purpose-driven** — every project must improve lives or systems. That's not marketing; "
            "it's how we decide what to take on."
        ),
    ],

    "why_1pax": [
        (
            "**Why 1PAX matters:**\n\n"
            "With an unwavering focus on sustainability, human-centered design, and global collaboration, "
            "1PAX is at the forefront of transforming the built environment.\n\n"
            "Whether reshaping airports into green, multimodal hubs, integrating eVTOL technologies into "
            "urban spaces, or reimagining the passenger experience with innovative patents — 1PAX creates "
            "solutions that prioritize humanity and the planet.\n\n"
            "We are architects, engineers, and visionaries working as one team with one purpose: to "
            "design for the well-being of society and the future of humankind."
        ),
    ],

    # ── Careers ───────────────────────────────────────────────────────────────

    "careers": [
        (
            "**Join the 1PAX team.**\n\n"
            "1PAX welcomes people who believe design can shape a better world — architects, "
            "planners, urbanists, interior designers, landscape architects, engineers, 3D and graphic "
            "designers, digital specialists, and innovators who want their work to improve how people "
            "move through cities, airports, and public spaces."
        ),
        (
            "**What applicants usually want to know:**\n"
            "• We work across airport design, mobility, masterplanning, interiors, BIM, visualization, "
            "and innovation\n"
            "• Continuous mentorship from senior team members, including our founder\n"
            "• Real responsibility on major infrastructure projects\n"
            "• Flexible and remote-work policies where the role and project setup allow it\n"
            "• A collaborative, international, multicultural studio environment\n"
            "• A Graduate Fellowship Program for students and recent graduates\n\n"
            "To apply, send your details through the 1PAX contact page: "
            "[www.1pax.com/contact](https://www.1pax.com/contact)."
        ),
    ],

    "application": [
        (
            "**How to apply to 1PAX:**\n\n"
            "The best place to start is the 1PAX contact page: "
            "[www.1pax.com/contact](https://www.1pax.com/contact).\n\n"
            "If you are applying for a role, include a short note about the kind of opportunity you are "
            "seeking and the discipline you work in. For design and architecture roles, a CV/resume and "
            "portfolio are the most useful materials to share."
        ),
        (
            "**Helpful application details:**\n"
            "• Mention your location and availability\n"
            "• Share the role or discipline you are interested in\n"
            "• Include relevant project, studio, BIM, visualization, planning, or innovation experience\n"
            "• For portfolios, a concise PDF or a stable portfolio link is usually easiest to review\n"
            "• If you have a preferred office, remote setup, or start date, mention it clearly\n"
            "• Students and recent graduates can mention fellowship, internship, or junior opportunities\n\n"
            "The chatbot cannot receive files directly, so use the contact page rather than sending a CV here."
        ),
    ],

    "hiring_process": [
        (
            "**Hiring process at 1PAX:**\n\n"
            "Start by applying through [www.1pax.com/contact](https://www.1pax.com/contact). "
            "The team reviews applications against current studio needs, discipline fit, portfolio or "
            "experience, and alignment with 1PAX's values: human-centered design, sustainability, "
            "innovation, collaboration, and purpose."
        ),
        (
            "If there is a fit, the next step is usually a direct conversation with the team to understand "
            "your background, interests, availability, and how you could contribute to ongoing or future "
            "work. Current vacancies can change, so the contact page is the right place to express interest "
            "even when a specific opening is not listed in the chatbot."
        ),
        (
            "For application status, deadlines, or timing, the chatbot cannot see the recruiting inbox or "
            "confirm whether an application has been reviewed. Use "
            "[www.1pax.com/contact](https://www.1pax.com/contact) for follow-up, and include the same "
            "name and email you used in your original application."
        ),
    ],

    "candidate_profile": [
        (
            "**Who 1PAX looks for:**\n\n"
            "We look for curious, responsible, forward-thinking people who care about design quality and "
            "real-world impact. Airport experience is valuable, but it is not the only path in — 1PAX is "
            "multidisciplinary, so strong candidates can come from architecture, planning, engineering, "
            "urbanism, interiors, landscape, graphic design, BIM, visualization, research, and innovation."
        ),
        (
            "**Strong candidates often bring:**\n"
            "• Clear design thinking and attention to users\n"
            "• Comfort with collaboration across cultures, time zones, and disciplines\n"
            "• Technical discipline, communication skills, and ownership\n"
            "• Interest in sustainable, inclusive, future-ready mobility\n"
            "• Clear communication in an international environment; English is especially useful, and "
            "additional languages are a plus\n"
            "• Relevant tools for the role, such as BIM, Revit, Rhino, visualization, graphic design, "
            "research, or digital workflow experience\n"
            "• A portfolio or work sample that shows how they think, not just what they produced\n\n"
            "If that sounds like you, apply through "
            "[www.1pax.com/contact](https://www.1pax.com/contact)."
        ),
    ],

    "compensation_benefits": [
        (
            "**Compensation and benefits:**\n\n"
            "Salary, benefits, internship stipends, leave, and role-specific packages are not published "
            "through the chatbot because they depend on the role, seniority, location, contract type, and "
            "project setup."
        ),
        (
            "1PAX's people commitments include fair compensation, well-being, work-life balance, training, "
            "and flexible work models where possible. For a specific opportunity, ask through "
            "[www.1pax.com/contact](https://www.1pax.com/contact) and include the role, office, and level "
            "you are interested in."
        ),
    ],

    "visa_relocation": [
        (
            "**International applicants, visas, and relocation:**\n\n"
            "1PAX is an international studio, and the team is used to working across countries and time "
            "zones. Whether relocation, visa sponsorship, work permits, or a particular office setup can "
            "be supported depends on the role, location, timing, and legal requirements."
        ),
        (
            "If you would need visa support, relocation, remote work from another country, or a specific "
            "office arrangement, mention it clearly when applying through "
            "[www.1pax.com/contact](https://www.1pax.com/contact). The recruiting team is the right place "
            "to confirm what is possible for a given opportunity."
        ),
    ],

    "culture": [
        (
            "**Life at 1PAX:**\n\n"
            "We cultivate a **collaborative, positive, and supportive studio culture**. We believe "
            "creativity thrives when people find harmony between work and personal life — so we have "
            "implemented flexible remote-work policies that respect both productivity and wellbeing.\n\n"
            "Our international team spans five offices and 13 languages. The richness of different "
            "cultures and perspectives isn't just celebrated here — it's the engine of our design "
            "process. We are proud to have watched many team members grow with us over the past decade, "
            "taking on meaningful challenges with real impact."
        ),
        (
            "If you are exploring whether 1PAX is the right place for you, you can also ask about "
            "**open roles**, **how to apply**, **mentorship**, **candidate profile**, or **work arrangements**. "
            "Applications should go through [www.1pax.com/contact](https://www.1pax.com/contact)."
        ),
    ],

    "work_arrangements": [
        (
            "**Working arrangements at 1PAX:**\n\n"
            "1PAX is an international studio with offices in Paris, Belgrade, Shanghai, Barcelona, and Lima. "
            "The team is used to cross-border collaboration, different time zones, and flexible ways of "
            "working. Remote or flexible work can be part of the setup when the role, project, and team "
            "needs allow it."
        ),
        (
            "The day-to-day culture is collaborative and purpose-driven: people are trusted with meaningful "
            "responsibility, supported by senior mentorship, and expected to communicate clearly across "
            "disciplines. For role-specific arrangements, apply or ask through "
            "[www.1pax.com/contact](https://www.1pax.com/contact)."
        ),
        (
            "If you are wondering which office a role belongs to, whether remote or hybrid work is possible, "
            "or whether travel is expected, include those questions in your application note so the team can "
            "answer them in context."
        ),
    ],

    "mentorship": [
        (
            "**Career development and mentorship are central to 1PAX.**\n\n"
            "Our senior team — including founder Mabel Miranda — actively mentors young professionals, "
            "sharing experience, expertise, and time to help shape the next generation of leaders. "
            "We trust our people with meaningful challenges and provide the guidance they need to advance.\n\n"
            "For students and recent graduates, we offer a **Graduate Fellowship Program** — a structured "
            "pathway into the studio for emerging talent, especially those from underserved communities. "
            "At 1PAX, your ideas and your voice matter, regardless of your background."
        ),
        (
            "To ask about mentorship, junior roles, or future development opportunities, use "
            "[www.1pax.com/contact](https://www.1pax.com/contact)."
        ),
    ],

    "internships": [
        (
            "**Students, interns, and recent graduates:**\n\n"
            "1PAX supports emerging talent through mentorship and a Graduate Fellowship Program. Students, "
            "recent graduates, junior architects, planners, designers, and innovation-minded candidates can "
            "express interest even if they are still early in their career."
        ),
        (
            "When applying, explain your studies or recent experience, the discipline you want to grow in, "
            "and include a CV/resume and portfolio or sample work when relevant. Start here: "
            "[www.1pax.com/contact](https://www.1pax.com/contact)."
        ),
    ],

    "open_roles": [
        (
            "**Roles and disciplines 1PAX is interested in:**\n\n"
            "• Architecture\n"
            "• Interior Design\n"
            "• Planning\n"
            "• Landscape Architecture\n"
            "• Urbanism\n"
            "• 3D & Graphic Design\n"
            "• Innovation\n\n"
            "We welcome forward-thinking individuals at all career stages. Students and recent graduates "
            "should explore our **Graduate Fellowship Program**, and experienced candidates can express "
            "interest for senior or specialist roles even when a perfect vacancy is not listed in the chatbot. "
            "For current opportunities or speculative applications, visit "
            "[www.1pax.com/contact](https://www.1pax.com/contact)."
        ),
    ],

    # ── Values ────────────────────────────────────────────────────────────────

    "values": [
        (
            "**The values that guide 1PAX:**\n\n"
            "• **Human-centered** — people first, always\n"
            "• **Sustainable** — by conviction, not compliance\n"
            "• **Innovative** — as a method and an ambition\n"
            "• **Inclusive** — diverse voices, open doors\n"
            "• **Long-term** — designing for what comes next\n"
            "• **Collaborative** — with clients, communities, and each other\n"
            "• **Purpose-driven** — every project must improve lives or systems\n\n"
            "Our work is guided by a commitment to improve lives, foster equity, and build a more "
            "resilient and hopeful future for all."
        ),
    ],

    # ── Ethics & Sustainability pillars ──────────────────────────────────────

    "ethics": [
        (
            "**1PAX is built on a clear ethical framework** — architecture as a tool for a cleaner, "
            "fairer, and more conscious society.\n\n"
            "We align our principles with the **10 Principles of the UN Global Compact**, which we "
            "have applied to join — ensuring our actions generate measurable, transparent, and lasting impact."
        ),
        (
            "**Our commitments are structured around 8 ethical pillars:**\n\n"
            "1. **Sustainability at our core** — life-cycle thinking in every project\n"
            "2. **Social commitment** — inclusive design that improves lives\n"
            "3. **Culture and heritage** — respecting local identity in every context\n"
            "4. **We value our people** — safe, inclusive, growth-oriented workplace\n"
            "5. **Diversity and inclusion** — no discrimination, equal opportunity, LMIC Fellowship\n"
            "6. **Good governance** — ethics committee, anti-corruption, public annual report\n"
            "7. **Aligned partners** — suppliers held to the same standards we hold ourselves\n"
            "8. **Intellectual property** — protecting creativity and honoring authorship\n\n"
            "Ask me about any of these pillars individually."
        ),
    ],

    "social_commitment": [
        (
            "**Social Commitment — Architecture that serves people:**\n\n"
            "We design to improve people's lives. Every project considers the quality of life, "
            "accessibility, and well-being of both users and the communities they affect.\n\n"
            "• All our projects are **universally accessible** and follow an inclusive design approach\n"
            "• We invest in **research and innovation** to continuously improve social impact\n"
            "• Every project includes a **social impact assessment** after the design phase\n"
            "• A **post-completion evaluation** is conducted three years after delivery\n\n"
            "We publish annual impact reports and lessons learned to ensure full transparency."
        ),
    ],

    "heritage": [
        (
            "**Culture and Heritage Respect — Architecture rooted in culture:**\n\n"
            "We integrate local culture, heritage, and values into every project we create. "
            "We are committed to preserving cultural identity and ensuring our work never negatively "
            "impacts local communities or heritage sites.\n\n"
            "Before every design phase, we conduct a **cultural impact assessment** — to understand "
            "the context, the communities, and the stories embedded in each place. "
            "Architecture, for us, is always a conversation. Never an imposition."
        ),
    ],

    "people_values": [
        (
            "**We Value Our People — Empowering Talent with Purpose:**\n\n"
            "Our employees are our greatest asset. We bring together professionals from over "
            "**ten nationalities** who share common values: sustainability, functional creativity, "
            "innovation, and transparency.\n\n"
            "• A **safe, inclusive environment** that supports learning, well-being, and professional growth\n"
            "• Strong policies for **work–life balance**, mental health, and fair compensation\n"
            "• **Continuous training** for at least 80% of staff by 2028\n"
            "• Annual **employee well-being and satisfaction surveys**\n"
            "• **Flexible and remote work models** that respect both productivity and personal life"
        ),
    ],

    "diversity": [
        (
            "**Diversity, Inclusion, and Equal Opportunity:**\n\n"
            "We believe in gender equality and reject all forms of discrimination — based on race, "
            "religion, age, sexual orientation, political opinion, or disability.\n\n"
            "• **Equal opportunities** and active support for diversity at every level\n"
            "• **1PAX Grad Fellowship** — opens doors for talented architects from LMICs "
            "(Low- and Middle-Income Countries)\n"
            "• Active collaborations with educational institutions to **mentor underrepresented professionals**\n"
            "• **Annual diversity report** to track and publish our progress\n"
            "• Senior leadership maintains at least **50% female representation**\n\n"
            "We don't just talk about inclusion — we build it into our structure, our hiring, and our leadership."
        ),
    ],

    "governance": [
        (
            "**Ethical Governance that Builds Trust:**\n\n"
            "We uphold the highest ethical standards through transparent policies, training, and oversight. "
            "Strict protocols guide anti-corruption, conflicts of interest, due diligence, and donations.\n\n"
            "• An **Ethics and Sustainability Committee** ensures compliance and accountability\n"
            "• An **annual public ethics report** is published for full transparency\n"
            "• All governance and ethics policies are **published and regularly updated**\n"
            "• **Annual ethics reviews** ensure ongoing alignment with our principles\n"
            "• Full compliance with **anti-corruption and transparency protocols** guaranteed\n\n"
            "Our approach to governance isn't compliance-driven — it's conviction-driven."
        ),
    ],

    "suppliers": [
        (
            "**Partners and Providers Aligned with Our Values:**\n\n"
            "We choose to work with companies that share our values and ethical standards. "
            "All partners and providers are expected to comply with our **Supplier Code of Conduct** — "
            "incorporating environmental, social, and governance principles.\n\n"
            "• We prioritize suppliers with **sustainable practices, anti-corruption policies, "
            "and human rights protections**\n"
            "• We favor **local suppliers and manufacturers** to reduce transport emissions and "
            "strengthen local economies\n"
            "• Goal: **100% of suppliers to comply** with our sustainability and ethics standards by 2028\n"
            "• **Continuous improvement plans** implemented for all key supplier relationships"
        ),
    ],

    "ip": [
        (
            "**Protecting Creativity and Intellectual Property:**\n\n"
            "In architecture, ideas become lasting structures — and every design carries the imprint "
            "of its creator. At 1PAX, respecting intellectual property is a core value.\n\n"
            "We protect the creative work of our studio and honor the contributions of every team member. "
            "We encourage creativity and respect authorship — because safeguarding ideas is essential "
            "to preserving innovation, ensuring fairness, and allowing creativity to thrive with "
            "purpose and respect."
        ),
    ],

    "ethics_plan": [
        (
            "**1PAX 2026–2028 Ethics and Sustainability Plan:**\n\n"
            "We are fully committed to living up to our goals. This plan outlines priority actions "
            "for the next three years, structured through seven strategic lines with measurable objectives:"
        ),
        (
            "**The seven commitments:**\n\n"
            "• **Sustainability** — 100% of projects BREEAM-certified by 2028; annual clean energy "
            "and ecosystem reviews\n"
            "• **Social impact** — social impact assessments after design; post-completion evaluation "
            "3 years after delivery; annual impact reports\n"
            "• **Cultural respect** — cultural impact assessments before every design phase\n"
            "• **Our people** — 80% of staff continuously trained by 2028; annual well-being surveys; "
            "flexible work models\n"
            "• **Diversity** — annual Grad Fellowship for LMIC architects; 50% female senior leadership\n"
            "• **Governance** — full policy publication by 2026; annual ethics review; "
            "anti-corruption compliance\n"
            "• **Suppliers** — 100% supplier compliance with ethics and sustainability standards by 2028; "
            "local sourcing priority"
        ),
    ],

    # ── Innovation products ───────────────────────────────────────────────────

    "patents": [
        (
            "**1PAX patents and proprietary innovation**\n\n"
            "The 1PAX website highlights **4 registered patents in aviation design**. The "
            "public innovation pages I can confidently name focus on passenger mobility, "
            "airport operations, and advanced air mobility infrastructure."
        ),
        (
            "**Publicly highlighted patents and innovation projects include:**\n\n"
            "• **PAX Cart / Passenger Assisted Xperience** — a patented all-in-one mobility device "
            "for airports and mobility hubs. It combines **seat, cart, stroller, and stackable unit** "
            "in one object, with smart-infrastructure options such as wireless charging, QR connectivity, "
            "passenger app integration, geolocation, usage analytics, and BIM integration. "
            "Patent references: **EU 4096986B1** and **CN 202530430900.9**.\n"
            "• **Ecoport** — a modular multimodal vertiport system for future-ready mobility. "
            "It is based on a **30 x 30 m modular grid**, supports phased deployment, and integrates "
            "eVTOL aircraft, helicopters, electric buses, ground transport, electric boats, and seaplanes. "
            "Utility model: **CN 202530610079.9**.\n"
            "• **Skylo** — a 2025 internal research framework for aerial logistics and the "
            "low-altitude economy, covering drones, eVTOLs, medical logistics, emergency response, "
            "infrastructure inspection, and remote-territory connectivity."
        ),
        (
            "**Note on Skylo:** it is part of 1PAX's innovation portfolio, but it is not presented "
            "as a registered patent in the public materials. It is a strategic research platform "
            "for the low-altitude economy."
        ),
        (
            "These patents are part of 1PAX's broader innovation work: developing proprietary systems "
            "that improve passenger experience, reduce operational clutter, support scalable deployment, "
            "and create long-term intellectual property value for mobility infrastructure."
        ),
    ],

    "pax_cart": [
        (
            "**PAX — Passenger Assisted Experience**\n\n"
            "PAX is 1PAX's patented all-in-one airport mobility product. "
            "Conceived from a passenger-centered perspective, it integrates **seat, cart, stroller, "
            "and stacking system** into a single elegant object — solving the clutter, inefficiency, "
            "and operational complexity of traditional multi-equipment solutions.\n\n"
            "*Patent: EU 4096986B1 · CN 202530430900.9*"
        ),
        (
            "**Four configurations. One gesture.**\n\n"
            "• **Seat** — resting points anywhere in the terminal\n"
            "• **Cart** — transport of hand luggage or shopping\n"
            "• **Stroller** — safe transport of children or small pets\n"
            "• **Stack/Nest** — compact storage, minimal footprint\n\n"
            "PAX serves families with children, elderly passengers, people with reduced mobility, "
            "business travellers, and leisure travellers — making the terminal more inclusive and comfortable."
        ),
        (
            "**Smart infrastructure integration:**\n\n"
            "• Wireless charging capability\n"
            "• QR-based connectivity and app integration\n"
            "• Optional geolocation and usage data analytics\n"
            "• BIM-compatible design\n"
            "• Future-ready energy and data interfaces\n\n"
            "For **operators**, this means valuable operational insights, optimised fleet management, "
            "and new revenue streams. For **passengers**, a seamless and intuitive experience throughout the terminal."
        ),
        (
            "**Commercial models:**\n\n"
            "PAX is designed for B2B deployment across airports, stations, cruise terminals, and mobility hubs. "
            "Deployment models include concession-based operation, rental or premium passenger services, "
            "branding and customisation, and data-enabled service management.\n\n"
            "The product is backed by a comprehensive patent portfolio — EU 4096986B1 and CN 202530430900.9 — "
            "ensuring clear market differentiation and high barriers to entry.\n\n"
            "Ask about **Ecoport** for 1PAX's modular vertiport system, or **innovation services** for licensing."
        ),
    ],

    "ecoport": [
        (
            "**Ecoport — The Modular Vertiport for Future-Ready Mobility**\n\n"
            "Ecoport is 1PAX's patented modular vertiport system — compact, scalable, and sustainable. "
            "Unlike site-specific proposals that slow deployment and limit scalability, Ecoport is a "
            "robust, phased solution ready to adapt to real geographies, real regulations, and real demand growth.\n\n"
            "*Patent: CN 202530610079.9*"
        ),
        (
            "**Modular growth, phase by phase — built on a 30 × 30 m grid:**\n\n"
            "• **Phase 00** — Compact vertiport base for drone logistics and light eVTOL operations\n"
            "• **Phase 01** — Expanded single-level eVTOL terminal\n"
            "• **Phase 02** — Integration with regional aircraft or multimodal ground transport\n"
            "• **Phase 03–04** — Vertical expansion with independent circulation cores and increased gate capacity\n\n"
            "Each phase builds on the previous, ensuring continuity of operations and long-term flexibility."
        ),
        (
            "**Multimodal by design:**\n\n"
            "Ecoport integrates air, land, and water mobility in a single coherent hub — eVTOL, helicopters, "
            "general aviation, electric buses, electric boats, and seaplanes.\n\n"
            "Passenger flow is engineered to IATA, ADRM, and ICAO standards: clear separation of "
            "arrivals/departures/transfers, reduced walking distances, decentralised boarding by level, "
            "and intuitive wayfinding.\n\n"
            "**Adaptable to any geography:** dense urban contexts, coastal locations, remote territories, "
            "islands, forests, deserts, tropical, and cold climates."
        ),
        (
            "**Sustainability at the core:**\n\n"
            "• Reduced footprint — compact vertical design\n"
            "• Prefabrication and modular construction\n"
            "• Optimised energy use and electric/low-emission transport integration\n"
            "• Biodiversity-aware site strategies\n\n"
            "Ecoport aligns with ESG goals, decarbonisation targets, and future mobility regulations — "
            "making it suitable for both infrastructure investors and operators seeking a proven, "
            "deployable vertiport solution.\n\n"
            "Ask about **PAX** for 1PAX's all-in-one airport mobility product, or **future mobility services** for vertiport design."
        ),
    ],

    "skylo": [
        (
            "**SKYLO — Aerial Logistics Infrastructure for the Next Mobility Era**\n\n"
            "SKYLO is 1PAX's strategic research and design framework for the **low-altitude economy**. "
            "It explores how drones and eVTOL aircraft can move beyond isolated pilot projects and "
            "become scalable territorial infrastructure for public value.\n\n"
            "The framework connects **cities, peri-urban zones, and rural landscapes** through a unified "
            "network for medical logistics, emergency response, infrastructure inspection, environmental "
            "operations, agriculture, tourism, and sustainable mobility."
        ),
        (
            "**What problem does SKYLO solve?**\n\n"
            "Ground logistics is reaching its limits: congestion delays medical transport, blocked roads "
            "slow emergency response, infrastructure inspections expose workers to risk, and remote "
            "communities can be cut off from essential services.\n\n"
            "SKYLO treats low-altitude airspace as a distributed logistics layer above conventional "
            "transport networks, using drones and eVTOL aircraft where the fastest and most resilient "
            "route is through the air."
        ),
        (
            "**Core applications:**\n\n"
            "• **Medical logistics** — organ transport, blood delivery, medicine delivery, and emergency supplies\n"
            "• **Infrastructure monitoring** — high-rise buildings, power lines, tunnels, and underground networks\n"
            "• **Disaster response** — flood mapping, wildfire detection, search and rescue, and rapid supply delivery\n"
            "• **Environmental and agricultural operations** — crop monitoring, precision seeding, wildlife, and tourism management"
        ),
        (
            "**How SKYLO is evaluated:**\n\n"
            "The toolkit measures coverage, response speed, operational efficiency, cost efficiency, "
            "and safety. It combines vision, technical analysis, regulation, environmental and spatial "
            "constraints, social impact, and international case studies from Europe and China.\n\n"
            "The initial concept focuses on France, with expansion scenarios for extreme geographies "
            "such as the Amazon Basin and Patagonian Fjords, where low-carbon aerial logistics can "
            "compress journeys from days to hours."
        ),
        (
            "SKYLO invites collaboration with cities and regional governments, healthcare institutions, "
            "mobility innovators, logistics operators, and research institutions.\n\n"
            "Ask about **Ecoport** for 1PAX's modular vertiport infrastructure, or **PAX Cart** for the "
            "passenger mobility product."
        ),
    ],

    # ── Follow-up prompt pool ─────────────────────────────────────────────────

    "follow_up": [
        (
            "Want to know more? I can tell you about our **design approach**, **mission**, "
            "**offices**, **founder**, **expertise**, **careers**, or what makes us **different**."
        ),
        (
            "Happy to go deeper — ask me about our **team**, **values**, **innovation**, "
            "**sustainability commitment**, or **how to join us**."
        ),
        (
            "There's plenty more to explore — our **design philosophy**, **global operations**, "
            "**what we specialize in**, or **who founded 1PAX**. Just ask."
        ),
        (
            "You can also ask about our **ethical pillars**, **diversity commitment**, "
            "**governance**, or our **2026–2028 sustainability plan**."
        ),
    ],
}
