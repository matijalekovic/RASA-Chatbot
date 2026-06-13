"""
Project data registry for 1PAX chatbot.

To add a new project:
  1. Add a new entry to PROJECTS below (copy the sofia_airport block as a template).
  2. Add NLU synonym entries in data/nlu.yml under the `- synonym: <project_key>` block.
  3. Run `rasa train`.
  No other files need to change.
"""

PROJECTS = {
    "sofia_airport": {
        "display_name": "Sofia Airport – Terminal 3 International & Terminal 2 Refurbishment",
        "category": "Airports and Transportation",
        "location": "Sofia, Bulgaria",
        "year": "2023–2026",
        "client": "SOF Connect",
        "architect": "1PAX + IPA EOOD",
        "partners": "EGIS AVIA",
        "area": "110,000 m²",
        "capacity": "15 million passengers annually",
        "cost": "200 million €",
        "video_url": "https://vimeo.com/1166384100/d890adfee8?share=copy&fl=sv&fe=ci",
        "tagline": (
            "A centralized terminal vision designed to elevate passenger experience "
            "and position Sofia Airport as a 5-Star regional hub."
        ),
        "overview": (
            "From 2023 to 2026, 1PAX, in association with IPA EOOD and EGIS AVIA, led "
            "the architectural design for the expansion and reorganization of Sofia Airport. "
            "Commissioned by SOF Connect, the project combines the refurbishment of Terminal 2 "
            "with the development of a new international Terminal 3, delivering a unified airport "
            "system of approximately 110,000 m² designed to accommodate up to 15 million "
            "passengers annually."
        ),
        "key_challenge": (
            "Sofia Airport's ambition to achieve a 5-Star Label required a fundamental rethinking "
            "of passenger processing, spatial organization, and service quality. The challenge was "
            "to centralize and streamline flows across existing and new terminals, significantly "
            "upgrade international processing facilities, and integrate a high-quality commercial "
            "and hospitality offer — while maintaining operational continuity and meeting "
            "stringent sustainability objectives."
        ),
        "approach": (
            "1PAX developed a fully centralized terminal concept, placing passenger clarity and "
            "comfort at the core of the design strategy. The new Terminal 3 is conceived as a "
            "dedicated international terminal with its own pier, while Terminal 2 is refurbished "
            "and reorganized to integrate seamlessly into the overall system. The project "
            "introduces entirely new baggage reclaim areas, upgraded security checkpoints, and "
            "modernized immigration and emigration facilities to improve passenger flow and "
            "service quality throughout the airport."
        ),
        "five_star_detail": (
            "The 5-Star Airport Label (based on Skytrax standards) is awarded to airports that "
            "deliver the highest benchmarks in passenger experience, terminal facilities, staff "
            "service quality, and cleanliness across all touchpoints. For Sofia Airport, achieving "
            "this ambition meant fundamentally redesigning passenger flows to eliminate congestion, "
            "introducing premium retail and F&B zones, and upgrading every processing touchpoint — "
            "from check-in and security through immigration and emigration. 1PAX's centralized "
            "terminal concept directly addresses each 5-Star criterion by ensuring clarity, "
            "comfort, and seamless movement for every passenger."
        ),
        "sustainability": (
            "Sustainability was a core objective throughout the Sofia Airport project. The design "
            "strategy prioritized operational continuity during construction to minimize disruption, "
            "while the unified terminal system reduces energy consumption through centralized "
            "infrastructure. The project meets stringent environmental objectives set by SOF "
            "Connect, integrating sustainable materials, efficient building systems, and "
            "future-ready infrastructure into both the refurbished Terminal 2 and the new "
            "Terminal 3."
        ),
        "status": "Under construction — expected completion 2026",
        "tender_result": "Direct commission by SOF Connect",
        "scope": "Architectural design — new Terminal 3 (international) + Terminal 2 refurbishment, total 110,000 m²",
        "program": (
            "• New Terminal 3 — dedicated international terminal with its own pier\n"
            "• Terminal 2 refurbishment and full reorganization\n"
            "• New centralized baggage reclaim areas\n"
            "• Upgraded security checkpoints and immigration/emigration facilities\n"
            "• Premium retail and F&B zones targeting 5-Star Skytrax standards"
        ),
        "fun_facts": (
            "• Sofia Airport aims to become a 5-Star Skytrax-rated airport — one of fewer than 20 in the world.\n"
            "• The project unifies two separate terminals into one centralized system covering 110,000 m².\n"
            "• 1PAX worked with IPA EOOD and EGIS AVIA on this landmark Bulgarian aviation project."
        ),
    },

    "belgrade_airport": {
        "display_name": "Belgrade Airport – Phase 1 & Phase 2 Terminal Expansion",
        "category": "Airports and Transportation",
        "location": "Belgrade, Serbia",
        "year": "2021–2025 / ongoing",
        "client": "Belgrade Airport (Vinci Airports concession)",
        "architect": "1PAX, Energoprojekt",
        "partners": "TG Concept, Egis, Systra",
        "area": "47,000 m² new + 50,000 m² refurbishment",
        "capacity": "12 million passengers annually",
        "cost": "700 million € total (200 million € terminal)",
        "video_url": "https://vimeo.com/1166383100/8327a1a2ca?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Delivering a phased transformation of Serbia's main gateway through "
            "modern design, clarity and efficiency."
        ),
        "overview": (
            "1PAX was commissioned by Belgrade Airport, under the Vinci Airports concession, "
            "to design the architecture for the two main phases of the airport's terminal "
            "expansion. Working in collaboration with Energoprojekt and partners TG Concept, "
            "Egis, and Systra, the project encompasses the construction of approximately 47,000 "
            "m² of new facilities and the refurbishment of an additional 50,000 m² of existing "
            "terminal space. "
            "The project provides Belgrade Airport with a robust, future-ready terminal "
            "environment capable of supporting sustained traffic growth and evolving operational "
            "requirements. Through careful phasing, architectural coherence, and integration of "
            "support infrastructure, 1PAX's work enhances passenger experience, operational "
            "efficiency, and overall airport resilience. The ongoing collaboration underscores "
            "the strategic role of architecture as a long-term partner in the airport's "
            "transformation."
        ),
        "key_challenge": (
            "The airport required a major capacity and service upgrade while maintaining full "
            "operations throughout construction. The challenge was to phase the expansion "
            "strategically, ensuring continuity of passenger processing, improving spatial "
            "legibility, and integrating new infrastructure seamlessly with existing terminal "
            "buildings—all while meeting evolving security, safety, and operational standards."
        ),
        "approach": (
            "1PAX developed a clear, phased architectural strategy. "
            "Phase 1 focuses on immediate capacity and flow improvements, including the addition "
            "of an arrivals gallery on the roof of the existing terminal, the construction of a "
            "new boarding pier with three MARS contact stands, and an interior refurbishment "
            "introducing a new centralized security screening area to streamline passenger "
            "processing. "
            "Phase 2 delivers a substantial expansion of core processing areas, extending "
            "check-in halls, security screening zones, duty-free areas, and baggage delivery "
            "facilities to support long-term growth and improved passenger comfort. "
            "Beyond the terminal itself, 1PAX was also responsible for the architectural design "
            "of several key support facilities, including the new main firefighting station, the "
            "NTA administration building, and dedicated maintenance workshops. Since the "
            "completion of the main design phases, 1PAX continues to assist Belgrade Airport "
            "through a framework contract, supporting updates to passenger processing systems "
            "on behalf of the Grantor."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The phased construction strategy was a core sustainability measure, preserving "
            "operational continuity and avoiding full airport shutdowns during construction. "
            "The design integrates modern building systems and energy-efficient infrastructure "
            "across both the new 47,000 m² terminal wing and the refurbished 50,000 m² of "
            "existing space, supporting long-term operational efficiency and environmental "
            "performance in line with Vinci Airports' concession standards."
        ),
        "status": "Under construction — ongoing (2021–2025+)",
        "tender_result": "Direct commission under Vinci Airports concession framework",
        "scope": "Architectural design for phased terminal expansion — 47,000 m² new build + 50,000 m² refurbishment, plus support facilities",
        "program": (
            "• New arrivals gallery on roof of existing terminal (Phase 1)\n"
            "• New boarding pier with three MARS contact stands (Phase 1)\n"
            "• New centralized security screening area (Phase 1)\n"
            "• Extended check-in halls, duty-free, and baggage delivery (Phase 2)\n"
            "• New main firefighting station, NTA administration building, maintenance workshops\n"
            "• Ongoing framework contract support for passenger processing systems"
        ),
        "fun_facts": (
            "• The total investment across the Belgrade Airport program reaches 700 million €, making it one of Serbia's largest infrastructure projects.\n"
            "• 1PAX's scope extended beyond the terminal to include the fire station, admin building, and maintenance facilities — a full campus approach.\n"
            "• The project is delivered under the Vinci Airports concession, Serbia's first major private airport operation."
        ),
    },

    "velana_airport": {
        "display_name": "Velana International Airport – New Terminal Building",
        "category": "Airports and Transportation",
        "location": "Malé, Maldives",
        "year": "2016–2025 (inaugurated July 2025)",
        "client": "Maldives Airport Company Limited (MACL), Saudi Binladin Group",
        "architect": "1PAX",
        "partners": "SETEC (engineers), SBG-CHEC (contractor)",
        "area": "102,000 m²",
        "capacity": "7.3 million passengers (Phase 1) – 9.5 million passengers (Phase 2)",
        "cost": "850 million €",
        "video_url": "https://vimeo.com/1166382926/62ecfd5a55?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Designing a world-class island gateway that redefines arrival through "
            "seamless connectivity, clarity, and place-making."
        ),
        "overview": (
            "Developed between 2016 and 2025 and inaugurated in July 2025, the New Terminal "
            "Building at Velana International Airport represents a major national infrastructure "
            "investment for the Maldives. Commissioned by Maldives Airport Company Limited "
            "(MACL), with Saudi Binladin Group appointed as contractor and SETEC as lead "
            "engineer, 1PAX was selected to deliver the architectural and interior design of "
            "the new international terminal. With a total area of 102,000 m², the terminal is "
            "designed to accommodate 7.3 million passengers in Phase 1 and up to 9.5 million "
            "passengers in Phase 2. "
            "The new terminal delivers a transformative upgrade to the Maldives' primary "
            "international gateway. By combining robust operational performance with a refined "
            "passenger experience and seamless intermodal connectivity, the project strengthens "
            "the country's tourism infrastructure and international accessibility. The terminal "
            "establishes a clear, memorable sense of arrival—positioning Velana International "
            "Airport as a resilient, future-ready hub that reflects both the aspirations of the "
            "nation and the expectations of global travelers."
        ),
        "key_challenge": (
            "The airport required a new terminal capable of responding to rapid traffic growth "
            "while addressing the unique logistical and experiential conditions of an island "
            "nation. A critical challenge was the creation of a clear and efficient connectivity "
            "zone linking the terminal with the seaplane terminal, jetty piers, and landside "
            "resort transfers—an essential interface for a country where air–sea intermodality "
            "defines the travel experience. At the same time, the terminal needed to deliver a "
            "strong first impression aligned with the Maldives' global tourism identity."
        ),
        "approach": (
            "1PAX developed an architectural concept centered on clarity of movement, spatial "
            "generosity, and intuitive wayfinding. A key design component is the resort plaza, "
            "conceived as a contemporary arrival and distribution space that connects the "
            "terminal seamlessly to seaplane operations, marine transport, and onward resort "
            "destinations. This plaza acts as both an infrastructural hub and a symbolic "
            "threshold, welcoming travelers with a sense of openness and calm. "
            "The project was fully developed in Building Information Modeling (BIM), involving "
            "a multidisciplinary team of over 30 architects and engineers. This approach ensured "
            "precise coordination across architecture, structure, systems, and construction "
            "sequencing. The design was approved by MACL in August 2017, enabling construction "
            "to proceed within a highly complex logistical environment."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The BIM-driven design process enabled precision coordination and waste reduction "
            "across architecture, structure, and MEP systems. The terminal's spatial strategy "
            "prioritizes natural light and spatial openness, reducing reliance on artificial "
            "lighting. The resort plaza concept promotes intermodal connectivity, reducing "
            "unnecessary vehicle journeys and supporting a lower-carbon arrival experience "
            "consistent with the Maldives' commitment to sustainable tourism."
        ),
        "status": "Built — inaugurated July 2025",
        "tender_result": "Direct commission by Maldives Airport Company Limited (MACL)",
        "scope": "Architectural and interior design — new international terminal, 102,000 m², developed entirely in BIM",
        "program": (
            "• New international passenger terminal — 102,000 m²\n"
            "• Resort plaza — intermodal hub connecting terminal to seaplane operations and marine transport\n"
            "• Jetty piers and landside resort transfer interfaces\n"
            "• Full interior design across all passenger-facing zones\n"
            "• BIM coordination across a 30+ person multidisciplinary team"
        ),
        "fun_facts": (
            "• The Velana terminal project took nearly a decade from design approval (2017) to inauguration (July 2025).\n"
            "• With 102,000 m², it is one of the largest airport projects ever delivered by 1PAX.\n"
            "• The resort plaza is a unique typology — a terminal zone designed specifically for the Maldives' air-to-sea transfer model, reflecting an island nation where arriving at an airport is only the beginning of the journey."
        ),
    },

    "bordeaux_airport": {
        "display_name": "Bordeaux–Mérignac Airport – Hall B New Façades",
        "category": "Airports and Transportation",
        "location": "Mérignac, France",
        "year": "2023 (built)",
        "client": "Aéroport de Bordeaux Mérignac",
        "architect": "1PAX, KAIRN",
        "partners": "Coveris (contractor)",
        "area": "1,800 m² façade",
        "capacity": "N/A",
        "cost": "5 million €",
        "video_url": "https://vimeo.com/1166381816/2b86e30951?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Reinstating transparency and architectural integrity through a technically "
            "refined façade reconstruction."
        ),
        "overview": (
            "Completed in 2023, this project involved the demolition and reconstruction of the "
            "façades of Hall B at Bordeaux–Mérignac Airport, originally designed in the 1990s "
            "by architect Paul Andreu. Commissioned by Aéroport de Bordeaux Mérignac, the "
            "intervention was led by 1PAX in collaboration with KAIRN, with Coveris as "
            "contractor. The scope covered approximately 1,800 m² of façade and addressed the "
            "need to restore both structural reliability and architectural intent within an "
            "active terminal environment. "
            "The reconstructed façades restore Hall B's iconic transparency and architectural "
            "clarity while significantly improving structural reliability and longevity. Through "
            "a sensitive balance of heritage respect, technical innovation, and operational "
            "coordination, the project delivers a renewed terminal envelope that meets "
            "contemporary standards without compromising its original identity. The result "
            "reinforces Bordeaux–Mérignac Airport's architectural legacy while ensuring "
            "resilience and performance for decades to come."
        ),
        "key_challenge": (
            "The original glass façade system, characterized by large transparent panels held "
            "by structural stiffeners, had suffered damage over time, making full replacement "
            "unavoidable. The challenge was to reconstruct the façade while preserving the "
            "original concept of transparency and lightness, managing complex technical "
            "constraints—including experimental validation (ATEX)—and maintaining uninterrupted "
            "terminal operations throughout construction."
        ),
        "approach": (
            "1PAX developed a façade strategy that carefully respected Paul Andreu's original "
            "architectural vision. New steel stiffeners were designed and encased in polished "
            "stainless-steel cladding, maintaining visual continuity while enhancing durability "
            "and performance. The technical complexity of the façade system required rigorous "
            "testing and validation, ensuring compliance with safety and performance standards. "
            "Construction phasing was meticulously coordinated to allow the terminal to remain "
            "operational, minimizing disruption to passengers and airport activities while "
            "ensuring precise execution of the new envelope."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The project's approach to sustainability centered on adaptive reuse and material "
            "performance rather than demolition and full replacement. By retaining the existing "
            "terminal structure and reconstructing only the damaged façade envelope, the "
            "intervention minimized waste and embodied carbon. The new polished stainless-steel "
            "cladding system is designed for long-term durability, reducing future maintenance "
            "cycles and extending the building's service life for decades to come."
        ),
        "status": "Built — completed 2023",
        "tender_result": "Direct commission by Aéroport de Bordeaux Mérignac",
        "scope": "Façade reconstruction — demolition and replacement of 1,800 m² historic glass façade designed by Paul Andreu",
        "program": (
            "• Demolition of original 1990s glass façade system (1,800 m²)\n"
            "• New steel stiffeners encased in polished stainless-steel cladding\n"
            "• ATEX experimental validation of new façade system\n"
            "• Phased construction to maintain full terminal operations throughout"
        ),
        "fun_facts": (
            "• Hall B was originally designed by Paul Andreu — one of France's most celebrated airport architects, known for CDG Terminal 1.\n"
            "• The new façade required ATEX (explosive atmosphere) certification testing — an unusually rigorous validation process for a glass building skin.\n"
            "• Despite covering 1,800 m², the project was delivered at a cost of just 5 million €, demonstrating highly efficient façade engineering."
        ),
    },

    "cayenne_terminal": {
        "display_name": "Félix Eboué Cayenne Airport – New Terminal",
        "category": "Airports and Transportation",
        "location": "French Guiana",
        "year": "2023",
        "client": "EDEIS COLAS",
        "architect": "1PAX",
        "partners": "Ingerop",
        "area": "25,000 m²",
        "capacity": "N/A",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Expanding a tropical gateway through a sustainable, service-oriented "
            "terminal strategy."
        ),
        "overview": (
            "In 2023, 1PAX was commissioned by EDEIS COLAS, in collaboration with Ingerop, "
            "to design the expansion and transformation of Félix Eboué Cayenne Airport's "
            "passenger terminal. The project responds to the airport's ambition to raise service "
            "quality and significantly enhance the overall user experience, while reinforcing "
            "the terminal's capacity and functional diversity within a rapidly evolving regional "
            "context. "
            "The project delivers a resilient, future-ready terminal that significantly elevates "
            "passenger experience while diversifying airport services. By combining functional "
            "expansion with a strong sustainable vision, the new terminal supports operational "
            "efficiency, environmental responsibility, and long-term adaptability. The result "
            "strengthens Félix Eboué Cayenne Airport's role as a modern, climate-responsive "
            "gateway for French Guiana, aligned with international standards and local realities."
        ),
        "key_challenge": (
            "The main challenge was to expand the terminal's capacity and services without "
            "compromising operational continuity, while ensuring the project remained fully "
            "adapted to the climatic, environmental, and urban conditions of French Guiana. "
            "The intervention needed to improve passenger comfort, integrate new public and "
            "support functions, and embed sustainability as a core design driver rather than "
            "a technical add-on."
        ),
        "approach": (
            "1PAX developed a comprehensive architectural proposal combining targeted expansion "
            "of the existing terminal with the creation of new complementary facilities. The "
            "project includes the extension of more than 2,000 m² of the current "
            "building—encompassing the main hall, boarding lounges, and border control "
            "areas—to improve capacity, flow, and comfort. "
            "In parallel, a new 3,000 m² covered area was designed to consolidate key passenger "
            "and airport services, including a health center, food court, car rental facilities, "
            "parking interfaces, airport support spaces, and offices. The architectural and "
            "spatial organization prioritizes clarity, accessibility, and intuitive movement, "
            "reinforcing the terminal as a coherent and welcoming gateway."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability was embedded throughout the design as a core objective rather than "
            "a technical add-on. The project integrates solar panels on the terminal roof, "
            "natural ventilation strategies tailored to the tropical climate of French Guiana, "
            "rainwater harvesting systems, and additional energy-efficiency measures. The design "
            "responds specifically to local climatic conditions—heat, humidity, and intense "
            "sunlight—ensuring long-term environmental responsibility and reduced operational "
            "energy consumption."
        ),
        "status": "Built — completed 2023",
        "tender_result": "Direct commission by EDEIS COLAS",
        "scope": "Architectural design for terminal extension and new covered facilities — 25,000 m² total",
        "program": (
            "• Extension of existing terminal: main hall, boarding lounges, border control (2,000+ m²)\n"
            "• New 3,000 m² covered area with health centre, food court, car rental, and airport support spaces\n"
            "• Solar panels on terminal roof\n"
            "• Natural ventilation systems tailored to tropical climate\n"
            "• Rainwater harvesting systems"
        ),
        "fun_facts": (
            "• Félix Eboué Cayenne Airport is the main gateway to French Guiana — France's territory on the northern coast of South America, home to the Guiana Space Centre (CNES).\n"
            "• The project integrates a health centre as a key facility — reflecting the airport's role in a remote territory where medical transit is critical.\n"
            "• Solar panels, natural ventilation, and rainwater harvesting were all embedded as core design features, not afterthoughts — setting a benchmark for tropical airport sustainability."
        ),
    },

    "nice_airport": {
        "display_name": "Nice Côte d'Azur Airport – Terminal Boarding Gates Expansion",
        "category": "Airports and Transportation",
        "location": "Nice, France",
        "year": "2017–2020",
        "client": "Aéroport de la Côte d'Azur",
        "architect": "1PAX",
        "partners": "SETEC",
        "area": "1,100 m²",
        "capacity": "5 million passengers annually",
        "cost": "15 million €",
        "video_url": "",
        "tagline": (
            "Expanding gate capacity through a carefully phased intervention integrated "
            "seamlessly into an active terminal."
        ),
        "overview": (
            "Between 2017 and 2020, 1PAX was commissioned by Aéroport de la Côte d'Azur to "
            "design the expansion of boarding gate facilities at Terminal 1 of Nice Côte d'Azur "
            "Airport. Developed in collaboration with SETEC, the project addressed the extension "
            "of the terminal through the creation of a new boarding lounge and two additional "
            "contact stands, supporting an airport handling up to 5 million passengers. The "
            "intervention formed part of a broader effort to modernize aircraft interfaces and "
            "improve operational efficiency. "
            "The project delivered a significant increase in boarding capacity and operational "
            "efficiency without compromising passenger experience during construction. Through "
            "phased implementation and a restrained architectural approach, the expansion "
            "reinforces Terminal 1's long-term performance and adaptability. The result is a "
            "robust, well-integrated upgrade that supports Nice Côte d'Azur Airport's role as "
            "a major international gateway on the Mediterranean."
        ),
        "key_challenge": (
            "The principal challenge was to increase boarding capacity and upgrade aircraft "
            "stands while maintaining full terminal operations throughout construction. The "
            "airport's high traffic levels required a phased delivery strategy that preserved "
            "passenger capacity and service quality over a prolonged construction period, all "
            "within the spatial and operational constraints of an existing terminal."
        ),
        "approach": (
            "1PAX developed an architectural solution focused on continuity and integration. "
            "The extension includes a new boarding lounge and two contact stands, alongside the "
            "redesign of all aircraft stands and the replacement of passenger boarding bridges. "
            "To minimize disruption, the works were carefully staged over a five-year "
            "timeframe, allowing the terminal to remain fully operational at each phase. "
            "Architecturally, the new elements were designed to blend smoothly with the existing "
            "terminal, respecting its scale, materiality, and spatial logic, while discreetly "
            "upgrading performance and functionality."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The project's phased construction strategy was key to its sustainability approach: "
            "by staging works over five years, the terminal remained operational throughout, "
            "avoiding closures and the associated waste of large-scale demolition. The new "
            "boarding bridges and contact stands were designed for long-term durability and "
            "compatibility with future aircraft types, supporting the airport's operational "
            "resilience and reducing the need for near-term replacement."
        ),
        "status": "Built — completed 2020",
        "tender_result": "Direct commission by Aéroport de la Côte d'Azur",
        "scope": "Architectural design for boarding gate expansion and aircraft stand upgrade at Terminal 1",
        "program": (
            "• New boarding lounge serving two additional contact stands\n"
            "• Redesign and upgrade of all aircraft stands\n"
            "• Replacement of passenger boarding bridges\n"
            "• Phased delivery over five-year construction period to maintain full operations"
        ),
        "fun_facts": (
            "• Nice Côte d'Azur Airport is one of France's busiest airports, handling millions of passengers on the French Riviera.\n"
            "• The project was carefully phased over five years — one of 1PAX's longest active construction timelines for a single gate expansion.\n"
            "• The intervention at Terminal 1 increased capacity while ensuring zero closures, a logistical achievement in a high-traffic Mediterranean hub."
        ),
    },

    "pointe_a_pitre_t1": {
        "display_name": "Pointe-à-Pitre International Airport – New Terminal Extension (Winner)",
        "category": "Airports and Transportation",
        "location": "Pointe-à-Pitre, Guadeloupe",
        "year": "2019–2027",
        "client": "Aéroport de Guadeloupe Pôle Caraïbes",
        "architect": "ENIA, 1PAX, BM",
        "partners": "GUEZ, SETEC",
        "area": "23,600 m²",
        "capacity": "3 million passengers annually",
        "cost": "103 million €",
        "video_url": "https://vimeo.com/1166382459/3caa308f73?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Transforming the airport's main terminal into a resilient, sustainable, and "
            "future-ready Caribbean gateway."
        ),
        "overview": (
            "Awarded through an international competition, the expansion of Terminal 1 at "
            "Pointe-à-Pitre International Airport represents a major long-term transformation "
            "of Guadeloupe's primary aviation hub. Led by a multidisciplinary team including "
            "ENIA, 1PAX, and BM, with GUEZ and SETEC as partners, the project is being "
            "developed between 2019 and 2027 for Aéroport de Guadeloupe Pôle Caraïbes. "
            "Covering 23,600 m², the extension supports an airport capacity of 3 million "
            "passengers annually and forms a cornerstone of the airport's modernization strategy. "
            "The Terminal 1 extension delivers a profound upgrade to Pointe-à-Pitre "
            "International Airport's capacity, functionality, and passenger experience. By "
            "combining operational efficiency, architectural clarity, and environmental "
            "responsibility, the project strengthens the airport's role as a modern Caribbean "
            "gateway. The winning competition proposal provides a robust, future-oriented "
            "framework that supports sustainable growth, improves service quality, and "
            "reinforces the airport's resilience for decades to come."
        ),
        "key_challenge": (
            "The existing terminal infrastructure required a comprehensive upgrade to meet "
            "evolving security standards, growing passenger volumes, and higher expectations in "
            "terms of comfort and efficiency. The challenge was to reorganize core processing "
            "functions—check-in, security, border control, boarding, and arrivals—while "
            "maintaining continuous airport operations and embedding strong sustainability "
            "commitments within a complex tropical context."
        ),
        "approach": (
            "The project introduces a new processing area integrating enhanced security "
            "screening, immigration and emigration facilities, and an expanded duty-free zone. "
            "New boarding lounges are designed to accommodate two Code E aircraft at contact "
            "stands, significantly improving operational capacity and passenger comfort. A "
            "modern baggage reclaim hall is added, alongside a complete reconfiguration of the "
            "existing check-in area and baggage handling system to streamline flows and improve "
            "reliability. "
            "Sustainability is embedded at every level of the design. The curbside and gate "
            "areas are fully redesigned to improve landside efficiency and passenger clarity, "
            "while photovoltaic panels installed on the terminal roof harness solar energy. "
            "Environmental monitoring and mitigation measures are incorporated to reduce the "
            "airport's footprint and align the project with long-term sustainability objectives."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability is embedded at every level of the Terminal 1 extension design. "
            "Photovoltaic panels installed on the terminal roof harness solar energy to offset "
            "operational energy demand. Environmental monitoring and mitigation measures are "
            "incorporated throughout to reduce the airport's carbon footprint. The curbside "
            "and gate area redesign improves landside efficiency and reduces vehicle idle times, "
            "while the new building systems and envelope are aligned with long-term "
            "sustainability objectives in this tropical island context."
        ),
        "status": "Under construction (2019–2027)",
        "tender_result": "Winner of international competition",
        "scope": "Architectural design for 23,600 m² terminal extension including security, immigration, boarding, baggage, and curbside redesign",
        "program": (
            "• New security screening and immigration/emigration facilities\n"
            "• Expanded duty-free zone\n"
            "• New boarding lounges for two Code E aircraft at contact stands\n"
            "• Modern baggage reclaim hall\n"
            "• Full reconfiguration of check-in area and baggage handling system\n"
            "• Curbside and gate area redesign\n"
            "• Photovoltaic panels on terminal roof"
        ),
        "fun_facts": (
            "• Pointe-à-Pitre International Airport is the main gateway to Guadeloupe — a French Caribbean island territory with a strong tourism and transit economy.\n"
            "• The project was won through an international design competition, with ENIA, 1PAX, and BM forming the winning team.\n"
            "• At 103 million € and 2019–2027 delivery, this is one of the most substantial airport transformation programs in the French Caribbean."
        ),
    },

    "pointe_a_pitre_t2": {
        "display_name": "Pointe-à-Pitre International Airport – Terminal 2 Extension",
        "category": "Airports and Transportation",
        "location": "Pointe-à-Pitre, Guadeloupe",
        "year": "2023–2025",
        "client": "SAGPC",
        "architect": "1PAX",
        "partners": "Systra, Colorado Architecture",
        "area": "900 m²",
        "capacity": "3 million passengers annually (airport total)",
        "cost": "6 million €",
        "video_url": "",
        "tagline": (
            "Expanding departure capacity to improve passenger comfort, flow efficiency, "
            "and operational resilience."
        ),
        "overview": (
            "Between 2023 and 2025, 1PAX was commissioned by SAGPC to design the extension of "
            "the departure lounge at Terminal 2 of Pointe-à-Pitre International Airport, in "
            "collaboration with SYSTRA and Colorado Architecture. The project forms part of the "
            "broader Projet du Centre, a strategic initiative aimed at reinforcing the airport's "
            "capacity and improving the overall balance between terminal facilities. Serving an "
            "airport with a capacity of approximately 3 million passengers per year, the "
            "intervention targets a critical interface within the departure process. "
            "The Terminal 2 extension significantly improves the airport's ability to manage "
            "growing passenger volumes while easing pressure on Terminal 1. By optimizing flows, "
            "increasing functional capacity, and upgrading passenger amenities, the project "
            "enhances both operational performance and the quality of the travel experience. "
            "The intervention strengthens Pointe-à-Pitre International Airport's overall "
            "resilience and positions it to better support future traffic growth within the "
            "Caribbean region."
        ),
        "key_challenge": (
            "The airport faced increasing congestion, particularly within Terminal 1, driven by "
            "growing traffic and complex transfer operations. The challenge was to expand "
            "Terminal 2 in a constrained environment while improving passenger flows, "
            "accommodating remote boarding for Code C and E aircraft, and ensuring a seamless "
            "integration with the existing terminal structure—all without disrupting ongoing "
            "operations."
        ),
        "approach": (
            "1PAX developed an architectural and functional solution focused on clarity, "
            "comfort, and operational efficiency. The project includes the construction of a "
            "new ramp, the addition of an extra floor on the southern section of Terminal 2, "
            "and the creation of new boarding facilities for remote stands. "
            "A central design principle was to streamline departure flows by redirecting "
            "passengers toward the core of the existing terminal, reinforcing legibility and "
            "reducing bottlenecks. Passenger comfort was prioritized through the design of "
            "generous waiting areas, modern sanitary facilities, enhanced services, and upgraded "
            "technical rooms, all integrated within a coherent and intuitive spatial layout."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Terminal 2 extension is designed to ease congestion at Terminal 1 and improve "
            "the balance of passenger flows across the airport, reducing peak-load inefficiencies "
            "and idle energy consumption. The new floor addition and ramp are integrated "
            "sustainably within the existing structure, minimizing new footprint while "
            "maximizing spatial efficiency. Modern technical systems are integrated throughout "
            "to improve long-term operational performance in the tropical climate of Guadeloupe."
        ),
        "status": "Built — completed 2025",
        "tender_result": "Direct commission by SAGPC",
        "scope": "Architectural design for 900 m² departure lounge extension at Terminal 2, including new floor and ramp",
        "program": (
            "• New ramp connecting terminal levels\n"
            "• Additional floor on the southern section of Terminal 2\n"
            "• New boarding facilities for remote Code C and E aircraft stands\n"
            "• Generous waiting areas and upgraded passenger amenities\n"
            "• Modern sanitary facilities and enhanced technical rooms"
        ),
        "fun_facts": (
            "• The Terminal 2 extension is part of the 'Projet du Centre' — a strategic initiative to rebalance passenger flows across the entire Pointe-à-Pitre airport campus.\n"
            "• Despite a modest 900 m² scope, the project significantly relieves pressure on Terminal 1 by rerouting passengers to a fully upgraded departure lounge.\n"
            "• At 6 million €, the project represents one of the most cost-efficient terminal capacity upgrades in the French Caribbean."
        ),
    },

    "annecy_airport": {
        "display_name": "Annecy Mont-Blanc General Aviation Terminal – Concession Competition (Winner)",
        "category": "Airports and Transportation",
        "location": "Annecy Mont-Blanc, France",
        "year": "2020",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "None listed",
        "area": "N/A",
        "capacity": "80,000 passengers annually",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Reinventing a general aviation terminal through environmental excellence, "
            "conviviality, and alpine-inspired comfort."
        ),
        "overview": (
            "In 2020, 1PAX supported Vinci Airports in the winning concession proposal for "
            "the Annecy Mont-Blanc General Aviation Terminal. Serving a limited but highly "
            "specific passenger profile, the project focused on the rehabilitation and "
            "enhancement of the existing terminal, positioning it as a high-quality, sustainable "
            "gateway aligned with the values of general aviation and the exceptional alpine "
            "context of Annecy. "
            "The project delivers a renewed general aviation terminal that combines environmental "
            "responsibility with a high-quality passenger experience. By achieving ambitious "
            "sustainability goals while enhancing comfort, conviviality, and architectural "
            "identity, the proposal positions Annecy Mont-Blanc Airport as a benchmark for "
            "small-scale, eco-conscious aviation facilities. The winning concession outcome "
            "confirms the strength of a design approach rooted in sustainability, place, and "
            "user well-being."
        ),
        "key_challenge": (
            "The challenge was to significantly improve environmental performance, spatial "
            "quality, and user experience within an existing structure, while achieving a High "
            "Environmental Quality certification (Label HQE). The project needed to balance "
            "energy efficiency, comfort, and operational clarity, while reinforcing the "
            "terminal's role as a welcoming and convivial place for passengers and visitors."
        ),
        "approach": (
            "1PAX developed a comprehensive refit strategy centered on sustainability, comfort, "
            "and spatial clarity. The proposal enhanced façades, interiors, and surrounding "
            "outdoor areas, introducing landscaped gardens, waiting zones, and improved shared "
            "spaces. The terrace bar was rehabilitated as a key social element, extending the "
            "passenger experience outdoors and encouraging interaction. "
            "Internally, circulation was reorganized around a strengthened Main Hall, improving "
            "legibility and flow while optimizing energy performance. The design emphasized "
            "contemporary and eco-friendly solutions, with careful attention to materials, "
            "acoustics, lighting, and cleanliness. Lounges were conceived with a "
            "Switzerland-inspired aesthetic, combining wooden and glazed façades with carpeted "
            "areas to create a warm, refined atmosphere. Bio-sourced materials and integrated "
            "vegetation further reinforced the project's sustainable and human-centered ethos."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability is the defining principle of this project. The terminal achieves "
            "High Environmental Quality certification (Label HQE), reflecting best-in-class "
            "energy efficiency, indoor environmental quality, and lifecycle performance. "
            "Bio-sourced materials, integrated vegetation, and passive environmental strategies "
            "are embedded throughout the design. The use of wooden and glazed façades, carpeted "
            "areas, and landscaped outdoor spaces creates a low-impact, thermally comfortable "
            "environment tailored to the alpine context of Annecy."
        ),
        "status": "Concession support — design proposal delivered 2020",
        "tender_result": "Concession support — won (2020), supporting Vinci Airports' successful bid",
        "scope": "Architectural design support for concession proposal — terminal refurbishment, HQE sustainability strategy, and passenger experience concept",
        "program": (
            "• Terminal façade and interior enhancement\n"
            "• Landscaped gardens and outdoor waiting zones\n"
            "• Rehabilitated terrace bar as social and passenger amenity\n"
            "• Reorganized Main Hall with improved circulation and flow\n"
            "• Switzerland-inspired lounges with wooden/glazed façades and carpeted areas\n"
            "• HQE-certified environmental performance strategy"
        ),
        "fun_facts": (
            "• Annecy Mont-Blanc Airport is one of the few French general aviation terminals to achieve HQE (High Environmental Quality) certification.\n"
            "• The terminal design drew inspiration from Swiss alpine aesthetics — bio-sourced materials, wood, and integrated vegetation creating a warm contrast to the technical aviation context.\n"
            "• 1PAX's work on this concession helped Vinci Airports win the management of an 80,000-passenger alpine gateway — a niche but strategically important aviation market."
        ),
    },

    "conakry_airport": {
        "display_name": "Conakry–Gbessia International Airport – Expansion",
        "category": "Airports and Transportation",
        "location": "Conakry, Guinea",
        "year": "2020–ongoing",
        "client": "Conakry–Gbessia International Airport",
        "architect": "1PAX",
        "partners": "EGIS Bâtiment, EGIS Avia",
        "area": "27,500 m²",
        "capacity": "N/A",
        "cost": "107 million € HT",
        "video_url": "",
        "tagline": (
            "Delivering robust auxiliary infrastructure to support operational growth, "
            "safety, and long-term airport performance."
        ),
        "overview": (
            "Starting in 2020, 1PAX was commissioned for the expansion of Conakry–Gbessia "
            "International Airport, focusing on the design of key auxiliary facilities essential "
            "to the airport's operational efficiency and resilience. Working in collaboration "
            "with EGIS Bâtiment and EGIS Avia, the scope addressed a total area of approximately "
            "27,500 m² and formed part of a major investment program aimed at strengthening the "
            "airport's capacity and technical performance. "
            "The project delivers a cohesive suite of auxiliary buildings that reinforce the "
            "operational backbone of Conakry–Gbessia International Airport. By combining "
            "technical rigor with architectural consistency, the expansion enhances safety, "
            "reliability, and efficiency across airport operations. The outcome supports the "
            "airport's long-term development ambitions, providing resilient infrastructure "
            "capable of accommodating future growth while maintaining high standards of "
            "performance and service."
        ),
        "key_challenge": (
            "The expansion required the integration of multiple highly technical facilities "
            "within an active airport environment. The challenge was to ensure that each "
            "building—administrative, operational, and safety-related—met strict standards for "
            "security, accessibility, maintenance, and durability, while achieving architectural "
            "coherence and seamless integration within the overall airport site."
        ),
        "approach": (
            "1PAX defined clear architectural and technical principles for a set of "
            "complementary facilities, including an administrative headquarters, a cargo "
            "building, a power plant, and an SSLIA fire station. The design approach emphasized "
            "functional clarity, operational efficiency, and long-term robustness. Particular "
            "attention was given to the selection of high-quality, durable materials suited to "
            "local climatic conditions, as well as to the careful organization of spaces to "
            "ensure safe circulation, ease of maintenance, and compliance with international "
            "airport standards."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Conakry expansion prioritizes long-term operational resilience through the "
            "selection of high-quality, climate-appropriate materials suited to Guinea's "
            "tropical environment. The design of the auxiliary buildings—including the power "
            "plant and SSLIA fire station—integrates efficient infrastructure layouts that "
            "minimize energy waste and simplify maintenance. The durable construction approach "
            "is designed to reduce lifecycle costs and support the airport's long-term "
            "development without requiring premature replacement."
        ),
        "status": "Under construction — ongoing (from 2020)",
        "tender_result": "Direct commission by Conakry–Gbessia International Airport",
        "scope": "Architectural design for a suite of auxiliary airport buildings totaling approximately 27,500 m²",
        "program": (
            "• Administrative headquarters building\n"
            "• Cargo building\n"
            "• Power plant\n"
            "• SSLIA fire station\n"
            "• Integration with airport operational and safety systems"
        ),
        "fun_facts": (
            "• Conakry–Gbessia is Guinea's principal international airport, serving one of West Africa's fastest-growing economies.\n"
            "• The project is unusual in its focus entirely on auxiliary buildings rather than the passenger terminal — reflecting the airport's need to strengthen its operational backbone before expanding passenger capacity.\n"
            "• At 107 million € HT, this is one of the largest airport infrastructure investments 1PAX has been involved with in sub-Saharan Africa."
        ),
    },

    "papeete_airport": {
        "display_name": "Papeete Faa'a International Airport – Concession Competition (Winner)",
        "category": "Airports and Transportation",
        "location": "Papeete Faa'a, Tahiti, French Polynesia",
        "year": "2020",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "Michel Forges",
        "area": "N/A",
        "capacity": "1.9 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "https://vimeo.com/1166384536/2c6c13278b?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Optimizing capacity and passenger experience through culturally rooted design "
            "and strategic terminal expansion."
        ),
        "overview": (
            "In 2020, 1PAX supported Vinci Airports in the winning concession proposal for "
            "Papeete Faa'a International Airport, Tahiti's primary international gateway. "
            "Serving nearly 2 million passengers annually, the airport plays a vital role in "
            "connecting French Polynesia to international and regional destinations. The project "
            "focused on defining a clear development strategy to improve passenger flow, service "
            "levels, and long-term operational performance, while reinforcing the airport's "
            "strong cultural identity. "
            "The project delivered a robust and culturally sensitive framework for the evolution "
            "of Papeete Faa'a International Airport. By aligning capacity planning, architectural "
            "identity, and operational efficiency, the proposal improves passenger experience "
            "during peak periods while preparing the airport for future growth. The successful "
            "concession outcome positions Papeete Airport as a welcoming, efficient, and "
            "culturally expressive gateway to French Polynesia."
        ),
        "key_challenge": (
            "Passenger traffic at Papeete Airport is characterized by pronounced peak periods, "
            "with high-density international arrivals and departures concentrated in the morning "
            "and shorter departures in the evening, while domestic traffic remains evenly "
            "distributed throughout the day. These dynamics created pressure on existing "
            "facilities and highlighted the need for short-term capacity expansion. The challenge "
            "was to address these constraints while maintaining operational continuity, improving "
            "comfort, and controlling energy consumption and operating costs."
        ),
        "approach": (
            "1PAX carried out detailed capacity and peak-hour studies based on a representative "
            "operational day, identifying critical bottlenecks and prioritizing targeted "
            "expansion. The architectural strategy combined terminal extensions and the addition "
            "of boarding bridges to improve passenger comfort, aircraft interface efficiency, "
            "and overall service quality. "
            "The design approach integrated traditional Polynesian architectural elements, "
            "translating local culture, materials, and spatial openness into a contemporary "
            "airport environment. Renovation of existing spaces was combined with upgrades to "
            "building systems, improving energy efficiency and reducing long-term operating "
            "costs while enhancing spatial quality."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Energy efficiency and reduced operating costs were central objectives. Building "
            "system upgrades improve energy performance and reduce long-term operational "
            "expenditure. The integration of traditional Polynesian architecture and local "
            "materials supports a low-impact approach that respects local environmental and "
            "cultural context. Peak-hour studies enabled targeted expansion rather than "
            "wholesale reconstruction, minimizing unnecessary construction and embedded carbon."
        ),
        "status": "Concession support — design proposal delivered 2020",
        "tender_result": "Concession support — won (2020), supporting Vinci Airports' successful bid",
        "scope": "Architectural design support for concession proposal — capacity studies, terminal extensions, boarding bridge additions, and building system upgrades",
        "program": (
            "• Detailed peak-hour capacity studies for terminal operations\n"
            "• Terminal extensions to address identified bottlenecks\n"
            "• Addition of boarding bridges to improve passenger comfort and aircraft interface\n"
            "• Building system upgrades for improved energy efficiency\n"
            "• Integration of traditional Polynesian architectural elements into terminal design"
        ),
        "fun_facts": (
            "• Papeete Faa'a is the only international airport in French Polynesia, serving an archipelago of 118 islands spread across a sea area the size of Europe.\n"
            "• The airport experiences dramatic peak-hour surges driven by long-haul international flights, creating operational intensity that shaped the entire design strategy.\n"
            "• The architectural concept deliberately integrated traditional Polynesian culture — wood, open structures, and spatial openness — into a contemporary aviation environment."
        ),
    },

    "amilcar_cabral_airport": {
        "display_name": "Amílcar Cabral International Airport – Concession Assistance (Winner)",
        "category": "Airports and Transportation",
        "location": "Sal Island, Cabo Verde",
        "year": "2019 (concession) – 2025 (Phase 1B)",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "NRV, Saguez",
        "area": "N/A",
        "capacity": "2 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "https://vimeo.com/1166381892/9317a5c8f5?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Reimagining an island gateway through climate-driven design and the Open "
            "Airport concept."
        ),
        "overview": (
            "In 2019, 1PAX supported Vinci Airports in the successful concession process for "
            "Amílcar Cabral International Airport on Sal Island, one of Cabo Verde's primary "
            "international gateways. The mission, extended into Phase 1B planning in 2025, "
            "focused on defining a development strategy capable of enhancing operational "
            "performance and passenger experience while responding to the island's specific "
            "climatic and environmental conditions. With a capacity of approximately 2 million "
            "passengers, the airport plays a central role in the country's tourism and "
            "international connectivity. "
            "The project delivered a forward-looking framework aligning passenger experience, "
            "operational efficiency, and environmental performance. By translating local climatic "
            "advantages into architectural and technical solutions, 1PAX helped position Amílcar "
            "Cabral International Airport as a benchmark for sustainable airport development in "
            "island contexts. The Open Airport vision offers a resilient, low-carbon, and "
            "passenger-centered model for future growth in Cabo Verde."
        ),
        "key_challenge": (
            "The challenge was to improve service levels and passenger comfort while minimizing "
            "environmental impact and operational costs. Any expansion or refurbishment needed "
            "to be resilient, low-energy, and well adapted to Sal Island's dry climate, stable "
            "temperatures, and limited rainfall, while supporting seamless connectivity and "
            "efficient airport operations."
        ),
        "approach": (
            "1PAX contributed to the concession technical documentation and developed a design "
            "strategy centered on the innovative Open Airport concept. The proposal introduced "
            "environmentally responsible terminal extensions designed to significantly reduce "
            "carbon emissions, targeting near-zero energy demand. "
            "By leveraging Sal Island's favorable climate—characterized by natural ventilation "
            "potential and consistent temperatures around 25°C—the design eliminated the need "
            "for conventional HVAC systems. Lightweight structures, passive environmental "
            "strategies, and sustainable materials formed the backbone of the architectural "
            "approach, ensuring comfort, simplicity, and efficiency. The concept reinforced "
            "visual openness, intuitive passenger movement, and strong indoor–outdoor "
            "relationships."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability is the central pillar of this project. The Open Airport concept "
            "targets near-zero energy demand by eliminating conventional HVAC systems, instead "
            "leveraging Sal Island's natural ventilation potential and stable 25°C temperatures. "
            "Lightweight structures, passive environmental strategies, and sustainable materials "
            "minimize embodied carbon and operational energy use. The result is a benchmark for "
            "low-carbon, climate-adapted airport design in island contexts."
        ),
        "status": "Concession support — design proposal delivered 2019; Phase 1B planning ongoing to 2025",
        "tender_result": "Concession support — won (2019), supporting Vinci Airports' successful bid",
        "scope": "Architectural design support for concession proposal — Open Airport concept, near-zero energy terminal extensions, and sustainable design strategy for Sal Island",
        "program": (
            "• Open Airport concept — terminal extensions designed for near-zero energy demand\n"
            "• Elimination of conventional HVAC systems through passive ventilation design\n"
            "• Lightweight structures with sustainable materials\n"
            "• Visual openness and intuitive passenger movement strategy\n"
            "• Phase 1B planning for further development (2025)"
        ),
        "fun_facts": (
            "• The Open Airport concept at Amílcar Cabral targets near-zero energy demand — an extraordinary ambition for airport infrastructure anywhere in the world.\n"
            "• Sal Island's remarkably stable climate (around 25°C year-round) made it uniquely suited to passive ventilation strategies, eliminating the need for air conditioning.\n"
            "• Amílcar Cabral International Airport is named after the celebrated anti-colonial leader — a figure of enormous symbolic importance in Cabo Verde's national identity."
        ),
    },

    "nelson_mandela_airport": {
        "display_name": "Nelson Mandela International Airport – Assistance for the Concession (Winner)",
        "category": "Airports and Transportation",
        "location": "Santiago, Cabo Verde",
        "year": "2019 (concession) – 2025 (Phase 1B)",
        "client": "Vinci Airports, Cabo Verde Airports",
        "architect": "1PAX",
        "partners": "NRV, Saguez",
        "area": "N/A",
        "capacity": "2 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Strengthening a national gateway through operational efficiency, connectivity, "
            "and an enhanced passenger experience."
        ),
        "overview": (
            "In 2019, 1PAX supported Vinci Airports and Cabo Verde Airports in the successful "
            "concession process for Nelson Mandela International Airport, located in Santiago, "
            "approximately 5 km east of Praia. The mission, extended into Phase 1B planning in "
            "2025, addressed one of the country's most strategic airports, certified in 2017 as "
            "a category 4D facility and serving both passenger and cargo traffic at the national "
            "and international levels. "
            "The project provided a coherent and forward-looking framework for the development "
            "of Nelson Mandela International Airport. By aligning operational efficiency, spatial "
            "clarity, and passenger comfort, 1PAX helped define an airport experience that is "
            "both functional and welcoming—positioning the airport as a well-connected, "
            "contemporary gateway supporting Cabo Verde's mobility and economic development."
        ),
        "key_challenge": (
            "The airport faced the need to improve operational performance and manage growing "
            "passenger and cargo flows while reinforcing its role as a primary gateway to the "
            "archipelago. The challenge was to enhance connectivity, rationalize landside and "
            "airside operations, and upgrade the passenger experience—without compromising "
            "flexibility or the airport's long-term development potential."
        ),
        "approach": (
            "1PAX contributed to the technical documentation for the concession, focusing on "
            "strategies to optimize passenger and cargo traffic management and strengthen "
            "overall connectivity. The design approach emphasized the 'Open Airport' concept, "
            "promoting transparency, visual continuity, and intuitive passenger movement. "
            "Architectural and interior strategies incorporated modern design elements and "
            "framed views to enhance the quality of the passenger journey. Landside organization "
            "was carefully structured, with public and bus parking areas, car parks, and a "
            "dedicated taxi rank all accessed via a clear, legible roundabout, simplifying "
            "circulation and improving first and last impressions of the airport."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Open Airport concept promotes passive design strategies—natural ventilation, "
            "visual openness, and lightweight structures—to minimize energy demand. The "
            "rationalized landside organization reduces vehicle circulation and idle times, "
            "supporting lower operational carbon emissions. The strategy is designed for "
            "long-term adaptability, reducing the need for costly future redesigns."
        ),
        "status": "Concession support — design proposal delivered 2019; Phase 1B planning ongoing to 2025",
        "tender_result": "Concession support — won (2019), supporting Vinci Airports and Cabo Verde Airports' successful bid",
        "scope": "Architectural design support for concession proposal — Open Airport concept, passenger experience strategy, and landside organization for Nelson Mandela International Airport",
        "program": (
            "• Open Airport concept — transparent, visually open terminal design\n"
            "• Optimized passenger and cargo traffic management strategy\n"
            "• Rationalized landside organization: public/bus parking, car parks, dedicated taxi rank\n"
            "• Modern architectural and interior design elements with framed views\n"
            "• Phase 1B planning for further development (2025)"
        ),
        "fun_facts": (
            "• Nelson Mandela International Airport is located approximately 5 km east of Praia, the capital of Cabo Verde — serving both domestic and international routes as a certified category 4D facility.\n"
            "• The airport is one of two major international airports serving Santiago Island, the most populous island in the Cabo Verde archipelago.\n"
            "• 1PAX developed the Open Airport concept for multiple Cabo Verde airports simultaneously — creating a coherent, island-adapted design philosophy across an entire national network."
        ),
    },

    "aristides_pereira_airport": {
        "display_name": "Aristides Pereira International Airport – Assistance for the Concession (Winner)",
        "category": "Airports and Transportation",
        "location": "Boa Vista, Cabo Verde",
        "year": "2019 (concession) – 2025 (Phase 1B)",
        "client": "Vinci Airports, Cabo Verde Airports",
        "architect": "1PAX",
        "partners": "NRV, Saguez",
        "area": "4,465 m² (existing terminal)",
        "capacity": "2 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Upgrading a strategic island gateway to support growing international traffic "
            "and improve passenger experience."
        ),
        "overview": (
            "In 2019, 1PAX supported Vinci Airports and Cabo Verde Airports in the successful "
            "concession process for Aristides Pereira International Airport, located on the "
            "island of Boa Vista. The mission extended into Phase 1B planning in 2025 and "
            "focused on defining a clear development strategy for one of Cabo Verde's key "
            "international airports. Certified in 2017 and classified as category 4D, the "
            "airport plays a central role in the archipelago's tourism-driven economy and "
            "international connectivity. "
            "The project provided a structured and realistic roadmap for the airport's "
            "development, aligned with international standards and the specific context of an "
            "island destination. By improving capacity, comfort, and operational systems, the "
            "proposal enhances the experience for both passengers and airlines while "
            "strengthening Boa Vista's role as a key international gateway."
        ),
        "key_challenge": (
            "The airport was experiencing increasing international traffic that exceeded the "
            "capacity and comfort levels of its existing facilities. The challenge was to "
            "modernize and expand the terminal while maintaining operational continuity, "
            "improving environmental performance, and upgrading technical systems essential "
            "to airport safety, comfort, and efficiency."
        ),
        "approach": (
            "1PAX contributed to the concession technical documentation and proposed a targeted "
            "expansion and refurbishment strategy for the existing terminal building, covering "
            "approximately 4,465 m². The approach focused on increasing passenger space and "
            "improving environmental comfort through air-conditioning in public areas. "
            "The project also addressed complementary infrastructure needs, including the "
            "planning of a dedicated cargo terminal, streamlined aircraft fueling systems, "
            "wastewater management solutions, and the integration of solar energy development. "
            "Each intervention was conceived to enhance operational performance while supporting "
            "sustainability and long-term resilience."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability is embedded throughout: solar energy development reduces grid "
            "dependency; wastewater management solutions address environmental impact in a "
            "sensitive island context; streamlined fueling systems reduce spill risk and "
            "improve efficiency. The targeted refurbishment approach—working within the "
            "existing 4,465 m² terminal—minimizes embodied carbon compared to demolition "
            "and full reconstruction."
        ),
        "status": "Concession support — design proposal delivered 2019; Phase 1B planning ongoing to 2025",
        "tender_result": "Concession support — won (2019), supporting Vinci Airports and Cabo Verde Airports' successful bid",
        "scope": "Architectural design support for concession proposal — terminal expansion strategy, cargo terminal planning, solar energy integration, and wastewater management for Boa Vista Island",
        "program": (
            "• Targeted expansion and refurbishment of existing 4,465 m² terminal\n"
            "• Air-conditioning for public areas to improve environmental comfort\n"
            "• Dedicated cargo terminal planning\n"
            "• Streamlined aircraft fueling systems\n"
            "• Wastewater management solutions\n"
            "• Solar energy development integration\n"
            "• Phase 1B planning for further development (2025)"
        ),
        "fun_facts": (
            "• Aristides Pereira International Airport is named after the founding president of Cabo Verde — the leader who guided the islands to independence in 1975.\n"
            "• Boa Vista is Cabo Verde's third-largest island and one of its most popular tourism destinations — the airport is the primary entry point for international beach tourism.\n"
            "• The project team worked on three Cabo Verde airports simultaneously (Sal, Santiago, Boa Vista) as part of a unified national concession — a rare multi-island aviation design assignment."
        ),
    },

    "lille_airport": {
        "display_name": "Lille International Airport – Concession Competition",
        "category": "Airports and Transportation",
        "location": "Lille, France",
        "year": "November 2018 – May 2019",
        "client": "Eiffage Concession",
        "architect": "1PAX",
        "partners": "None listed",
        "area": "N/A",
        "capacity": "up to 5.4 million passengers annually",
        "cost": "N/A (competition entry)",
        "video_url": "",
        "tagline": (
            "Reimagining the passenger experience to support sustainable growth and "
            "long-term terminal evolution."
        ),
        "overview": (
            "Between November 2018 and May 2019, 1PAX participated in the concession "
            "competition for Lille International Airport, commissioned by Eiffage Concession. "
            "The proposal addressed an airport serving up to 5.4 million passengers annually "
            "and focused on defining a strategic vision capable of supporting future growth "
            "through the renovation and expansion of the existing terminal. "
            "The competition proposal delivered a clear and future-oriented vision for Lille "
            "International Airport, aligning passenger comfort, operational performance, and "
            "environmental responsibility. By coupling terminal modernization with digital "
            "innovation and improved public transport integration, the project positioned the "
            "airport for sustainable growth and enhanced competitiveness within the regional "
            "aviation network."
        ),
        "key_challenge": (
            "The airport faced the dual challenge of improving customer experience while "
            "preparing for capacity expansion within an existing infrastructure. The project "
            "needed to enhance service quality, streamline passenger flows, and integrate new "
            "technologies, all while responding to increasing environmental expectations and "
            "the necessity for better connectivity with the surrounding territory."
        ),
        "approach": (
            "1PAX developed a proposal centered on passenger experience, operational efficiency, "
            "and adaptability. The strategy combined targeted terminal renovation with phased "
            "expansion, ensuring continuity of operations and long-term flexibility. Digital "
            "technologies were integrated as key enablers to improve wayfinding, service quality, "
            "and overall passenger satisfaction. "
            "At the territorial scale, particular attention was given to strengthening public "
            "transportation links to the airport, reducing reliance on private vehicles and "
            "supporting more sustainable access strategies."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Environmental responsibility was a core pillar. The strategy addresses increasing "
            "environmental expectations through phased, low-disruption terminal renovation and "
            "expansion. Strengthening public transport links reduces private vehicle dependency "
            "and associated carbon emissions. Digital wayfinding and flow optimization "
            "technologies reduce energy waste from inefficient circulation patterns. The "
            "proposal is designed for long-term operational flexibility and reduced lifecycle "
            "costs."
        ),
        "status": "Competition entry — not awarded (2018–2019)",
        "tender_result": "Competition entry for Eiffage Concession — concession competition",
        "scope": "Architectural and strategic design for concession competition proposal — terminal renovation, phased expansion, digital integration, and public transport connectivity",
        "program": (
            "• Terminal renovation and phased expansion strategy\n"
            "• Digital technology integration for wayfinding and passenger services\n"
            "• Strengthened public transport links to the airport\n"
            "• Passenger experience improvements across terminal zones\n"
            "• Long-term adaptability framework for up to 5.4 million passengers annually"
        ),
        "fun_facts": (
            "• Lille International Airport sits at the heart of one of Europe's most connected regions — within 90 minutes of Paris, Brussels, and London by rail.\n"
            "• 1PAX's proposal for the Lille concession prioritized digital innovation as a core differentiator — a forward-looking approach at a time when airport digitalization was still emerging.\n"
            "• The competition ran from November 2018 to May 2019 — a rapid six-month design sprint for a complex concession proposal."
        ),
    },

    "fuzhou_airport": {
        "display_name": "Fuzhou New International Airport – Passenger Terminal & Rail Integration (2nd Prize)",
        "category": "Airports and Transportation",
        "location": "Fuzhou, China",
        "year": "2017 (competition)",
        "client": "Fuzhou Airport Authority",
        "architect": "1PAX, ECADI, AVIC CAPDI",
        "partners": "None listed",
        "area": "275,000 m²",
        "capacity": "25 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "A multimodal airport city vision combining aviation capacity, rail connectivity, "
            "and long-term urban development."
        ),
        "overview": (
            "In 2017, 1PAX participated in the international design competition for the new "
            "passenger terminal at Fuzhou New International Airport, awarded second prize. The "
            "project was developed within a multidisciplinary team led by ECADI and AVIC CAPDI, "
            "acting as Lead Designers for both the terminal architecture and the extension of "
            "Fuzhou's city rail network. The proposal addressed a major new airport "
            "infrastructure designed to serve up to 25 million passengers annually. "
            "The proposal delivered a clear, scalable vision for Fuzhou's new international "
            "gateway, positioning the airport as both a transportation hub and a driver of "
            "urban development. By integrating air, rail, and road systems within a cohesive "
            "masterplan, the project supported efficient operations, strong connectivity, and "
            "sustainable long-term growth."
        ),
        "key_challenge": (
            "The competition required reconciling high-capacity aviation infrastructure with "
            "seamless multimodal connectivity and long-term urban development. The challenge "
            "was to maximize airside efficiency—particularly aircraft parking capacity—while "
            "creating a generous, flexible landside environment capable of evolving into a "
            "future 'airport city' integrated with regional transport networks."
        ),
        "approach": (
            "The team developed a comprehensive masterplan integrating the new passenger "
            "terminal with existing road systems and a direct connection to the extended city "
            "rail network. The terminal layout was designed to optimize aircraft parking stands "
            "and airside operations, while the landside strategy established a strong interface "
            "with the rail station as a catalyst for urban development. "
            "The masterplan envisioned a mixed-use airport city incorporating offices, retail "
            "areas, parking facilities, conference centers, and hotels. Sustainability and "
            "long-term flexibility were central to the design approach, ensuring that buildings "
            "and public spaces could adapt to future demands, technological evolution, and "
            "phased growth."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability and long-term flexibility were central design principles. The "
            "airport city concept promotes multimodal transport—reducing car dependency by "
            "directly connecting the terminal to the city rail network. The masterplan's phased "
            "growth strategy ensures buildings can adapt to future demands without wholesale "
            "reconstruction, reducing lifecycle waste across the 275,000 m² development."
        ),
        "status": "Competition entry — 2nd Prize (2017)",
        "tender_result": "Winner of international competition — 2nd Prize",
        "scope": "Competition design — 275,000 m² passenger terminal, airport masterplan, and rail integration for Fuzhou New International Airport",
        "program": (
            "• Passenger terminal — 275,000 m² designed for 25 million passengers annually\n"
            "• Airport masterplan integrating airside parking, apron taxiways, cargo/freight, runway configuration, and ATCT positioning\n"
            "• Direct connection to extended Fuzhou city rail network\n"
            "• Mixed-use airport city: offices, retail, parking, conference centres, hotels\n"
            "• Landside real estate strategy for long-term non-aeronautical development"
        ),
        "fun_facts": (
            "• At 275,000 m² and 25 million passengers, the Fuzhou proposal is among the largest terminal designs ever produced by 1PAX.\n"
            "• The project won second prize in an international competition involving some of the world's leading airport design firms.\n"
            "• The airport city vision integrated a direct city rail extension — making Fuzhou one of the first Chinese airports designed from inception around multimodal urban connectivity."
        ),
    },

    "euroairport_modernization": {
        "display_name": "EuroAirport Basel–Mulhouse–Freiburg – Terminal Extension & South Gates Modernization",
        "category": "Airports and Transportation",
        "location": "Mulhouse, France",
        "year": "2018",
        "client": "Basel Mulhouse Airport Authority",
        "architect": "1PAX (part of multidisciplinary team)",
        "partners": "FERRIER, NORDIC, ARCADIS, WEST8, TG CONCEPT, MILIEU",
        "area": "90,000 m²",
        "capacity": "12 million passengers annually",
        "cost": "200 million €",
        "video_url": "",
        "tagline": (
            "Reorganizing landside and terminal interfaces to improve capacity, clarity, and "
            "long-term passenger flow performance."
        ),
        "overview": (
            "In 2018, 1PAX participated as part of a multidisciplinary team to support the "
            "extension and modernization of the EuroAirport terminal, focusing on the South "
            "Gates and the broader East Terminal zone. The large-scale project addressed "
            "approximately 90,000 m² of terminal and interface areas within an airport serving "
            "up to 12 million passengers, forming a key trinational gateway between France, "
            "Switzerland, and Germany. "
            "The project delivered a robust framework for the modernization of EuroAirport's "
            "East Terminal, significantly improving traffic organization, passenger flow, and "
            "overall legibility. By clarifying interfaces between landside mobility, parking, "
            "and terminal access, the proposal supports smoother operations, reduced "
            "congestion, and an enhanced passenger experience across this major trinational hub."
        ),
        "key_challenge": (
            "The East Terminal zone faced increasing congestion and operational complexity due "
            "to growing passenger volumes, overlapping traffic flows, and fragmented access "
            "systems. The challenge was to reorganize landside and terminal circulation to "
            "improve passenger experience and operational efficiency, while ensuring the system "
            "could adapt to medium- and long-term growth without disrupting airport operations."
        ),
        "approach": (
            "The project proposed a comprehensive reorganization of traffic and passenger flows "
            "across multiple levels of the terminal interface. Key interventions included the "
            "relocation and clarification of access routes to the Swiss and French delivery "
            "zones, the reconfiguration of parking areas for passengers, staff, VTC services, "
            "and buses, and the optimization of vehicle movements around the terminal. "
            "At the terminal scale, the second level was redesigned to improve taxi and bus "
            "circulation. The third-level viaduct was simplified by realigning connections "
            "between the terminal and the multimodal hall. These interventions were conceived "
            "as part of a phased strategy, supporting both immediate improvements and long-term "
            "adaptability."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The reorganization of traffic and passenger flows reduces congestion-related "
            "energy waste across the 90,000 m² terminal zone. The phased strategy minimizes "
            "construction disruption, avoiding costly shutdowns at this busy trinational hub. "
            "Reconfigured parking and access routes are designed to reduce vehicle idle times "
            "and improve overall landside energy efficiency for the 12 million passengers "
            "served annually."
        ),
        "status": "Study completed 2018",
        "tender_result": "Direct commission as part of multidisciplinary team",
        "scope": "Terminal extension and South Gates modernization study — traffic and passenger flow reorganization across 90,000 m² East Terminal zone",
        "program": (
            "• Relocation and clarification of Swiss and French delivery zone access routes\n"
            "• Reconfiguration of passenger, staff, VTC, and bus parking areas\n"
            "• Optimization of vehicle circulation around the terminal\n"
            "• Redesign of second-level taxi and bus circulation\n"
            "• Simplification of third-level viaduct connections to multimodal hall\n"
            "• Phased strategy for immediate and long-term adaptability"
        ),
        "fun_facts": (
            "• EuroAirport Basel–Mulhouse–Freiburg is one of the world's few airports serving three countries simultaneously — France, Switzerland, and Germany — each with its own customs and immigration zone.\n"
            "• The trinational nature of the airport creates uniquely complex traffic and access patterns — Swiss and French zones have entirely separate delivery, staffing, and passenger systems.\n"
            "• 1PAX worked alongside a broad multidisciplinary team including FERRIER, NORDIC, ARCADIS, WEST8, TG CONCEPT, and MILIEU — one of the most collaborative projects in the firm's portfolio."
        ),
    },

    "lanzhou_airport": {
        "display_name": "Lanzhou New International Airport – Masterplan & Terminal Design (2nd Prize)",
        "category": "Airports and Transportation",
        "location": "Lanzhou, China",
        "year": "2017 (competition)",
        "client": "Lanzhou Airport Authority, ECADI",
        "architect": "1PAX",
        "partners": "ECADI, AVIC",
        "area": "377,000 m²",
        "capacity": "30 million passengers (Phase 1) – 46 million passengers (subsequent phases)",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "A scalable and sustainable airport vision designed to support long-term growth "
            "and operational excellence."
        ),
        "overview": (
            "In 2017, 1PAX was awarded second prize in the international competition for the "
            "new Lanzhou International Airport, commissioned by the Lanzhou Airport Authority "
            "and ECADI. The project encompassed the development of a comprehensive airport "
            "masterplan and the architectural design of the Terminal Building. Working in "
            "partnership with ECADI and AVIC, 1PAX addressed an infrastructure of metropolitan "
            "scale, planned to accommodate 30 million passengers in Phase 1 and up to 46 "
            "million passengers in subsequent phases. "
            "The proposal delivered a coherent, future-ready vision for Lanzhou's new "
            "international gateway. By combining comprehensive masterplanning with a flexible "
            "and sustainable terminal architecture, 1PAX provided a robust framework capable "
            "of evolving with traffic demand and operational requirements."
        ),
        "key_challenge": (
            "The main challenge was to conceive a new airport capable of supporting significant "
            "long-term growth while maintaining clarity, efficiency, and environmental "
            "responsibility. The project required the coordination of complex airside and "
            "landside systems, future-proof capacity planning, and a terminal architecture "
            "flexible enough to adapt to evolving operational and passenger needs."
        ),
        "approach": (
            "1PAX developed an integrated masterplan covering airside parking stands, apron "
            "taxiways, cargo and freight facilities, runway configuration, and the positioning "
            "of the air traffic control tower. Equal emphasis was placed on landside "
            "accessibility, passenger flows, and a long-term real estate strategy to support "
            "non-aeronautical development. "
            "For the Terminal Building, 1PAX proposed a contemporary architectural concept "
            "grounded in sustainability, modularity, and phased expansion. The terminal layout "
            "was designed to ensure seamless operations for passengers, visitors, and airport "
            "personnel, with clear circulation, intuitive wayfinding, and adaptable structural "
            "systems. Sustainability principles informed both planning and architecture, enabling "
            "efficient resource use and long-term environmental performance."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability principles were embedded throughout both masterplan and terminal "
            "design. The modular terminal architecture enables phased expansion—from 30 to 46 "
            "million passengers—without wholesale reconstruction, minimizing future embodied "
            "carbon. The masterplan integrates efficient apron taxiway layouts to reduce "
            "aircraft ground movement times and fuel consumption. Adaptable structural systems "
            "support long-term energy efficiency and reduced lifecycle operational costs."
        ),
        "status": "Competition entry — 2nd Prize (2017)",
        "tender_result": "Winner of international competition — 2nd Prize",
        "scope": "Competition design — comprehensive airport masterplan and terminal building, 377,000 m², for Lanzhou New International Airport",
        "program": (
            "• Passenger terminal — 377,000 m² designed for 30 million passengers (Phase 1) and 46 million (full build)\n"
            "• Full airport masterplan: airside parking stands, apron taxiways, cargo/freight, runway configuration, ATCT positioning\n"
            "• Landside accessibility, passenger flow design, and long-term real estate strategy\n"
            "• Modular, phased terminal architecture for scalable expansion\n"
            "• Sustainability principles embedded in planning and architecture"
        ),
        "fun_facts": (
            "• At 377,000 m² and 46 million passengers at full capacity, the Lanzhou proposal is one of the largest airport designs ever produced by 1PAX.\n"
            "• Lanzhou is the capital of Gansu Province in northwestern China — a gateway city linking China's eastern cities to Central Asia and the ancient Silk Road.\n"
            "• The project won second prize in an international competition alongside industry giants — recognizing 1PAX's expertise in large-scale Asian airport design."
        ),
    },

    "mashhad_airport": {
        "display_name": "New Mashhad International Airport – Extension & Domestic Terminal",
        "category": "Airports and Transportation",
        "location": "Mashhad, Iran",
        "year": "2016–2019",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "Vinci Airports, VCGP",
        "area": "60,000 m² (international) + 33,000 m² (domestic)",
        "capacity": "11 million passengers (Phase 1) – 18 million passengers (Phase 2)",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "A culturally rooted and future-ready airport expansion supporting phased growth "
            "and sustainable mobility."
        ),
        "overview": (
            "Between 2016 and 2019, 1PAX was commissioned by Vinci Airports to lead "
            "feasibility studies for the airport masterplan and to develop the architectural "
            "design of the new international terminal at Mashhad International Airport. The "
            "scope also included a comprehensive landside masterplan addressing access, parking, "
            "and public spaces, alongside a phased development strategy for the domestic "
            "terminal. The project supports a capacity increase from 11 million passengers in "
            "Phase 1 to 18 million passengers in Phase 2. "
            "The project delivers a coherent and scalable vision for Mashhad International "
            "Airport's transformation into a modern, high-capacity gateway, integrating "
            "masterplanning, architecture, mobility, and sustainability within a phased "
            "strategy that supports operational efficiency, cultural identity, and long-term "
            "environmental performance."
        ),
        "key_challenge": (
            "The project required accommodating rapid traffic growth while ensuring operational "
            "clarity, cultural relevance, and long-term sustainability. The challenge was to "
            "coordinate multiple large-scale components—international and domestic terminals, "
            "landside infrastructure, parking, and mobility systems—within a phased framework "
            "that minimizes disruption and remains adaptable to evolving passenger demand and "
            "transport technologies."
        ),
        "approach": (
            "1PAX developed an integrated masterplanning and architectural strategy. The new "
            "international terminal was conceived as the anchor of the expansion, supported by "
            "a comprehensive landside plan including access roads, pedestrian walkways, public "
            "spaces, and parking facilities. As part of Phase 2, a four-level multi-storey car "
            "park was planned in front of the international terminal. "
            "A key focus was placed on sustainable and electric mobility, with dedicated "
            "pedestrian routes, public realm enhancements, and a strategy for integrating "
            "electric transport solutions. The domestic terminal expansion included a dedicated "
            "electric road for shuttle services. All new buildings were designed to incorporate "
            "solar panels. Architecturally, the terminal draws inspiration from traditional "
            "motifs, blending cultural heritage with contemporary design and functional "
            "efficiency."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability and electric mobility are central to the Mashhad strategy. All new "
            "buildings incorporate solar panels, reducing grid energy dependency across a "
            "93,000 m² expansion. A dedicated electric road for shuttle services and an "
            "electric transport integration strategy for the landside masterplan significantly "
            "reduce ground transportation emissions. The phased approach minimizes construction "
            "disruption and enables efficient resource use throughout the development."
        ),
        "status": "Study completed — feasibility and design development 2016–2019",
        "tender_result": "Direct commission by Vinci Airports",
        "scope": "Architectural design — new international terminal (60,000 m²), landside masterplan, and domestic terminal expansion (33,000 m²) with electric mobility strategy",
        "program": (
            "• New international terminal — 60,000 m²\n"
            "• Comprehensive landside masterplan: access roads, pedestrian walkways, public spaces, parking\n"
            "• Four-level multi-storey car park (Phase 2)\n"
            "• Domestic terminal expansion with dedicated electric road for shuttle services\n"
            "• Solar panels on all new buildings\n"
            "• Cultural motif integration — traditional Iranian architectural elements in terminal design"
        ),
        "fun_facts": (
            "• Mashhad is one of Iran's holiest cities — a major pilgrimage destination receiving millions of religious visitors annually, placing extraordinary demands on airport capacity.\n"
            "• All new buildings were designed with solar panels as standard — a forward-thinking sustainability commitment at a time when solar integration was still rare in Iranian airport architecture.\n"
            "• The project featured a dedicated electric road for shuttle services between terminals — an early example of electric mobility integration in airport landside planning."
        ),
    },

    "almaty_airport": {
        "display_name": "Almaty International Airport – Masterplanning & New Terminal Design",
        "category": "Airports and Transportation",
        "location": "Almaty, Kazakhstan",
        "year": "2015–2016",
        "client": "Vinci Airports, VCGP",
        "architect": "1PAX",
        "partners": "ARUP",
        "area": "80,000 m²",
        "capacity": "8 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "A climate-responsive airport vision shaped by landscape, resilience, and "
            "long-term operational efficiency."
        ),
        "overview": (
            "Between 2015 and 2016, Vinci Airports selected 1PAX to develop the architectural "
            "concept design for the new international terminal at Almaty International Airport. "
            "The commission also included the airport masterplan, functional planning, and the "
            "design of access roads, parking facilities, and landscape systems. Working in "
            "collaboration with ARUP, 1PAX addressed the airport as an integrated territorial "
            "and architectural project, responding to both operational needs and the specific "
            "environmental conditions of Kazakhstan. "
            "The project delivered a resilient and sustainable vision for Almaty International "
            "Airport, combining masterplanning, architecture, and landscape into a single "
            "integrated strategy. By addressing seismic risk, climate performance, and "
            "operational clarity from the outset, 1PAX provided a robust framework that "
            "supports long-term energy efficiency, passenger comfort, and adaptability."
        ),
        "key_challenge": (
            "Almaty's geographical and climatic context posed significant challenges. The "
            "project needed to respond to complex topography, soil conditions, and high seismic "
            "risk, while also addressing extreme seasonal temperature variations. At the same "
            "time, the new terminal had to support growing passenger volumes and provide a "
            "clear, efficient passenger experience within a robust and future-ready "
            "infrastructure."
        ),
        "approach": (
            "1PAX developed a masterplan and terminal concept deeply informed by site "
            "conditions. The architectural strategy integrated a man-made landscape that played "
            "a dual role: absorbing and reusing the earthworks generated by extensive foundation "
            "excavations, and acting as an environmental buffer for the terminal. "
            "This landscape supports heat retention during cold seasons and mitigates heat gain "
            "during warmer periods. Passive heating and cooling principles guided the design of "
            "the terminal envelope, with particular attention to façade orientation and "
            "protection against extreme weather exposure. Access roads and parking areas were "
            "designed as part of a coherent landscape system, reinforcing legibility and ease "
            "of use."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability is the structural backbone of the Almaty design. The man-made "
            "landscape acts as a passive environmental buffer—retaining heat in Kazakhstan's "
            "severe winters and mitigating heat gain in summer—dramatically reducing HVAC "
            "demand across the 80,000 m² terminal. Earthworks from foundation excavations are "
            "reused to form this landscape, eliminating waste and reducing construction "
            "logistics. Passive heating and cooling principles govern façade orientation and "
            "envelope performance, enabling long-term energy efficiency in one of the world's "
            "most extreme climatic environments."
        ),
        "status": "Study completed — concept design 2015–2016",
        "tender_result": "Direct commission by Vinci Airports",
        "scope": "Architectural concept design — 80,000 m² new international terminal, airport masterplan, access roads, parking, and landscape systems",
        "program": (
            "• New international terminal — 80,000 m² designed for 8 million passengers annually\n"
            "• Airport masterplan integrating all airside and landside elements\n"
            "• Man-made landscape system for passive thermal regulation\n"
            "• Access roads and parking areas integrated into landscape strategy\n"
            "• Seismic-resilient structural approach for high-risk zone\n"
            "• Passive heating and cooling principles for extreme seasonal climate"
        ),
        "fun_facts": (
            "• Almaty sits in one of Central Asia's most seismically active zones — requiring a structural approach specifically designed to withstand major earthquakes.\n"
            "• The project's most innovative feature is its man-made landscape: earthworks from foundation excavations are reused to create a thermal buffer around the terminal, turning construction waste into an environmental asset.\n"
            "• Kazakhstan's climate swings from -30°C winters to +40°C summers — making the passive thermal design strategy a critical functional requirement, not just an architectural gesture."
        ),
    },

    "euroairport_south_gates": {
        "display_name": "EuroAirport Basel–Mulhouse–Freiburg – Extension of the Terminal's South Gates",
        "category": "Airports and Transportation",
        "location": "Saint-Louis, France",
        "year": "2018–2020",
        "client": "Aéroport de Bâle-Mulhouse",
        "architect": "1PAX",
        "partners": "GEC, AVLS, PROCOBAT",
        "area": "2,950 m²",
        "capacity": "Not disclosed",
        "cost": "5.9 million €",
        "video_url": "",
        "tagline": (
            "Expanding gate capacity through a sustainable, BIM-driven terminal extension "
            "tailored to low-cost operations."
        ),
        "overview": (
            "Between 2018 and 2020, 1PAX was commissioned by Aéroport de Bâle-Mulhouse to lead "
            "the architectural design of the South Gates extension at EuroAirport Basel–Mulhouse–Freiburg. "
            "The project comprises the construction of four new boarding gates, the refurbishment of five "
            "existing gates, and the addition of an upper floor accommodating airline offices. Developed in "
            "collaboration with GEC, AVLS, and PROCOBAT, the extension responds to the airport's increasing "
            "traffic, particularly driven by the growth of low-cost carriers. The South Gates extension "
            "significantly enhances EuroAirport's capacity and flexibility, allowing it to accommodate growing "
            "passenger volumes while maintaining smooth operations. Through a combination of sustainable design, "
            "technical rigor, and BIM-led delivery, the project provides a future-ready terminal extension that "
            "strengthens the airport's competitiveness and environmental performance within the trinational region."
        ),
        "key_challenge": (
            "The challenge was to increase gate capacity and operational efficiency within an active terminal "
            "environment while minimizing disruption to airport operations. At the same time, the project needed "
            "to meet ambitious sustainability objectives, ensuring high energy performance and long-term "
            "environmental responsibility without compromising functionality or passenger comfort."
        ),
        "approach": (
            "1PAX developed a clear and efficient architectural solution aligned with the specific operational "
            "requirements of low-cost airlines. Sustainability was embedded from the outset, supported by a "
            "detailed life cycle assessment and a high-performance building envelope targeting E+/C- "
            "certification. The entire project was designed using BIM, enabling precise coordination across "
            "disciplines and supporting the delivery of detailed and execution-level drawings. This approach "
            "ensured constructability, cost control, and seamless integration with existing terminal infrastructure."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability was a core commitment throughout the South Gates extension. A detailed life cycle "
            "assessment informed all design choices, and the building envelope was engineered to target E+/C- "
            "certification — one of the most demanding French environmental standards. BIM-led coordination "
            "ensured minimal material waste and precise constructability, while the overall design supports "
            "long-term energy efficiency and reduced operational carbon footprint."
        ),
        "status": "Built — completed 2020",
        "tender_result": "Direct commission by Aéroport de Bâle-Mulhouse",
        "scope": "Architectural design for South Gates extension — 2,950 m² comprising four new boarding gates, refurbishment of five existing gates, and new airline office floor",
        "program": (
            "• Four new boarding gates\n"
            "• Refurbishment of five existing boarding gates\n"
            "• New upper floor with airline offices\n"
            "• E+/C- high-performance building envelope\n"
            "• Full BIM delivery including detailed and execution-level drawings\n"
            "• Life cycle assessment integrated into all design decisions"
        ),
        "fun_facts": (
            "• EuroAirport Basel–Mulhouse–Freiburg is unique in Europe — it sits on French territory but is jointly managed by France and Switzerland, with separate customs zones for each country.\n"
            "• The South Gates extension targets E+/C- certification — one of France's most rigorous environmental building standards, rarely achieved for airport industrial buildings.\n"
            "• The project was entirely designed in BIM, enabling the production of both detailed design and execution-level drawings with exceptional precision and coordination."
        ),
    },

    "kigali_airport": {
        "display_name": "Kigali/Bugesera New International Airport – Terminal Consultation",
        "category": "Airports and Transportation",
        "location": "Kigali, Rwanda",
        "year": "2021",
        "client": "Vinci Construction / Qatar Airways Investments",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "Not disclosed",
        "capacity": "12 million passengers",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Value engineering and design optimisation for Rwanda's new international gateway."
        ),
        "overview": (
            "In 2021, 1PAX was commissioned by Vinci Construction and Qatar Airways Investments to provide "
            "expert consultation on the Kigali/Bugesera New International Airport project in Rwanda. The scope "
            "focused on value engineering and design review of the new terminal building, planned to accommodate "
            "12 million passengers. 1PAX's role was to analyse the existing design and identify targeted "
            "optimisations that would improve buildability, reduce costs, and enhance long-term performance "
            "without compromising the architectural quality or operational efficiency of the terminal. The "
            "consultation delivered concrete, actionable recommendations that improved the project's "
            "cost-effectiveness and constructability while supporting Rwanda's ambition to establish a "
            "world-class international hub in Kigali."
        ),
        "key_challenge": (
            "The project required a rigorous technical review of an existing terminal design, identifying "
            "opportunities to optimise structural and envelope systems — particularly roof seam details, "
            "skylight configurations, and solar heat gain control — while maintaining design intent and "
            "meeting the performance requirements for a 12-million-passenger facility in a tropical climate."
        ),
        "approach": (
            "1PAX conducted a detailed value engineering review focused on key building systems, including "
            "roof seam construction, the removal or replacement of skylight elements, and strategies to "
            "mitigate solar heat gains through envelope design. Recommendations were developed to improve "
            "constructability and reduce lifecycle costs, with particular attention to thermal performance "
            "and long-term maintainability in the local climatic context."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability considerations were central to the value engineering review. Key interventions "
            "addressed solar heat gain management through envelope optimisation, contributing to reduced "
            "cooling loads and improved energy performance. Skylight reconfiguration and roof detailing "
            "improvements were assessed for their lifecycle impact, supporting a more thermally efficient "
            "and operationally resilient terminal in Rwanda's tropical climate."
        ),
        "status": "Consultation completed — 2021",
        "tender_result": "Direct commission by Vinci Construction / Qatar Airways Investments",
        "scope": "Value engineering consultation and design review for 12-million-passenger terminal — roof, skylight, and envelope optimization",
        "program": (
            "• Value engineering review of terminal design\n"
            "• Roof seam construction analysis and improvement recommendations\n"
            "• Skylight removal/replacement strategy\n"
            "• Solar heat gain mitigation through envelope design\n"
            "• Lifecycle cost and constructability recommendations"
        ),
        "fun_facts": (
            "• The Kigali/Bugesera New International Airport is backed by Qatar Airways Investments — a rare example of a Gulf airline directly investing in African aviation infrastructure.\n"
            "• 1PAX was brought in specifically for value engineering expertise, reviewing an existing design by other architects and finding targeted improvements — a high-trust advisory role.\n"
            "• Rwanda's aviation ambitions are remarkable: Kigali is positioning itself as a pan-African hub, with RwandAir expanding rapidly across the continent."
        ),
    },

    "tocumen_airport": {
        "display_name": "Tocumen International Airport – Fire Safety Strategy Review",
        "category": "Airports and Transportation",
        "location": "Panama City, Panama",
        "year": "2019",
        "client": "Aeropuerto de Tocumen / EGIS",
        "architect": "1PAX",
        "partners": "Foster + Partners (terminal architect)",
        "area": "85,000 m²",
        "capacity": "16 million passengers",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Independent fire safety review ensuring NFPA 101 compliance for a landmark terminal expansion."
        ),
        "overview": (
            "In 2019, 1PAX was engaged by Aeropuerto de Tocumen and EGIS to conduct an independent fire "
            "safety strategy review for the new terminal expansion at Tocumen International Airport in Panama, "
            "designed by Foster + Partners. Covering approximately 85,000 m² and serving up to 16 million "
            "passengers, the project required a rigorous verification of compliance with NFPA 101 life safety "
            "standards. 1PAX's review provided a comprehensive fire safety assessment and evacuation strategy, "
            "ensuring the terminal met international safety requirements and could safely accommodate its "
            "projected passenger volumes. The consultation delivered a robust safety framework aligned with "
            "both regulatory requirements and operational best practices, supporting the airport's continued "
            "development as a major Latin American hub."
        ),
        "key_challenge": (
            "The challenge was to independently verify that the architectural and technical design of a "
            "large-scale, architecturally complex terminal — designed by Foster + Partners — met the stringent "
            "requirements of NFPA 101 life safety codes. This required deep expertise in fire safety "
            "engineering, evacuation modelling, and airport operations, applied to an 85,000 m² facility "
            "serving millions of passengers annually."
        ),
        "approach": (
            "1PAX conducted a systematic review of the terminal's fire safety strategy against NFPA 101 "
            "standards, assessing egress routes, evacuation capacity, fire compartmentation, and emergency "
            "systems. The team developed a detailed evacuation plan to ensure safe and efficient passenger "
            "movement under emergency conditions, identifying any gaps and recommending corrective measures "
            "to achieve full compliance with international life safety requirements."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "While the primary focus was fire safety and life safety compliance, the evacuation strategy "
            "and egress planning contributed to a safer, more operationally resilient terminal environment — "
            "a foundational element of sustainable, long-term airport infrastructure. Robust fire safety "
            "frameworks reduce the risk of catastrophic events and protect both lives and assets over the "
            "facility's operational lifetime."
        ),
        "status": "Consultation completed — 2019",
        "tender_result": "Direct commission by Aeropuerto de Tocumen / EGIS",
        "scope": "Independent fire safety strategy review and NFPA 101 compliance verification for 85,000 m² terminal expansion designed by Foster + Partners",
        "program": (
            "• Systematic NFPA 101 compliance review of terminal fire safety strategy\n"
            "• Egress route and evacuation capacity assessment\n"
            "• Fire compartmentation and emergency systems evaluation\n"
            "• Detailed evacuation plan for 16-million-passenger terminal\n"
            "• Corrective measure recommendations for full compliance"
        ),
        "fun_facts": (
            "• Tocumen International Airport is Latin America's largest hub, designed by the world-renowned Foster + Partners — making 1PAX's independent review role a particularly high-profile advisory assignment.\n"
            "• The project required deep expertise in NFPA 101 — the American life safety code — applied to a monumental 85,000 m² terminal serving 16 million passengers.\n"
            "• Panama City's Tocumen airport is the primary connecting hub for intercontinental travel between North/South America and Europe, making fire safety compliance a matter of global aviation importance."
        ),
    },

    "cusco_airport": {
        "display_name": "Alejandro Velasco Astete International Airport – Operational & Safety Diagnostic",
        "category": "Airports and Transportation",
        "location": "Cusco, Peru",
        "year": "2018",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "Not disclosed",
        "capacity": "1.2 million passengers",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Expert diagnostic assessment to evaluate operational performance and safety at a constrained high-altitude airport."
        ),
        "overview": (
            "In 2018, 1PAX was commissioned by Vinci Airports to carry out a comprehensive operational and "
            "safety diagnostic at Alejandro Velasco Astete International Airport in Cusco, Peru. The airport "
            "serves approximately 1.2 million passengers and operates under significant constraints given its "
            "location at high altitude in a historically sensitive urban environment. 1PAX's diagnostic "
            "assessed the airport's current operational capacity, passenger flow, safety conditions, and "
            "infrastructure performance, providing a detailed baseline to inform future improvement strategies "
            "and potential expansion planning. The assessment delivered a clear, evidence-based picture of "
            "existing conditions, enabling Vinci Airports to make informed decisions about investments and "
            "operational improvements at this unique and complex facility."
        ),
        "key_challenge": (
            "The airport operates under exceptional constraints: its location at high altitude in Cusco limits "
            "runway performance and aircraft capacity, while its urban context and proximity to UNESCO World "
            "Heritage sites impose strict limitations on expansion. The diagnostic had to account for these "
            "physical and regulatory constraints while providing actionable insights to improve safety and "
            "operational efficiency."
        ),
        "approach": (
            "1PAX conducted a systematic audit of the airport's infrastructure, operational flows, safety "
            "systems, and passenger experience, benchmarking findings against international standards and "
            "best practices. The diagnostic covered terminal and landside operations, airside safety conditions, "
            "and the interface between existing infrastructure and growing passenger demand, resulting in a "
            "structured set of recommendations tailored to the airport's unique context."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The diagnostic approach emphasised long-term operational sustainability by identifying inefficiencies "
            "and safety risks that, if unaddressed, could lead to costly interventions or incidents. By providing "
            "a clear baseline of existing conditions, the assessment supports informed, targeted investment — "
            "avoiding unnecessary construction while improving the airport's performance and resilience within "
            "its constrained high-altitude environment."
        ),
        "status": "Diagnostic completed — 2018",
        "tender_result": "Direct commission by Vinci Airports",
        "scope": "Comprehensive operational and safety diagnostic — terminal, landside, airside, passenger flow, safety systems, and infrastructure performance assessment",
        "program": (
            "• Terminal and landside operations audit\n"
            "• Airside safety conditions assessment\n"
            "• Passenger flow and infrastructure performance benchmarking\n"
            "• Safety systems evaluation\n"
            "• Structured recommendations tailored to high-altitude, heritage-constrained context"
        ),
        "fun_facts": (
            "• Alejandro Velasco Astete Airport is one of the world's highest commercial airports — operating at over 3,300 metres above sea level, which significantly affects aircraft performance and runway capacity.\n"
            "• The airport sits within UNESCO World Heritage territory — Cusco is the historic capital of the Inca Empire — imposing strict constraints on any potential expansion.\n"
            "• Despite serving only 1.2 million passengers, Cusco airport handles some of the most complex flight operations in South America due to its altitude, terrain, and limited runway geometry."
        ),
    },

    "jaipur_airport": {
        "display_name": "Jaipur International Airport – Feasibility Studies & Terminal Strategy",
        "category": "Airports and Transportation",
        "location": "Jaipur, Rajasthan, India",
        "year": "2018–2020",
        "client": "Airport Authority of India",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "13,740 m²",
        "capacity": "Not disclosed",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Integrated feasibility studies and terminal strategy for India's Pink City gateway."
        ),
        "overview": (
            "Between April 2018 and April 2020, 1PAX was commissioned by the Airport Authority of India to "
            "conduct feasibility studies and develop a terminal strategy for Jaipur International Airport. "
            "The scope encompassed Terminals 1, 2, and 3, addressing a combined area of approximately "
            "13,740 m². 1PAX's work provided a comprehensive assessment of the airport's existing facilities "
            "and future development potential, proposing a phased strategy for terminal improvement and "
            "capacity growth. The studies delivered a clear framework for the airport authority to plan and "
            "prioritise investments, supporting Jaipur's ambition to grow as a key regional gateway serving "
            "Rajasthan's tourism-driven economy and broader connectivity needs."
        ),
        "key_challenge": (
            "The challenge was to develop a coherent and financially viable multi-terminal strategy for an "
            "airport serving a rapidly growing city with significant tourism demand. The feasibility studies "
            "needed to address the interdependencies between three terminal buildings of varying age and "
            "condition, proposing an integrated approach that maximises capacity and efficiency within "
            "realistic investment parameters."
        ),
        "approach": (
            "1PAX conducted detailed feasibility assessments of all three terminal buildings, evaluating "
            "their structural condition, operational performance, and growth potential. The studies produced "
            "a phased development strategy that sequenced improvements and expansions across Terminals 1, 2, "
            "and 3, ensuring continuity of operations while progressively enhancing capacity, passenger "
            "experience, and operational efficiency."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The phased approach developed through the feasibility studies supports sustainable investment "
            "planning by prioritising the reuse and improvement of existing terminal infrastructure ahead of "
            "new construction. This strategy minimises embodied carbon and maximises the return on existing "
            "assets, while aligning with long-term operational and environmental performance goals for "
            "Jaipur International Airport."
        ),
        "status": "Study completed — 2018–2020",
        "tender_result": "Direct commission by Airport Authority of India",
        "scope": "Feasibility studies and terminal strategy — assessment and phased development roadmap for Terminals 1, 2, and 3 (combined 13,740 m²)",
        "program": (
            "• Structural condition and operational performance assessment of Terminals 1, 2, and 3\n"
            "• Phased development strategy sequencing improvements across all three terminals\n"
            "• Capacity and growth potential analysis\n"
            "• Recommendations for investment prioritisation and operational continuity"
        ),
        "fun_facts": (
            "• Jaipur is India's 'Pink City' — a UNESCO World Heritage Site and one of Rajasthan's primary tourism destinations, driving significant air traffic growth.\n"
            "• The project involved assessing three separate terminal buildings of different ages and conditions simultaneously — a complex multi-asset feasibility challenge.\n"
            "• 1PAX was commissioned directly by the Airport Authority of India — a significant recognition of expertise in one of the world's fastest-growing aviation markets."
        ),
    },

    "ahmedabad_airport": {
        "display_name": "Ahmedabad Airport – Feasibility Studies & Territorial Strategy",
        "category": "Airports and Transportation",
        "location": "Ahmedabad, India",
        "year": "2017",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "Not disclosed",
        "capacity": "35 million passengers per year",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "A strategic framework to unlock runway and terminal capacity while securing "
            "long-term operational resilience for one of India's fastest-growing aviation hubs."
        ),
        "overview": (
            "Commissioned by Vinci Airports in 2017, 1PAX carried out a comprehensive feasibility study "
            "and territorial strategy for Ahmedabad Airport, addressing existing and future terminal operations "
            "and airside infrastructure. The study assessed airport capacity within a broader mobility and "
            "territorial context, aligned with projected growth to 35 million passengers per year. The "
            "feasibility work covered Terminals 1, 2, and 3, providing a clear, actionable roadmap to "
            "mitigate congestion risks and optimise runway capacity over time. By strengthening airside "
            "efficiency and anticipating long-term growth, the project supported safer operations, improved "
            "punctuality, and enhanced passenger experience, reinforcing Ahmedabad Airport's role as a key "
            "regional gateway aligned with sustainable, future-ready mobility principles."
        ),
        "key_challenge": (
            "The primary challenge was addressing forecasted congestion risks linked to runway operations. "
            "With the majority of takeoffs and landings concentrated on a single runway configuration, the "
            "Airport Authority of India identified the need to extend the parallel taxiway system to safeguard "
            "operational efficiency in both the short and long term — without disrupting ongoing airport "
            "activity or compromising safety standards."
        ),
        "approach": (
            "1PAX conducted an in-depth analysis of runway capacity and airside operations, considering "
            "existing configurations, traffic forecasts, and operational patterns. Particular attention was "
            "given to the design and positioning of rapid exit taxiways, the performance of Instrument "
            "Landing System (ILS) equipment, and the interface between runway movements and terminal "
            "operations. The study established a phased strategy for extending the parallel taxiway, ensuring "
            "smoother aircraft circulation, reduced runway occupancy times, and improved resilience under "
            "peak demand scenarios. The approach balanced technical precision with a territorial vision, "
            "positioning airside upgrades as a catalyst for overall airport performance and future terminal "
            "development."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The territorial strategy embedded sustainability through a focus on operational efficiency and "
            "capacity optimisation rather than new construction. By improving taxiway systems and airside "
            "circulation, the study supports reduced aircraft ground movements, shorter runway occupancy "
            "times, and lower fuel burn and emissions per operation — delivering environmental and "
            "economic benefits aligned with long-term sustainable aviation goals."
        ),
        "status": "Study completed — 2017",
        "tender_result": "Direct commission by Vinci Airports",
        "scope": "Feasibility study and territorial strategy — runway capacity analysis, taxiway extension planning, and terminal operations assessment for Ahmedabad Airport",
        "program": (
            "• Runway capacity analysis and congestion risk assessment\n"
            "• Rapid exit taxiway design and positioning study\n"
            "• Instrument Landing System (ILS) performance evaluation\n"
            "• Parallel taxiway extension phasing strategy\n"
            "• Terminal 1, 2, and 3 operations review"
        ),
        "fun_facts": (
            "• Ahmedabad is one of India's fastest-growing metropolitan areas — home to major industrial and technology sectors — driving aviation demand that is quickly outpacing current runway capacity.\n"
            "• The study's key focus on taxiway geometry reflects a subtle but critical insight: most runway capacity constraints at busy airports are caused by inefficient ground movement, not runway length.\n"
            "• At a projected 35 million passengers per year, Ahmedabad Airport would rank among India's top five busiest airports — making 1PAX's strategic study a contribution to a nationally significant infrastructure debate."
        ),
    },

    "pachacamac_metro_station": {
        "display_name": "Intermodal Metro Station Pachacámac – Lima Metro Line 1 Extension",
        "category": "Future of Mobility",
        "location": "Lima, Peru",
        "year": "2018–2019",
        "client": "ATU (Autoridad de Transporte Urbano)",
        "architect": "1PAX",
        "partners": "Ing. Fabiola Espinoza",
        "area": "3,900 m²",
        "capacity": "5,000 passengers per hour",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "A multimodal gateway where contemporary mobility meets Peru's cultural and urban heritage."
        ),
        "overview": (
            "Between 2018 and 2019, 1PAX was commissioned by ATU to develop the functional programme and "
            "lead the architectural design of the Pachacámac Multimodal Station as part of the extension of "
            "Lima Metro Line 1. Conceived as a reference model for future metro stations in Peru, the project "
            "combines transport infrastructure with urban and cultural ambitions, serving a capacity of up to "
            "5,000 passengers per hour across a 3,900 m² facility. The Pachacámac Multimodal Station goes "
            "beyond its role as a transport hub to become a civic and cultural landmark. By integrating "
            "mobility, public space, and heritage, the project strengthens connectivity while enriching "
            "community life, establishing a scalable and context-sensitive model for future metro stations "
            "in Peru."
        ),
        "key_challenge": (
            "The primary challenge was to design an intermodal station capable of efficiently managing "
            "complex mobility flows while embedding the project within a highly sensitive cultural and urban "
            "context. The station needed to respond to Peru's specific mobility patterns, integrate multiple "
            "transport modes, and act as a catalyst for public life — while respecting its proximity to the "
            "Pachacámac Archaeological Sanctuary and major cultural institutions including the Site Museum "
            "and the National Museum of Peru (MUNA)."
        ),
        "approach": (
            "1PAX developed a comprehensive functional programme structured around intermodality, clarity of "
            "circulation, and urban integration. The station architecture is conceived as an elevated, legible "
            "system that organises connections between metro services, buses, taxis, and pedestrian networks. "
            "Beyond transport efficiency, the design incorporates principles of urban planning to create a "
            "vibrant public space that encourages social interaction, new activities, and recreational uses. "
            "The architectural language bridges modern infrastructure with cultural continuity, acknowledging "
            "the historical and symbolic significance of the Pachacámac site."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Pachacámac station promotes sustainable urban mobility by consolidating multiple transport "
            "modes — metro, bus, taxi, and pedestrian — into a single, efficient interchange. By reducing "
            "private car dependency and improving public transport connectivity, the station supports Lima's "
            "long-term mobility and environmental goals. Its integration with cultural and public spaces "
            "further encourages walking and non-motorised movement in the surrounding urban fabric."
        ),
        "status": "Design completed — 2018–2019",
        "tender_result": "Direct commission by ATU (Autoridad de Transporte Urbano)",
        "scope": "Functional programme definition and architectural design for 3,900 m² multimodal metro station — Pachacámac extension of Lima Metro Line 1",
        "program": (
            "• Intermodal station architecture — 3,900 m²\n"
            "• Metro connections integrated with bus, taxi, and pedestrian networks\n"
            "• Elevated platform as main distribution level with clearly separated vertical connections\n"
            "• Public space design encouraging social interaction and cultural programming\n"
            "• Cultural continuity with Pachacámac Archaeological Sanctuary and MUNA (National Museum of Peru)"
        ),
        "fun_facts": (
            "• The Pachacámac station sits adjacent to one of Peru's most important archaeological sites — the Pachacámac sanctuary, a pre-Inca ceremonial city that predates the Inca Empire by over 1,000 years.\n"
            "• The station was conceived as a 'reference model' for future metro stations in Peru — making it a design benchmark, not just a transport node.\n"
            "• At 5,000 passengers per hour, the station is designed to serve one of Lima's densest commuter corridors, linking southern suburbs directly to the city's electric metro backbone."
        ),
    },

    "belgrade_metro_line1": {
        "display_name": "Belgrade Metro Network – Line 1 Phase 1 Architectural Design",
        "category": "Future of Mobility",
        "location": "Belgrade, Serbia",
        "year": "2022",
        "client": "City of Belgrade",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "Not disclosed",
        "capacity": "Not disclosed",
        "cost": "Not disclosed",
        "video_url": "https://vimeo.com/1166382133/b6ff4ec0cc?share=copy&fl=sv&fe=ci",
        "tagline": (
            "A metro architecture that expresses a bright future while rooting mobility in "
            "Serbian culture and identity."
        ),
        "overview": (
            "In 2022, 1PAX was commissioned by the City of Belgrade to develop the architectural design for "
            "Phase 1 of Line 1 of the Belgrade Metro Network. The project establishes a unifying architectural "
            "and experiential framework for a new metropolitan transport system, positioning the metro not only "
            "as infrastructure, but as a cultural and civic space shaping everyday urban life. The project "
            "delivers a human-centered and culturally grounded architectural framework for Belgrade's first "
            "metro line. By combining contemporary design with national identity, the proposal creates "
            "memorable, welcoming stations that reinforce civic pride and everyday usability — a sustainable, "
            "interconnected metro system that supports Belgrade's future growth while offering passengers a "
            "comfortable, meaningful, and distinctly local travel experience."
        ),
        "key_challenge": (
            "The challenge was to define a strong and coherent identity for a brand-new metro network while "
            "ensuring clarity, comfort, and long-term adaptability. The design needed to balance international "
            "standards for metro infrastructure with a clear expression of local culture, language, and "
            "symbolism — all while prioritising passenger experience and operational efficiency."
        ),
        "approach": (
            "1PAX developed the concept of the 'Golden Line,' using architecture, materials, lighting, and "
            "graphics to convey a sense of optimism and a forward-looking vision for Belgrade. Station designs "
            "emphasise Serbian cultural identity through the use of Cyrillic as the primary language, "
            "supported by Latin as a secondary system. Signage and signalling were conceived with contemporary "
            "elegance, subtly integrating traditional Serbian patterns into a modern visual language. Each "
            "station is designed as a distinct spatial experience while remaining part of a coherent network, "
            "ensuring intuitive wayfinding, comfort, and a strong sense of place."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Belgrade Metro Line 1 represents a fundamental shift toward sustainable urban mobility for "
            "one of Southeast Europe's largest cities. By providing a high-capacity, low-emission public "
            "transport alternative, the metro directly reduces road congestion and private car dependency. "
            "The architectural approach prioritises durable materials, long-term adaptability, and efficient "
            "spatial organisation to minimise lifecycle costs and environmental impact across the network."
        ),
        "status": "Design completed — 2022",
        "tender_result": "Direct commission by City of Belgrade",
        "scope": "Architectural design for Phase 1 of Belgrade Metro Line 1 — unified station identity, spatial concept, signage, and cultural design language across the full network",
        "program": (
            "• Architectural and experiential framework for Phase 1 stations of Belgrade Metro Line 1\n"
            "• 'Golden Line' identity concept — materials, lighting, and graphics conveying optimism\n"
            "• Cyrillic primary / Latin secondary signage and wayfinding system\n"
            "• Integration of traditional Serbian patterns in contemporary visual language\n"
            "• Station-by-station spatial design ensuring network coherence and individual character"
        ),
        "fun_facts": (
            "• Belgrade Metro Line 1 is Serbia's first metro system — a historic national infrastructure milestone for a capital city of nearly 2 million people.\n"
            "• The 'Golden Line' concept — evoking optimism and forward momentum — positions the metro as more than transport: it is a civic expression of Belgrade's ambitions.\n"
            "• Cyrillic script was placed as the primary signage language — a deliberate affirmation of Serbian cultural identity in a city where Latin and Cyrillic have long coexisted."
        ),
    },

    "cergy_vertiport": {
        "display_name": "First European Taxidrone Vertiport – Cergy-Pontoise",
        "category": "Future of Mobility",
        "location": "Cergy-Pontoise, France",
        "year": "2022",
        "client": "Skyports Infrastructure / Groupe ADP",
        "architect": "1PAX",
        "partners": "Atelier des Fluides, Copilot",
        "area": "120 m²",
        "capacity": "Not disclosed",
        "cost": "500,000 €",
        "video_url": "https://vimeo.com/1166385052/772042ae19?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Delivering Europe's first fully operational vertiport as a catalyst for advanced air mobility."
        ),
        "overview": (
            "Completed in 2022, the First European Taxidrone Vertiport marks a major milestone in the "
            "development of Advanced Air Mobility (AAM) in Europe. Commissioned by Skyports Infrastructure "
            "in partnership with Groupe ADP, and architecturally designed by 1PAX with Atelier des Fluides "
            "and Copilot as partners, the 120 m² facility is located approximately 40 km northwest of Paris. "
            "It serves as a full-scale operational testbed for next-generation air mobility systems. The "
            "Cergy-Pontoise vertiport stands as the first fully functional and operational vertiport in "
            "Europe. By delivering a compact, efficient, and forward-looking architectural solution, 1PAX "
            "contributed to accelerating the deployment of urban air mobility while setting a benchmark for "
            "future vertiport design, positioning France and the Paris region at the forefront of innovation "
            "in next-generation aviation and sustainable mobility."
        ),
        "key_challenge": (
            "The challenge was to design a compact yet fully functional terminal capable of supporting "
            "real-world eVTOL operations, technology testing, and passenger experience validation. The "
            "vertiport needed to integrate emerging aviation standards, advanced technologies, and rapid "
            "passenger processing within a highly constrained footprint, while remaining adaptable to the "
            "fast-evolving Advanced Air Mobility ecosystem."
        ),
        "approach": (
            "1PAX conceived the vertiport as a highly efficient, technology-driven passenger interface. The "
            "architectural design prioritises clear spatial organisation and rapid flows, enabling flight "
            "turnaround times of less than 20 minutes. Advanced features such as facial recognition and door "
            "sensor technologies were integrated to streamline passenger processing and minimise waiting "
            "times. The facility supports a wide range of testing scenarios, including flight operations in "
            "collaboration with Thales, ground infrastructure validation, technology integration with "
            "partners such as SITA, and passenger experience trials. The architectural language is "
            "deliberately concise and modular, allowing the building to act as both an operational terminal "
            "and a demonstrator of future urban air mobility infrastructure."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Cergy-Pontoise vertiport is purpose-built to support the transition to sustainable aviation. "
            "By providing operational infrastructure for electric Vertical Take-Off and Landing (eVTOL) "
            "aircraft, the facility directly enables zero-emission urban air mobility. The compact 120 m² "
            "footprint minimises land use, while the modular design allows the facility to be adapted or "
            "replicated efficiently across future vertiport networks — reducing embodied carbon through "
            "scalable, low-waste construction."
        ),
        "status": "Built — completed and operational 2022",
        "tender_result": "Direct commission by Skyports Infrastructure in partnership with Groupe ADP",
        "scope": "Architectural design — Europe's first fully operational vertiport, 120 m², for eVTOL testing and Advanced Air Mobility operations",
        "program": (
            "• Compact 120 m² vertiport terminal — passenger processing and eVTOL operations interface\n"
            "• Facial recognition and door sensor technology integration\n"
            "• Flight operations testing infrastructure (in collaboration with Thales)\n"
            "• Ground infrastructure validation facilities\n"
            "• Technology integration with SITA and other AAM ecosystem partners\n"
            "• Passenger experience trial environment"
        ),
        "fun_facts": (
            "• The Cergy-Pontoise vertiport is the first fully operational vertiport in Europe — a genuine historic first in the history of aviation infrastructure.\n"
            "• Flight turnaround time was designed to be under 20 minutes — faster than most conventional helicopter operations, demonstrating the efficiency ambitions of Advanced Air Mobility.\n"
            "• Located just 40 km northwest of Paris, the facility is part of the broader Groupe ADP ecosystem preparing the Paris region for urban air mobility — including potential use for the Paris 2024 Olympics and beyond."
        ),
    },

    "singapore_vertiport": {
        "display_name": "VoloPort Vertiport – Singapore Competition",
        "category": "Future of Mobility",
        "location": "Singapore",
        "year": "2021–2022",
        "client": "Skyports",
        "architect": "1PAX",
        "partners": "Surbana Jurong",
        "area": "450 m²",
        "capacity": "Not disclosed",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Envisioning a human-centered gateway for urban air mobility in one of the world's most "
            "forward-looking cities."
        ),
        "overview": (
            "Between 2021 and 2022, 1PAX participated in the international competition for Singapore's first "
            "vertiport, the VoloPort, commissioned by Skyports in collaboration with Surbana Jurong. The "
            "project explored the architectural and operational foundations of a new generation of aviation "
            "infrastructure conceived to support the emergence of urban air mobility (UAM). 1PAX was awarded "
            "second prize, ranking ahead of proposals from eleven international architectural firms, "
            "reinforcing the studio's expertise in future mobility environments. The proposal delivered a "
            "clear, future-ready vision for vertiport architecture in Singapore, positioning the VoloPort as "
            "both an operational prototype and a public-facing ambassador for air taxi services."
        ),
        "key_challenge": (
            "The competition required envisioning an entirely new building typology — one that balances "
            "advanced aviation technology with public accessibility, regulatory readiness, and a clear "
            "passenger experience. Beyond technical feasibility, the vertiport needed to act as a "
            "demonstrator: a physical and experiential preview capable of building trust, understanding, and "
            "excitement around air taxi services in a dense urban context."
        ),
        "approach": (
            "1PAX conceived the VoloPort as a compact, highly legible showroom for urban air mobility. The "
            "design focused on clarity of movement, intuitive passenger flows, and a strong architectural "
            "identity that communicates safety, innovation, and accessibility. Infrastructure, operations, "
            "and user experience were developed as a single integrated system, anticipating scalability "
            "across multiple locations and routes identified by Skyports and Volocopter. The proposal "
            "acknowledged that successful UAM deployment depends on the convergence of three pillars: "
            "advanced aircraft technology, well-designed and adaptable infrastructure, and a robust "
            "regulatory framework."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The VoloPort Singapore competition entry was designed to champion sustainable urban mobility. "
            "By enabling electric air taxi operations in one of Asia's densest urban environments, the "
            "vertiport concept supports a shift away from fossil-fuel-based ground transport. The compact, "
            "adaptable 450 m² design was conceived for replicability across Singapore's urban network, "
            "minimising construction impact while maximising connectivity gains from zero-emission "
            "aerial mobility."
        ),
        "status": "Competition entry — 2nd Prize (2021–2022)",
        "tender_result": "Winner of international competition — 2nd Prize (ranked ahead of 11 international architectural firms)",
        "scope": "Competition design — 450 m² vertiport for Singapore's first urban air mobility operation, combining architecture, passenger experience, and operational infrastructure",
        "program": (
            "• Compact 450 m² vertiport terminal with passenger processing zones\n"
            "• Showroom and demonstrator space for air taxi services\n"
            "• Clear circulation system with intuitive passenger flows\n"
            "• Scalable design conceived for replication across Singapore's urban network\n"
            "• Integration with Skyports and Volocopter operational routes and requirements"
        ),
        "fun_facts": (
            "• 1PAX finished second in the VoloPort Singapore competition ahead of 11 other international architectural firms — a major recognition of expertise in the emerging vertiport typology.\n"
            "• The VoloPort concept was conceived as a 'showroom for urban air mobility' — as much a communications and trust-building exercise as a piece of operational infrastructure.\n"
            "• Singapore is one of the world's most progressive urban air mobility test environments — with Volocopter conducting Asia's first crewed eVTOL test flight there in 2019."
        ),
    },

    "paris_heliport": {
        "display_name": "Paris Heliport – Reconfiguration of Issy-les-Moulineaux Heliport",
        "category": "Future of Mobility",
        "location": "Issy-les-Moulineaux, Paris, France",
        "year": "2024–2025 (Under Construction)",
        "client": "Groupe ADP",
        "architect": "1PAX",
        "partners": "Ingerop",
        "area": "2,450 m²",
        "capacity": "500,000 passengers annually",
        "cost": "7.5 million €",
        "video_url": "",
        "tagline": (
            "Transforming a historic heliport into a future-ready hub for vertical mobility "
            "through a unified, sustainable architectural vision."
        ),
        "overview": (
            "Between 2024 and 2025, 1PAX was commissioned by Groupe ADP to lead the architectural design "
            "for the reconfiguration and expansion of the Paris Heliport at Issy-les-Moulineaux. Currently "
            "under construction, the project encompasses a mixed-use building combining a traditional "
            "heliport, a next-generation vertiport for eVTOL operations, and a new helicopter hangar. "
            "Designed to accommodate up to 500,000 passengers annually, the project positions the heliport "
            "as a key node in Paris's evolving urban air mobility ecosystem. The design redefines the Paris "
            "Heliport as a contemporary, sustainable, and adaptable mobility hub, ready to support both "
            "current helicopter operations and future eVTOL services, with an architectural language "
            "anchored in timber, natural light, and environmental performance."
        ),
        "key_challenge": (
            "The challenge was to modernise a highly constrained and operationally sensitive site while "
            "integrating emerging eVTOL infrastructure alongside existing helicopter operations. The project "
            "needed to reconcile diverse technical requirements, improve spatial flows, and elevate the "
            "passenger and user experience, all while meeting ambitious environmental standards and "
            "reinforcing the heliport's identity within a dense urban context."
        ),
        "approach": (
            "1PAX developed an architectural strategy focused on clarity, cohesion, and sustainability. "
            "Spatial layouts were reorganised to improve operational efficiency and passenger flows across "
            "heliport, vertiport, and hangar functions. A strong emphasis was placed on natural light, "
            "material quality, and user comfort. Wood was established as the central material of the "
            "project, used consistently across public spaces, façades, and the hangar — bringing warmth "
            "and human scale to an otherwise technical environment, while creating a unified architectural "
            "language. The design integrates natural materials, optimised lighting, and environmental "
            "strategies aligned with HQE and BREEAM certification objectives."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability is central to the Issy-les-Moulineaux heliport reconfiguration. The design "
            "pursues both HQE and BREEAM certification, embedding high environmental performance into every "
            "aspect of the building. The dominant use of timber across public spaces, façades, and the "
            "hangar significantly reduces embodied carbon compared to conventional industrial construction. "
            "The integration of eVTOL infrastructure positions the facility as a catalyst for zero-emission "
            "urban air mobility in the Paris metropolitan region."
        ),
        "status": "Under construction (2024–2025)",
        "tender_result": "Direct commission by Groupe ADP",
        "scope": "Architectural design for heliport reconfiguration — 2,450 m² mixed-use building combining traditional heliport, eVTOL vertiport, and helicopter hangar",
        "program": (
            "• Traditional heliport operations zone\n"
            "• Next-generation eVTOL vertiport for electric air taxi operations\n"
            "• New helicopter hangar\n"
            "• Public spaces, façades, and hangar in dominant timber construction\n"
            "• HQE and BREEAM certification targets\n"
            "• Reorganized spatial flows for 500,000 passengers annually"
        ),
        "fun_facts": (
            "• Paris Heliport at Issy-les-Moulineaux is the busiest heliport in Europe — and one of the world's most strategically located, just 5 km from the Eiffel Tower.\n"
            "• The project combines two distinct aviation typologies under one roof — a traditional heliport and a next-generation eVTOL vertiport — making it a genuinely unique building typology in European aviation.\n"
            "• Timber was chosen as the dominant construction material — bringing warmth and sustainability to what is typically a purely industrial building category, and targeting both HQE and BREEAM dual certification."
        ),
    },

    "cabo_verde_airports": {
        "display_name": "Cabo Verde – Assistance for the Concession of Seven Airports",
        "category": "Airports and Transportation",
        "location": "Cabo Verde, Macaronesia",
        "year": "2019 (Concession) / 2025 (Phase 1B)",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "Not disclosed",
        "capacity": "Various (7 airports across the archipelago)",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Defining a strategic, multi-airport vision to strengthen connectivity and support "
            "sustainable island development."
        ),
        "overview": (
            "In 2019, 1PAX supported Vinci Airports in the successful concession process for the management "
            "and development of seven airports across the Cabo Verde archipelago: Sal, Santiago, Boa Vista, "
            "São Vicente, Fogo, São Nicolau, and Maio. The assignment focused on the preparation of "
            "technical documentation for the concession and extended into Phase 1B planning in 2025. The "
            "network includes both international and domestic airports, each embedded within distinct "
            "geographic, economic, and tourism-driven contexts. The project provided Vinci Airports with "
            "a robust, structured foundation for the successful concession of Cabo Verde's airport network, "
            "supporting improved safety, enhanced passenger experience, and sustainable growth across "
            "seven islands."
        ),
        "key_challenge": (
            "The primary challenge lay in addressing the diversity and dispersion of the airport network "
            "while ensuring a coherent, long-term vision. Each airport presents unique operational "
            "conditions — ranging from proximity to beaches and tourism resorts to constraints linked to "
            "visibility, instrument flight procedures, and airspace management. The strategy needed to "
            "enhance safety, capacity, and passenger experience while remaining adaptable to the specific "
            "realities of each island."
        ),
        "approach": (
            "1PAX contributed to comprehensive technical documentation supporting the concession process, "
            "combining strategic analysis with architectural and planning expertise. For each airport, the "
            "team proposed a preliminary masterplan tailored to local conditions, addressing capacity "
            "assessment, operational constraints, and phased development scenarios. The approach emphasised "
            "scalability, resilience, and clarity, ensuring investments could be aligned with traffic "
            "evolution and tourism growth while improving connectivity across the archipelago."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The multi-airport concession strategy for Cabo Verde embeds sustainability at territorial "
            "scale. By developing a phased, coordinated masterplan for seven island airports, 1PAX helped "
            "avoid fragmented and wasteful investment. The approach prioritises the optimisation and "
            "progressive improvement of existing infrastructure, supporting efficient resource use across "
            "the archipelago while strengthening the islands' connectivity and long-term economic resilience."
        ),
        "status": "Concession support — design proposal delivered 2019; Phase 1B planning ongoing to 2025",
        "tender_result": "Concession support — won (2019), supporting Vinci Airports' successful bid for all seven Cabo Verde airports",
        "scope": "Technical documentation and preliminary masterplanning for seven island airports across the Cabo Verde archipelago — Sal, Santiago, Boa Vista, São Vicente, Fogo, São Nicolau, and Maio",
        "program": (
            "• Strategic analysis and preliminary masterplan for each of the seven airports\n"
            "• Capacity assessment and operational constraints study per airport\n"
            "• Phased development scenarios tailored to local conditions and traffic evolution\n"
            "• Technical concession documentation for the full seven-airport network\n"
            "• Phase 1B development planning (2025)"
        ),
        "fun_facts": (
            "• Cabo Verde's seven-airport concession is one of the world's few examples of a single team masterplanning an entire nation's commercial aviation network simultaneously.\n"
            "• The archipelago spans 10 inhabited islands across 4,000 km² of Atlantic Ocean — making inter-island air connectivity a national infrastructure necessity, not a luxury.\n"
            "• Vinci Airports won the concession in 2019, managing airports from a tiny Maio Island domestic strip to the major international gateway at Sal — an extraordinary range of aviation typologies within one national network."
        ),
    },

    "belgrade_nikola_tesla_landside": {
        "display_name": "Nikola Tesla Airport – Landside Design & Vehicle Simulation",
        "category": "Airports and Transportation",
        "location": "Belgrade, Serbia",
        "year": "2021–2025",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "SYSTRA",
        "area": "40,000 m²",
        "capacity": "20 million passengers (2043 target)",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Structuring a future-ready landside system that balances capacity growth, "
            "multimodal efficiency, and passenger clarity."
        ),
        "overview": (
            "From 2021 to 2025, 1PAX has been commissioned by Vinci Airports, the concessionaire of "
            "Belgrade's Nikola Tesla Airport, to design the landside architecture for the airport's "
            "expansion. In collaboration with SYSTRA, the scope includes the functional, architectural, "
            "and landscape design of access roads, kerbside areas, and car parks across two development "
            "phases. The project supports a long-term growth vision anticipating a capacity of 20 million "
            "passengers by 2043. The result is a robust, scalable landside framework that improves "
            "day-to-day operational efficiency and strengthens Nikola Tesla Airport's role as a modern, "
            "well-organised gateway aligned with Vinci Airports' standards."
        ),
        "key_challenge": (
            "The principal challenge was to accommodate significant future traffic growth while maintaining "
            "operational clarity, safety, and a high-quality passenger experience. The landside system "
            "needed to integrate seamlessly with the existing terminal, separate arrival and departure "
            "flows, and manage diverse vehicle types — from public transport and taxis to private drop-off "
            "and pick-up — within a constrained footprint."
        ),
        "approach": (
            "1PAX developed a two-level kerbside strategy clearly separating departures and arrivals. "
            "The upper level aligns with the existing terminal for departing passengers, while the lower "
            "level was reconfigured to accommodate larger transport vehicles and improve accessibility. "
            "Design assumptions were supported by detailed vehicle simulations based on a dual carriageway "
            "kerbside approximately 25 metres wide. Lanes closest to the terminal façade were dedicated to "
            "public transport — buses and taxis — prioritising collective mobility. Outer lanes were "
            "assigned to Kiss & Fly drop-off and pick-up functions. Landscape design was integrated to "
            "enhance legibility, comfort, and the overall perception of the landside environment."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The landside design prioritises sustainable mobility by dedicating the closest kerbside lanes "
            "to public transport ahead of private vehicles, actively encouraging modal shift. The integrated "
            "landscape strategy introduces greenery and shading to improve microclimate conditions and "
            "passenger comfort. Vehicle simulation tools were used to right-size infrastructure, avoiding "
            "overbuilding and reducing embodied carbon in road and car park construction."
        ),
        "status": "Design ongoing (2021–2025)",
        "tender_result": "Direct commission by Vinci Airports (concessionaire of Belgrade Nikola Tesla Airport)",
        "scope": "Functional, architectural, and landscape design of landside areas — access roads, kerbside, and car parks across two development phases supporting 20 million passengers by 2043",
        "program": (
            "• Two-level kerbside design — upper level for departures, lower level for larger transport vehicles\n"
            "• Dedicated inner lanes for public transport (buses and taxis)\n"
            "• Kiss & Fly outer lanes for drop-off and pick-up\n"
            "• Integrated landscape design across kerbside and car park areas\n"
            "• Vehicle simulation-based design validation (dual carriageway ~25 m wide)\n"
            "• Phased delivery strategy supporting long-term growth to 20 million passengers"
        ),
        "fun_facts": (
            "• The landside design is built around detailed vehicle simulations — ensuring the kerbside system can handle peak loads without becoming a bottleneck, even as the airport scales toward 20 million passengers.\n"
            "• By placing public transport lanes closest to the terminal façade, the design actively rewards sustainable travel choices — a meaningful policy decision embedded directly into the architecture.\n"
            "• The project runs in parallel with Belgrade Airport's major terminal expansion (also led by 1PAX) — making 1PAX the lead architect for both airside and landside transformation at Serbia's main international gateway."
        ),
    },

    "lima_metro_line1_stations": {
        "display_name": "Lima Metro Line 1 – Multimodal Station Sizing & Urban Insertion",
        "category": "Future of Mobility",
        "location": "Lima, Peru",
        "year": "2018–2019",
        "client": "AATE (Autonomous Authority for the Electric Train)",
        "architect": "1PAX",
        "partners": "Eng. Fabiola Espinoza",
        "area": "Not disclosed",
        "capacity": "Serving a catchment of 533,000 inhabitants",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Designing an intermodal gateway that connects mass transit with urban life "
            "and local mobility networks."
        ),
        "overview": (
            "Between 2018 and 2019, 1PAX was appointed as a consultant by AATE to support the extension "
            "of Lima Metro Line 1 through the definition and sizing of three new stations. The commission "
            "focused on urban integration, mobility analysis, and intermodality, with particular emphasis "
            "on the University Station — later renamed Pachacamac — conceived as a key multimodal hub "
            "serving a catchment of over 533,000 inhabitants. The project delivered a robust framework for "
            "new metro stations that respond to both transport performance and urban quality, contributing "
            "to strengthening Lima Metro Line 1 as a backbone of metropolitan mobility."
        ),
        "key_challenge": (
            "The extension of Line 1 required stations capable of absorbing complex and intense mobility "
            "flows in a dense metropolitan context. The challenge was to accurately size infrastructure "
            "and organise multiple transport modes — public transport, informal mobility, and pedestrians "
            "— while ensuring safe, efficient, and legible urban insertion. The Pachacamac station needed "
            "to function as a true intermodal node for over half a million daily commuters."
        ),
        "approach": (
            "1PAX carried out a detailed urban and mobility analysis, including traffic flows and sizing "
            "requirements for different vehicle types. Based on this diagnostic, the team developed an "
            "intermodality programme for the Pachacamac station. The design strategy is structured around "
            "an elevated platform acting as the main distribution level, with vertical connections clearly "
            "separating access to buses, taxis, motorcycle taxis, bicycle parking, and pedestrian areas — "
            "improving safety, legibility, and operational efficiency while integrating into the "
            "surrounding urban fabric."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Lima Metro Line 1 station study directly supports sustainable urban mobility by expanding "
            "Lima's electric metro network into underserved areas. The multimodal design integrates cycling, "
            "walking, and public transport connections — encouraging low-carbon movement for over 533,000 "
            "inhabitants. The elevated platform strategy efficiently organises diverse transport modes "
            "within a compact urban footprint, minimising land consumption while maximising connectivity."
        ),
        "status": "Study completed — 2018–2019",
        "tender_result": "Direct commission by AATE (Autonomous Authority for the Electric Train)",
        "scope": "Mobility consultancy and station sizing — definition of three new stations and intermodality programme for Lima Metro Line 1 extension, with focus on Pachacamac multimodal hub",
        "program": (
            "• Urban and mobility analysis for three new metro station locations\n"
            "• Traffic flow sizing for buses, taxis, motorcycle taxis, bicycles, and pedestrians\n"
            "• Intermodality programme for Pachacamac station (serving 533,000+ inhabitants catchment)\n"
            "• Elevated platform design as main distribution level\n"
            "• Vertical connections separating all transport modes for safety and legibility"
        ),
        "fun_facts": (
            "• Lima is one of Latin America's largest megacities, with over 10 million people in the metropolitan area — yet its public transport network remains one of the most under-resourced for a city of its scale.\n"
            "• The Pachacamac extension serves a catchment of over 533,000 inhabitants — nearly half a million people whose daily mobility would be transformed by a single metro station.\n"
            "• 1PAX worked on both the Lima Metro Line 1 station strategy (this project) and the Pachacamac Multimodal Station architectural design (separate project) — giving a uniquely integrated view of the extension."
        ),
    },

    "cayenne_airport_masterplan": {
        "display_name": "Félix Eboué Cayenne Airport – Masterplan",
        "category": "Airports and Transportation",
        "location": "French Guiana",
        "year": "2023",
        "client": "EDEIS COLAS",
        "architect": "1PAX",
        "partners": "Ingerop",
        "area": "25,000 m²",
        "capacity": "Not disclosed",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "A strategic masterplan to enhance passenger experience, strengthen safety, "
            "and unlock long-term airport and territorial development."
        ),
        "overview": (
            "In 2023, 1PAX was commissioned by EDEIS COLAS to develop a comprehensive masterplan for "
            "Félix Eboué Cayenne Airport, in collaboration with Ingerop. The study addressed the airport "
            "as both an operational infrastructure and a driver of regional development, with the objective "
            "of improving passenger experience while increasing security levels and expanding aircraft apron "
            "capacity. The masterplan provides a structured, long-term vision to guide phased development "
            "and coordinated decision-making, positioning the airport as a resilient, multifunctional "
            "platform serving regional mobility and broader territorial development objectives in "
            "French Guiana."
        ),
        "key_challenge": (
            "The airport faced multiple, interrelated challenges: limited operational capacity on the apron, "
            "safety concerns linked to the proximity of sensitive functions, and growing pressure to "
            "accommodate new aviation and non-aviation activities. Any intervention needed to improve "
            "performance without disrupting existing services, while anticipating future growth and "
            "diversification of the airport's role within the region."
        ),
        "approach": (
            "Following an extensive diagnostic and spatial analysis, 1PAX developed a masterplan that "
            "reorganises key airport functions to improve safety, efficiency, and clarity. The strategy "
            "included proposals for new hangars to increase capacity without impacting existing parking "
            "services, the relocation of Air Guyane facilities and the fuel depot to enhance safety and "
            "operational logic, expanded cargo parking areas to support logistics growth, and an adjacent "
            "economic activity zone including complementary programmes such as a hotel and a business centre."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Cayenne Airport masterplan embeds sustainability through strategic reorganisation of "
            "existing infrastructure rather than unconstrained expansion. Relocating hazardous facilities "
            "such as the fuel depot improves safety and operational continuity. The development of an "
            "adjacent economic activity zone supports non-aeronautical revenue diversification, "
            "strengthening the airport's long-term financial and environmental resilience."
        ),
        "status": "Study completed — 2023",
        "tender_result": "Direct commission by EDEIS COLAS",
        "scope": "Comprehensive airport masterplan — strategic reorganization of airport functions, expansion of apron capacity, and economic activity zone planning for Félix Eboué Cayenne Airport",
        "program": (
            "• New hangars to increase apron capacity without impacting existing parking\n"
            "• Relocation of Air Guyane facilities for improved safety and operational logic\n"
            "• Relocation of fuel depot to enhance safety separation\n"
            "• Expanded cargo parking areas\n"
            "• Adjacent economic activity zone: hotel, business centre, and complementary programmes\n"
            "• Spatial and safety diagnostic as masterplan foundation"
        ),
        "fun_facts": (
            "• Félix Eboué Cayenne Airport is the primary gateway to French Guiana — a French overseas territory on the South American coast, home to the Guiana Space Centre, one of the world's most active rocket launch sites.\n"
            "• The masterplan proposes an economic activity zone adjacent to the airport — a hotel and business centre that would transform the airport precinct into a regional economic catalyst.\n"
            "• The relocation of the fuel depot — a hazardous facility — was a critical safety measure requiring careful operational planning to execute without disrupting active flight operations."
        ),
    },

    "doha_metro_depot": {
        "display_name": "Qatar Railways – Doha West Metro Depot Masterplan",
        "category": "Future of Mobility",
        "location": "Doha, Qatar",
        "year": "Not disclosed",
        "client": "SETEC BÂTIMENT / Siemens / BESIX / TSO",
        "architect": "1PAX (as 1M2) / Jean Luc Chapel",
        "partners": "Graciela Torre",
        "area": "157,217 m²",
        "capacity": "Not disclosed",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Transforming critical rail infrastructure into an efficient, human-centered urban oasis."
        ),
        "overview": (
            "The Doha West Metro Depot masterplan establishes a comprehensive framework for the operational "
            "heart of Qatar Railways, integrating depot and maintenance facilities, stabling yards, control "
            "and training centres, power and water plants, and parking within a single, coherent vision. "
            "The project goes beyond technical coordination, redefining large-scale infrastructure as an "
            "integral and articulated piece of the city. Anchored by its relationship to the Qatar Railways "
            "headquarters, the masterplan introduces landscaped public spaces conceived as an oasis — where "
            "operational performance and urban presence coexist. The project transforms complex rail "
            "operations into a coherent, future-ready system, enhancing operational efficiency and "
            "strengthening the institutional presence of Qatar Railways."
        ),
        "key_challenge": (
            "The primary challenge lay in orchestrating a vast and highly technical programme — defined by "
            "strict operational, security, and logistical requirements — while ensuring clarity of movement, "
            "long-term flexibility, and a dignified civic interface. The depot needed to function as a "
            "resilient and efficient backbone for the metro system, yet avoid becoming an isolated "
            "industrial enclave within the urban fabric."
        ),
        "approach": (
            "The masterplan is structured through a clear zoning logic that separates and optimises "
            "operational flows — trains, maintenance, staff, utilities, and visitors — while maintaining "
            "intuitive internal circulation. A layered landscape strategy mediates between heavy "
            "infrastructure and the city through shaded courtyards, planted buffers, and water-conscious "
            "design principles that introduce environmental comfort and reduce heat gain. The oasis concept "
            "becomes both environmental infrastructure and social connector. Rational, durable, and "
            "adaptable structures support evolving rail technologies while preserving operational efficiency."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "Sustainability and life-cycle thinking are embedded throughout the Doha Metro Depot "
            "masterplan. Shaded courtyards, planted buffers, and water-conscious landscape design directly "
            "address Qatar's extreme heat, reducing cooling energy demand and improving microclimate "
            "conditions. The oasis landscape integrates passive environmental strategies at building scale, "
            "while rational zoning and adaptable structures ensure the facility can evolve with future "
            "rail technologies without costly reconstruction."
        ),
        "status": "Design completed — year not disclosed",
        "tender_result": "Direct commission by SETEC BÂTIMENT / Siemens / BESIX / TSO",
        "scope": "Masterplan design for Qatar Railways Doha West Metro Depot — 157,217 m² integrating depot, maintenance, stabling, control, training, utilities, and landscape",
        "program": (
            "• Metro depot and maintenance facilities\n"
            "• Stabling yards for rolling stock\n"
            "• Control and training centres\n"
            "• Power and water plants\n"
            "• Parking and staff facilities\n"
            "• Oasis landscape — shaded courtyards, planted buffers, and water-conscious design\n"
            "• Qatar Railways Headquarters as civic anchor of the masterplan"
        ),
        "fun_facts": (
            "• At 157,217 m², the Doha West Metro Depot is one of the largest single infrastructure projects in 1PAX's portfolio — an entire operational city for Qatar's metro system.\n"
            "• The 'oasis' landscape concept — planted courtyards and water features in one of the world's hottest climates — transforms what is typically a purely industrial environment into a habitable, human-centered campus.\n"
            "• The project was delivered under the brand name '1M2' — an earlier identity of 1PAX, reflecting the studio's evolution and long track record in major infrastructure masterplanning."
        ),
    },

    "chateauroux_atct_mro": {
        "display_name": "Châteauroux Airport – Air Traffic Control Tower & MRO Development",
        "category": "Industrial Buildings",
        "location": "Châteauroux, Centre-Val de Loire, France",
        "year": "2020 (Built)",
        "client": "DGAC / Région Centre-Val de Loire",
        "architect": "Calvo Tran Van / 1PAX",
        "partners": "SETEC (engineering)",
        "area": "400 m²",
        "capacity": "Not applicable",
        "cost": "9 million €",
        "video_url": "",
        "tagline": (
            "A precise and elegant control tower design supporting the growth of a "
            "strategic aeronautical hub."
        ),
        "overview": (
            "Delivered in 2020, the Châteauroux ATCT & MRO project forms part of an ambitious initiative "
            "led by the Centre-Val de Loire Region to strengthen the aeronautical industry around "
            "Châteauroux Airport. The development includes the construction of a large multifunctional "
            "maintenance hangar and a new air traffic control tower, required to support expanded "
            "maintenance and operational activities. Awarded through a design competition to a "
            "multidisciplinary consortium led by Calvo Tran Van, 1PAX was responsible for the "
            "architectural design of the new control tower alongside SETEC for engineering. The completed "
            "control tower provides Châteauroux Airport with a reliable, future-ready operational asset "
            "supporting the region's strategic ambitions in aircraft maintenance and aeronautical services."
        ),
        "key_challenge": (
            "The introduction of a 10,000 m² maintenance hangar fundamentally altered the operational "
            "landscape of the airport, making a new control tower essential. The challenge was to design "
            "a highly technical air traffic control facility meeting stringent regulatory and operational "
            "requirements, while remaining compact, clear in expression, and well integrated into "
            "its surroundings."
        ),
        "approach": (
            "1PAX developed a control tower design defined by clarity, restraint, and efficiency. The "
            "architectural concept is based on a clean and simple core, ensuring optimal functionality "
            "for air traffic control operations while maintaining a calm and legible presence within the "
            "airport environment. The design balances technical rigor with architectural elegance, focusing "
            "on proportion, materiality, and integration rather than formal excess, ensuring full "
            "compliance with aviation standards while reinforcing the coherence of the overall MRO "
            "development."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Châteauroux control tower is designed with economy of means as a core sustainability "
            "principle — a compact 400 m² structure achieving maximum operational performance without "
            "material excess. The restrained architectural approach avoids unnecessary building volume, "
            "reducing embodied carbon and long-term energy consumption. The MRO cluster the tower supports "
            "extends the operational life of aircraft, contributing to more sustainable aviation through "
            "maintenance, repair, and overhaul services."
        ),
        "status": "Built — completed 2020",
        "tender_result": "Winner of design competition (as part of consortium led by Calvo Tran Van)",
        "scope": "Architectural design for new Air Traffic Control Tower — 400 m², forming part of MRO development at Châteauroux Airport",
        "program": (
            "• New air traffic control tower — 400 m²\n"
            "• Clean, compact architectural concept meeting strict DGAC regulatory requirements\n"
            "• Integration with broader 10,000 m² multifunctional MRO hangar development\n"
            "• Collaboration with SETEC for engineering and regulatory compliance"
        ),
        "fun_facts": (
            "• The Châteauroux control tower was necessitated by a brand-new 10,000 m² MRO hangar — a new obstruction that changed the visual sight lines from the existing tower, making a new one operationally mandatory.\n"
            "• At just 400 m² and 9 million €, the project demonstrates 1PAX's ability to deliver technically complex aviation infrastructure at modest scale with architectural precision.\n"
            "• Châteauroux Airport is one of France's leading cargo and MRO hubs — a specialist aviation node that operates largely out of public view but plays a critical role in European aircraft maintenance."
        ),
    },

    "riga_control_tower": {
        "display_name": "Riga International Airport – New Control Tower & Offices",
        "category": "Industrial Buildings",
        "location": "Riga, Latvia",
        "year": "2018 (Competition — 3rd Prize)",
        "client": "Riga International Airport (RIX)",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "4,600 m²",
        "capacity": "Supporting an airport of 7 million passengers annually",
        "cost": "9 million €",
        "video_url": "https://vimeo.com/1166382087/264a6d260f?share=copy&fl=sv&fe=ci",
        "tagline": (
            "A landmark tower that reconciles operational precision with landscape continuity "
            "and urban balance."
        ),
        "overview": (
            "In 2018, 1PAX was awarded third prize in the international competition for the new control "
            "tower and office complex at Riga International Airport (RIX). The project proposed a "
            "comprehensive architectural and territorial vision for a strategic infrastructure serving an "
            "airport with a capacity of 7 million passengers annually. Beyond the tower itself, the "
            "proposal addressed the broader airport landscape, positioning the building as a new visual "
            "and operational landmark. The third-prize recognition acknowledged its conceptual clarity, "
            "urban integration, and distinctive architectural identity combining technical rigor with "
            "spatial elegance and landscape sensitivity."
        ),
        "key_challenge": (
            "The challenge was to design a highly technical and secure facility while ensuring meaningful "
            "integration within its surrounding environment. The project needed to reconcile strict "
            "operational requirements of air traffic control with issues of landscape balance, mobility, "
            "parking, and the relationship between built and unbuilt areas, while asserting a strong "
            "identity without disrupting the existing airport fabric."
        ),
        "approach": (
            "1PAX developed a global vision in which architecture, landscape, and urbanism operate as "
            "a single system. The proposal rebalanced built and open spaces, integrating soft mobility "
            "connections alongside parking and service access. Architecturally, the design established "
            "continuity between the existing building and the new tower, treating the former as the "
            "starting point of the technical base. Existing alignments and rhythms were preserved, "
            "gradually transforming into contemporary architectural 'ribbons' — fluid forms that slide "
            "over a landscaped base before rising vertically to wrap the control cabin, creating a "
            "dynamic dialogue between the tower, the terrain, and the sky."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Riga control tower proposal integrates landscape and architecture into a unified system, "
            "using soft mobility infrastructure and vegetated bases to reduce impermeable surface area "
            "and manage stormwater on site. The fluid architectural forms were designed to minimise wind "
            "loads and structural material use. Reuse of existing building alignments reduces embodied "
            "carbon compared to entirely new-build approaches."
        ),
        "status": "Competition entry — 3rd Prize (2018)",
        "tender_result": "Winner of international competition — 3rd Prize",
        "scope": "Competition design — 4,600 m² air traffic control tower and office complex for Riga International Airport, integrating architecture, landscape, and urban vision",
        "program": (
            "• New air traffic control tower — iconic landmark design\n"
            "• Office complex integrated with existing terminal base\n"
            "• Soft mobility infrastructure and landscaped grounds\n"
            "• Parking and service access reorganization\n"
            "• Fluid 'ribbon' architectural forms rising from landscaped base to control cabin"
        ),
        "fun_facts": (
            "• 1PAX's Riga tower proposal features fluid architectural 'ribbons' that slide from the landscape to wrap the control cabin — a poetic, landscape-integrated approach to a typically technical building type.\n"
            "• The project addresses the entire airport ground level, not just the tower — rebalancing built and open spaces as a unified architectural and landscape system.\n"
            "• Riga International Airport is the largest airport in the Baltic states, handling over 7 million passengers annually — making the control tower a highly visible landmark for the entire Baltic region."
        ),
    },

    "belgrade_fire_station": {
        "display_name": "Belgrade Nikola Tesla Airport – Main Fire Station",
        "category": "Industrial Buildings",
        "location": "Belgrade, Serbia",
        "year": "2019",
        "client": "Vinci Airports Serbia / Belgrade Airport",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "1,811 m²",
        "capacity": "Not applicable",
        "cost": "10 million €",
        "video_url": "",
        "tagline": (
            "A high-performance emergency facility designed for speed, clarity, and operational readiness."
        ),
        "overview": (
            "In 2019, 1PAX was commissioned by Vinci Airports Serbia / Belgrade Airport to design the new "
            "Main Fire Station for Nikola Tesla Airport. The project comprises a purpose-built, two-storey "
            "facility accommodating offices and shared spaces for airport firefighters, conceived as a "
            "critical component of the airport's safety and emergency response infrastructure. The new "
            "Main Fire Station delivers a robust, efficient, and highly legible emergency facility "
            "strengthening Belgrade Airport's safety infrastructure and providing firefighters with a "
            "purpose-built environment that supports readiness, performance, and resilience."
        ),
        "key_challenge": (
            "The core challenge was to design a building enabling rapid reaction and seamless coordination "
            "in emergency situations, while clearly separating functions with distinct environmental and "
            "technical requirements. The fire station needed to combine robust operational efficiency, "
            "firefighter well-being, and long-term durability within a demanding airport context."
        ),
        "approach": (
            "1PAX organised the building into two clearly defined zones. The living and working areas "
            "were designed as a thermally insulated volume providing comfortable conditions for offices, "
            "rest spaces, and shared facilities. The fire truck hangar was conceived as a naturally "
            "ventilated space optimised for vehicle readiness and fast deployment. A carefully designed "
            "internal connection links the two zones while remaining isolated, ensuring both functional "
            "efficiency and environmental control. Circulation paths were developed to minimise response "
            "times, allowing firefighters to move swiftly from rest or work areas to operational positions."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Belgrade Fire Station's dual-zone strategy — a thermally insulated volume for occupied "
            "spaces and a naturally ventilated hangar for vehicles — is inherently energy-efficient. By "
            "separating environmental zones, the design avoids conditioning large volumes unnecessarily, "
            "reducing heating and cooling energy consumption. Robust, durable materials ensure a long "
            "service life and minimal maintenance requirements over the building's operational lifetime."
        ),
        "status": "Design completed — 2019",
        "tender_result": "Direct commission by Vinci Airports Serbia / Belgrade Airport",
        "scope": "Architectural design — 1,811 m² two-storey main fire station for Nikola Tesla Airport, including firefighter offices, shared spaces, and vehicle hangar",
        "program": (
            "• Thermally insulated offices and shared spaces for airport firefighters\n"
            "• Naturally ventilated fire truck hangar optimized for rapid deployment\n"
            "• Carefully designed internal connection isolating occupied zones from hangar environment\n"
            "• Circulation paths minimizing response times from rest to operational positions"
        ),
        "fun_facts": (
            "• The Belgrade Fire Station is one component of 1PAX's comprehensive work at Nikola Tesla Airport — alongside the terminal expansion, administration building, and landside design, giving 1PAX one of the broadest portfolios of any architect at a single airport.\n"
            "• Fire station design is a specialized discipline requiring deep understanding of emergency response workflows — 1PAX's dual-zone strategy (occupied vs. hangar) reflects this operational intelligence.\n"
            "• Belgrade's Nikola Tesla Airport, under Vinci Airports' concession, is undergoing one of Central Europe's most comprehensive airport transformation programs — with 1PAX at the center of nearly every major project."
        ),
    },

    "cdg_baggage_building": {
        "display_name": "Paris Charles de Gaulle Airport – Baggage Handling System Building",
        "category": "Industrial Buildings",
        "location": "Paris Charles de Gaulle Airport, France",
        "year": "2019 (Competition)",
        "client": "Groupe ADP",
        "architect": "1PAX",
        "partners": "BRIAND, Scoping",
        "area": "10,000 m²",
        "capacity": "Not applicable",
        "cost": "16 million €",
        "video_url": "",
        "tagline": (
            "A clear and robust industrial architecture supporting security, capacity, and "
            "operational visibility at a major European hub."
        ),
        "overview": (
            "In 2019, 1PAX participated in the design competition launched by Groupe ADP for the "
            "construction of a new industrial building at Paris Charles de Gaulle Airport, dedicated to "
            "housing a new baggage sorting system. Developed in partnership with general contractor BRIAND "
            "and Scoping within a design-and-build framework, the project addressed critical upgrades to "
            "CDG's baggage handling capacity and security infrastructure. The project delivered a robust "
            "and efficient architectural response balancing technical performance with clarity of form and "
            "visual identity, reinforcing the role of infrastructure buildings as active contributors to "
            "the airport's overall image."
        ),
        "key_challenge": (
            "The building needed to accommodate complex technical systems and stringent security controls "
            "while ensuring operational clarity and seamless integration within an active airside "
            "environment. The structure also had to remain clearly legible from airside zones including "
            "air traffic control perspectives, and contribute positively to the airport's architectural "
            "identity."
        ),
        "approach": (
            "1PAX proposed a simple, refined architectural geometry prioritising efficiency, "
            "constructability, and visual clarity. The layout was designed to support smooth installation "
            "and operation of the baggage sorting system while maintaining clear sightlines and a strong, "
            "recognisable presence within the airfield. The south façade was conceived as an expressive "
            "element integrating a green wall and a large ADP logo — combining functional industrial "
            "architecture with a visible commitment to environmental quality and corporate identity."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The CDG baggage building incorporates a green wall on its south façade as an integral "
            "environmental strategy, reducing solar heat gain, improving building insulation, and managing "
            "stormwater through evapotranspiration. The simple, efficient building geometry minimises "
            "material use and construction waste. The green wall also contributes to biodiversity on the "
            "airfield site and signals Groupe ADP's commitment to environmental quality within industrial "
            "airport infrastructure."
        ),
        "status": "Competition entry — 2019",
        "tender_result": "Competition entry for Groupe ADP — design-and-build framework",
        "scope": "Competition design — 10,000 m² industrial building for new baggage sorting system at Paris Charles de Gaulle Airport, in design-and-build partnership with BRIAND",
        "program": (
            "• 10,000 m² industrial building housing new baggage sorting and handling system\n"
            "• Stringent security controls and airside integration\n"
            "• South façade with green wall and integrated ADP corporate identity\n"
            "• Optimized sightlines from air traffic control perspectives\n"
            "• Simple, refined geometry for efficient constructability"
        ),
        "fun_facts": (
            "• Paris Charles de Gaulle is the world's 9th busiest airport and Europe's second largest hub — making this baggage building one of the most operationally critical industrial buildings in European aviation.\n"
            "• The green wall on the south façade doubles as a corporate identity billboard, incorporating a large ADP logo — demonstrating how industrial airport buildings can express brand commitment to environmental quality.\n"
            "• 1PAX partnered with general contractor BRIAND in a design-and-build framework — an integrated delivery approach that aligns architectural vision with construction cost and schedule from the outset."
        ),
    },

    "le_bourget_fire_station": {
        "display_name": "Paris–Le Bourget Airport – New Fire Station (SSLIA)",
        "category": "Industrial Buildings",
        "location": "Paris–Le Bourget, France",
        "year": "2020 (Competition)",
        "client": "Groupe ADP",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "2,500 m²",
        "capacity": "Not applicable",
        "cost": "10 million €",
        "video_url": "",
        "tagline": (
            "An operational, legible, and scalable architecture designed to embody safety, "
            "efficiency, and readiness."
        ),
        "overview": (
            "In 2020, 1PAX participated in the design competition launched by Groupe ADP for the new "
            "SSLIA fire station at Paris–Le Bourget Airport. Conceived as a critical piece of airport "
            "infrastructure, the project addressed the architectural and functional requirements of an "
            "operational emergency facility designed to support airport protection and ensure rapid "
            "response capabilities. The proposal delivered a strong, pragmatic architectural response "
            "aligned with the demanding requirements of airport fire services, demonstrating how "
            "disciplined architectural expression can enhance both performance and identity in critical "
            "infrastructure buildings."
        ),
        "key_challenge": (
            "The fire station needed to be highly functional, robust, and adaptable over time, while "
            "clearly expressing its role within the airport landscape. The challenge was to translate "
            "complex operational requirements — from emergency response to training and administration "
            "— into a clear, efficient, and immediately readable architectural composition."
        ),
        "approach": (
            "1PAX developed a composition of simple, clearly articulated volumes, each directly reflecting "
            "its function. The fire shed was conceived as the heart of the building, accommodating "
            "emergency vehicles and rapid deployment operations, emphasised through a bright, distinctive "
            "colour ensuring instant visibility. Supporting volumes were organised around this core: "
            "living spaces at the rear for rest and readiness, a second level for administrative "
            "functions, and an independent wing for training activities — ensuring operational efficiency, "
            "safety, and long-term flexibility."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Le Bourget fire station design prioritises long-term adaptability through its clearly "
            "zoned, functionally legible layout. The separation of living, operational, and training "
            "zones allows each to be independently serviced and upgraded, extending the building's useful "
            "life and reducing lifecycle costs. The scalable organisation ensures the facility can "
            "accommodate future changes in equipment or team size without requiring structural modification."
        ),
        "status": "Competition entry — 2020",
        "tender_result": "Competition entry for Groupe ADP",
        "scope": "Competition design — 2,500 m² SSLIA fire station at Paris–Le Bourget Airport, with emergency vehicle shed, living quarters, administrative level, and training wing",
        "program": (
            "• Fire vehicle shed (fire shed) as building's operational core — highly visible with distinctive colour\n"
            "• Living spaces at rear for rest and firefighter readiness\n"
            "• Administrative offices on second level\n"
            "• Independent training wing\n"
            "• Clearly articulated composition of volumes reflecting distinct functions"
        ),
        "fun_facts": (
            "• Paris–Le Bourget Airport is best known as the home of the Paris Air Show — the world's largest aviation trade event — making its fire station a safety facility for one of aviation's most prestigious venues.\n"
            "• The SSLIA (Service de Sauvetage et de Lutte contre l'Incendie des Aéronefs) is the French standard for airport rescue and firefighting — one of the most stringent regulatory frameworks in the world.\n"
            "• 1PAX's architectural approach assigns a bold, distinctive colour to the fire shed — ensuring instant visual recognition in an emergency, a functional safety decision expressed through architectural design."
        ),
    },

    "air_guyane_hangar": {
        "display_name": "Air Guyane Hangar – Félix Eboué Cayenne Airport",
        "category": "Industrial Buildings",
        "location": "French Guiana",
        "year": "2023",
        "client": "EDEIS COLAS",
        "architect": "1PAX",
        "partners": "Ingerop",
        "area": "Not disclosed",
        "capacity": "Not applicable",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Delivering a compact, high-performance hangar that supports fleet growth "
            "within constrained airport conditions."
        ),
        "overview": (
            "In 2023, 1PAX was commissioned by EDEIS COLAS, in collaboration with Ingerop, to design a "
            "new aircraft hangar for Air Guyane at Félix Eboué Cayenne Airport. The project responds to "
            "the airline's growing operational needs, providing additional space to accommodate an "
            "expanding fleet while integrating seamlessly into existing airport infrastructure. The "
            "resulting hangar provides Air Guyane with a robust, future-ready facility that supports "
            "fleet expansion without disrupting airport logistics, strengthening Félix Eboué Cayenne "
            "Airport's capacity to support local aviation growth while maintaining high functional "
            "coherence across the airside environment."
        ),
        "key_challenge": (
            "The primary challenge was the site constraint: the designated area for the new hangar was "
            "partially occupied by an active cargo parking zone critical to airport operations. The "
            "project required a solution that could increase aircraft accommodation capacity without "
            "compromising existing logistics functions or reducing parking availability."
        ),
        "approach": (
            "1PAX developed an innovative spatial strategy that optimised land use and carefully balanced "
            "operational priorities. The hangar layout was designed to maximise internal efficiency and "
            "aircraft manoeuvrability while preserving the full functionality of the adjacent cargo "
            "parking area. Architectural and technical decisions were guided by clarity of circulation, "
            "ease of maintenance, and direct integration with Air Guyane's operational workflows."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Air Guyane hangar design demonstrates sustainable use of constrained land through "
            "spatial innovation — solving fleet growth needs without expanding the airport footprint into "
            "new areas or displacing essential cargo operations. The efficient layout minimises structural "
            "material use while maximising operational capacity, and the design's integration with "
            "adjacent infrastructure avoids duplicating circulation systems and utilities."
        ),
        "status": "Design completed — 2023",
        "tender_result": "Direct commission by EDEIS COLAS",
        "scope": "Architectural design — new aircraft hangar for Air Guyane at Félix Eboué Cayenne Airport, optimizing land use within active cargo zone constraints",
        "program": (
            "• Aircraft hangar accommodating Air Guyane's expanded fleet\n"
            "• Innovative spatial layout preserving full functionality of adjacent cargo parking zone\n"
            "• Maximized internal efficiency and aircraft manoeuvrability\n"
            "• Direct integration with Air Guyane operational workflows"
        ),
        "fun_facts": (
            "• Air Guyane is French Guiana's regional airline, operating flights across the territory's interior — an extraordinary operational context where small aircraft serve remote Amazonian communities.\n"
            "• The hangar's site constraint — an active cargo parking zone that could not be displaced — required a spatial solution that solved two operational needs simultaneously within a single footprint.\n"
            "• 1PAX designed the Air Guyane hangar alongside the terminal extension, office buildings, interior design, and airport masterplan at Cayenne — making it one of the firm's most comprehensive single-airport engagements."
        ),
    },

    "belgrade_admin_building": {
        "display_name": "Belgrade Nikola Tesla Airport – New Administration Building",
        "category": "Working and Living",
        "location": "Belgrade, Serbia",
        "year": "2019",
        "client": "Vinci Airports Serbia / Belgrade Airport",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "4,500 m²",
        "capacity": "Not applicable",
        "cost": "7 million €",
        "video_url": "",
        "tagline": (
            "Creating a biophilic, light-filled workplace that supports efficiency, well-being, "
            "and sustainable performance."
        ),
        "overview": (
            "In 2019, 1PAX was commissioned by Vinci Airports Serbia / Belgrade Airport to design the "
            "New Airport Administration Building (NAAB). The project comprises a five-storey office "
            "building with a basement level, accommodating administrative offices and support services "
            "for airport staff. Conceived as a contemporary workplace within the airport campus, the "
            "building is organised around a landscaped courtyard that defines its main pedestrian and "
            "parking entrances. The building provides a high-quality, sustainable work environment "
            "tailored to the needs of airport administration, with a central garden at its core that "
            "enhances well-being, informal interaction, and the overall quality of daily work life."
        ),
        "key_challenge": (
            "The challenge was to design a highly functional administrative building that supports "
            "diverse office activities while ensuring comfort, daylight access, and environmental "
            "performance. The project needed to balance operational efficiency with staff well-being, "
            "addressing issues of solar exposure, thermal gain, and spatial quality within a dense "
            "airport environment."
        ),
        "approach": (
            "1PAX developed a design strategy centred on natural light, greenery, and passive "
            "environmental control. Office layouts were carefully oriented to maximise daylight while "
            "minimising glare and overheating, supported by sunshades and external blinds protecting "
            "glazed façades. A planted roof was introduced to reduce thermal gain and improve overall "
            "environmental performance. At the heart of the building, a glazed roof covers an interior "
            "garden that visually and physically connects all levels, bringing natural light and "
            "vegetation into the core of the building and fostering informal interaction and well-being "
            "across entrances, the main hall, cafeterias, and conference areas."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Belgrade Administration Building integrates multiple passive environmental strategies: "
            "a planted roof reduces thermal gain and manages stormwater; external sunshades and blinds "
            "control solar exposure; and a central glazed garden provides natural ventilation and "
            "daylighting deep into the building floor plate. The biophilic approach — with a central "
            "garden at the heart of the workplace — improves staff well-being and reduces energy "
            "consumption for artificial lighting and mechanical ventilation."
        ),
        "status": "Design completed — 2019",
        "tender_result": "Direct commission by Vinci Airports Serbia / Belgrade Airport",
        "scope": "Architectural design — 4,500 m² five-storey airport administration building with biophilic central garden, serving airport staff at Nikola Tesla Airport",
        "program": (
            "• Five-storey office building with basement level — 4,500 m²\n"
            "• Administrative offices and support services for airport staff\n"
            "• Central glazed interior garden connecting all levels\n"
            "• Planted roof for thermal gain reduction and stormwater management\n"
            "• External sunshades and blinds for solar control\n"
            "• Cafeterias, conference areas, and informal interaction spaces around central garden"
        ),
        "fun_facts": (
            "• The building's defining feature — a glazed interior garden connecting all five floors — creates a biophilic heart in what would otherwise be a purely functional office building within an industrial airport campus.\n"
            "• At 4,500 m² and 7 million €, the Belgrade Administration Building demonstrates 1PAX's ability to deliver architectural quality and environmental intelligence within modest budgets.\n"
            "• The building is part of 1PAX's comprehensive presence at Belgrade Airport, where the firm has designed the terminal expansion, fire station, landside, and this administration building — an exceptional breadth of work at a single site."
        ),
    },

    "tokyo_eu_delegation": {
        "display_name": "European Commission New Delegation Building – Tokyo",
        "category": "Working and Living",
        "location": "Tokyo, Japan",
        "year": "2012",
        "client": "European Commission",
        "architect": "ADPI (Mabel Miranda, Lead Architect)",
        "partners": "Not disclosed",
        "area": "10,300 m²",
        "capacity": "Not applicable",
        "cost": "30 million €",
        "video_url": "https://vimeo.com/1166384769/c2f8efc903?share=copy&fl=sv&fe=ci",
        "tagline": (
            "A contemporary diplomatic landmark defined by urban intelligence, programmatic clarity, "
            "and a unifying architectural skin."
        ),
        "overview": (
            "In 2012, ADPI was awarded first prize in the competition for the new European Commission "
            "Delegation Building in Tokyo. Developed for the European Commission, the project "
            "encompassed studies, design development, and supervision of a major diplomatic complex "
            "bringing together headquarters offices, residential units for European representatives, "
            "diplomatic representation spaces, parking facilities, and landscaped gardens. Mabel Miranda "
            "acted as Lead Architect, with ADPI authorisation, on a project of significant institutional, "
            "urban, and symbolic importance. The project delivered a strong, legible, and enduring "
            "architectural response, with its first-prize recognition acknowledging clarity of urban "
            "strategy, effective resolution of functional complexity, and the expressive power of the "
            "copper façade."
        ),
        "key_challenge": (
            "The project addressed a highly complex brief combining multiple functions with distinct "
            "security, privacy, and representational requirements within a dense urban context. The "
            "challenge was to achieve a coherent architectural identity capable of unifying these diverse "
            "programmes while ensuring efficient circulation, strong urban integration, and a dignified "
            "yet contemporary image for the European Union's presence in Japan."
        ),
        "approach": (
            "The winning proposal was driven by a clear urban insertion strategy, carefully negotiating "
            "scale, alignment, and presence within the surrounding city fabric. Programmatic complexity "
            "was resolved through a rational spatial organisation clearly separating public, diplomatic, "
            "residential, and service zones while maintaining internal coherence. A continuous copper "
            "skin enveloped the building, acting as both an architectural unifier and a symbolic element "
            "— its materiality offering durability, elegance, and a distinctive identity that evolves "
            "over time through patina."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Tokyo EU Delegation Building's copper façade exemplifies material sustainability: "
            "copper is fully recyclable, develops a natural protective patina that eliminates the need "
            "for coatings or regular repainting, and has an operational lifespan measured in centuries. "
            "The building's integrated courtyard gardens support biodiversity and passive cooling within "
            "the dense urban site. The rational, compact organisation of the building's mixed programme "
            "minimises overall floor area and energy consumption relative to separated building "
            "typologies."
        ),
        "status": "Built — completed and delivered (competition won 2012)",
        "tender_result": "Winner of international competition (1st Prize, 2012)",
        "scope": "Architectural design — 10,300 m² European Commission delegation complex including headquarters offices, residential units, diplomatic representation spaces, parking, and gardens",
        "program": (
            "• Headquarters offices for European Commission Delegation\n"
            "• Residential units for European representatives\n"
            "• Diplomatic representation and reception spaces\n"
            "• Parking facilities\n"
            "• Landscaped courtyard gardens\n"
            "• Continuous copper skin façade unifying all programmes"
        ),
        "fun_facts": (
            "• The building's continuous copper skin was selected for its longevity, patina, and symbolic weight — copper develops a unique living surface over decades, making the building literally change appearance with time.\n"
            "• The project consolidates multiple functions — offices, residences, diplomatic spaces, parking, and gardens — under a single unified architectural skin, a compositional challenge rarely achieved with such elegance.\n"
            "• Mabel Miranda, Lead Architect on the project under ADPI authorization, subsequently became a founding force at 1PAX — making this Tokyo EU Delegation one of the DNA projects of the firm's leadership."
        ),
    },

    "french_embassy_bangkok": {
        "display_name": "French Embassy – Architectural Design",
        "category": "Working and Living",
        "location": "Bangkok, Thailand",
        "year": "2015",
        "client": "Ministère des Affaires Étrangères (French Ministry of Foreign Affairs)",
        "architect": "ADPI (Mabel Miranda, Lead Architect)",
        "partners": "Not disclosed",
        "area": "4,500 m²",
        "capacity": "Not applicable",
        "cost": "13 million €",
        "video_url": "https://vimeo.com/1166381524/b5d90d3995?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Reinterpreting diplomatic architecture through contextual renewal rather than demolition."
        ),
        "overview": (
            "In 2015, the architectural competition for the French Embassy in Bangkok proposed a "
            "strategic transformation of an existing diplomatic compound located within a highly degraded "
            "urban context. Commissioned by the French Ministry of Foreign Affairs, the project was "
            "developed by ADPI, with Mabel Miranda acting as Lead Architect. Rather than pursuing full "
            "demolition and reconstruction as initially suggested in the brief, the proposal advocated "
            "for a more sustainable and context-sensitive approach through refurbishment of existing "
            "facilities combined with a carefully integrated new extension. The winning proposal "
            "successfully reimagined the French Embassy as a modern diplomatic landmark rooted in its "
            "local context, reflecting a progressive vision of diplomatic architecture."
        ),
        "key_challenge": (
            "The principal challenge lay in redefining the image and presence of the Embassy within its "
            "neighbourhood while respecting diplomatic security requirements, functional needs, and "
            "local urban conditions. The project needed to modernise the embassy's facilities, reinforce "
            "its symbolic role, and improve environmental performance — all while minimising disruption "
            "and preserving existing structures where possible."
        ),
        "approach": (
            "The design proposed a radical yet respectful architectural language: a white building "
            "characterised by sharp, sloping forms inspired by Thai vernacular architecture. This "
            "contemporary interpretation established a strong identity while maintaining dialogue with "
            "local climatic and cultural references. The intervention combined the renovation of an "
            "existing building with the construction of a new extension, creating a cohesive ensemble "
            "that balanced modernity, tradition, and sustainability — demonstrating how adaptive reuse "
            "and extension can deliver architectural ambition without resorting to total reconstruction."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The French Embassy Bangkok project embodies adaptive reuse as a core sustainability "
            "strategy. By refurbishing existing structures rather than demolishing and rebuilding, the "
            "proposal avoids substantial embodied carbon waste and preserves the value of existing "
            "construction. The sloping roof forms inspired by Thai vernacular architecture actively "
            "manage solar exposure and natural ventilation in Bangkok's tropical climate, reducing "
            "long-term cooling energy demand."
        ),
        "status": "Competition entry — 2015",
        "tender_result": "Winner of architectural competition (1st Prize, 2015)",
        "scope": "Architectural design — 4,500 m² French Embassy compound transformation through refurbishment of existing buildings combined with new extension, Bangkok",
        "program": (
            "• Refurbishment of existing embassy compound buildings\n"
            "• New architectural extension integrated with existing fabric\n"
            "• Diplomatic offices and administrative spaces\n"
            "• Security-compliant access and circulation strategy\n"
            "• Contemporary Thai vernacular-inspired roof forms for solar control and identity"
        ),
        "fun_facts": (
            "• The competition brief initially called for demolition and full reconstruction — 1PAX's winning proposal successfully challenged this by demonstrating the superiority of adaptive refurbishment, both architecturally and environmentally.\n"
            "• The building's distinctive sloping white forms reference Thai vernacular architecture — a subtle but respectful cultural gesture by a foreign diplomatic mission.\n"
            "• Mabel Miranda, Lead Architect on this project under ADPI authorization, is one of the key figures who later founded 1PAX — making the Bangkok Embassy part of the firm's foundational design legacy."
        ),
    },

    "cayenne_airport_offices": {
        "display_name": "Félix Eboué Cayenne Airport – Office Buildings (Air Guyane & CNES)",
        "category": "Working and Living",
        "location": "French Guiana",
        "year": "2023",
        "client": "EDEIS COLAS",
        "architect": "1PAX",
        "partners": "Ingerop",
        "area": "800 m²",
        "capacity": "Not applicable",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Delivering functional, purpose-built work environments integrated within a "
            "complex airport ecosystem."
        ),
        "overview": (
            "In 2023, as part of the broader renovation and expansion of Félix Eboué Cayenne Airport, "
            "1PAX was commissioned by EDEIS COLAS to design a series of dedicated office and operational "
            "buildings. Developed in collaboration with Ingerop, the scope included corporate facilities "
            "for Air Guyane and a specialised building for CNES, integrating administrative, operational, "
            "and security-related functions within the airport precinct. The project delivered robust, "
            "fit-for-purpose office environments that respond precisely to the operational realities of "
            "airport-based organisations, improving operational efficiency and working conditions within "
            "Félix Eboué Cayenne Airport."
        ),
        "key_challenge": (
            "The project required accommodating highly specific operational needs within a secure and "
            "constrained airport environment. The challenge was to deliver efficient, clearly organised "
            "workspaces that support daily operations, security protocols, and staff well-being, while "
            "ensuring seamless integration with airside activities and adjacent infrastructure such as "
            "hangars and controlled access zones."
        ),
        "approach": (
            "1PAX developed tailored architectural solutions for each entity. The CNES/VIP building was "
            "designed to incorporate PIF control areas, reception spaces, passport control, and sanitary "
            "facilities, ensuring clear separation between public, controlled, and operational zones. For "
            "Air Guyane, offices adjacent to the airline's hangar were conceived as a fully functional "
            "operational hub, integrating workshops, locker rooms, meeting rooms, rest areas, and "
            "administrative offices — with spatial organisation prioritising efficiency, clarity of "
            "circulation, and direct adjacency to operational facilities."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Cayenne airport office buildings are designed for operational efficiency and minimal "
            "footprint within an already-developed airport precinct. By co-locating Air Guyane's offices "
            "directly adjacent to their hangar, the design minimises staff travel distances within the "
            "airside environment, reducing energy consumption and operational complexity. The compact, "
            "purposeful design avoids unnecessary floor area, directly reducing embodied carbon and "
            "ongoing energy use."
        ),
        "status": "Design completed — 2023",
        "tender_result": "Direct commission by EDEIS COLAS",
        "scope": "Architectural design — 800 m² dedicated office and operational buildings for Air Guyane and CNES at Félix Eboué Cayenne Airport",
        "program": (
            "• CNES/VIP building: PIF control areas, reception, passport control, and sanitary facilities\n"
            "• Air Guyane offices: workshops, locker rooms, meeting rooms, rest areas, and administrative offices\n"
            "• Clear separation of public, controlled, and operational zones\n"
            "• Direct spatial adjacency to Air Guyane hangar"
        ),
        "fun_facts": (
            "• The CNES building at Cayenne Airport serves one of the world's most unique tenant profiles — the French Space Agency (Centre National d'Études Spatiales), whose launch site at Kourou in French Guiana is among the most active in the world.\n"
            "• 1PAX's involvement at Cayenne Airport spans five distinct projects: terminal extension, masterplan, air hangar, office buildings, and interior design — making it one of the most comprehensive single-airport portfolios in the firm's history.\n"
            "• Designing offices for an operational airline within an active airside environment requires specialized knowledge of security protocols, controlled zone interfaces, and operational workflow — a niche expertise 1PAX developed through its deep airport portfolio."
        ),
    },

    "qatar_railways_hq": {
        "display_name": "Qatar Railways Headquarters",
        "category": "Working and Living",
        "location": "Doha, Qatar",
        "year": "Not disclosed",
        "client": "SETEC TPI / Siemens",
        "architect": "1PAX (as 1M2)",
        "partners": "Not disclosed",
        "area": "15,000 m²",
        "capacity": "Not applicable",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "A contemporary civic workplace that embodies the identity and ambition of a national "
            "mobility institution."
        ),
        "overview": (
            "Conceived as a competition entry for the headquarters of Qatar Railways in Doha, this "
            "proposal reimagines the corporate workplace as an open, integrated, and future-oriented "
            "urban ensemble. Designed by 1PAX (as 1M2) for SETEC TPI and Siemens, the project "
            "consolidates offices, parking, and public space into a coherent architectural composition "
            "embedded within the civic fabric. Beyond accommodating administrative functions, the "
            "headquarters acts as a public-facing institution — representing the operational excellence "
            "and forward-looking vision of Qatar's rail network. The design establishes a strong "
            "institutional identity for Qatar Railways that communicates innovation, reliability, and "
            "civic responsibility."
        ),
        "key_challenge": (
            "The challenge was to reconcile operational precision and security requirements with "
            "openness, accessibility, and urban integration. The headquarters needed to function as an "
            "efficient administrative machine while projecting transparency and civic presence — avoiding "
            "the isolation often associated with large institutional buildings."
        ),
        "approach": (
            "The architectural concept is structured around clarity of circulation, legible spatial "
            "organisation, and intuitive movement. Office environments are designed to foster "
            "collaboration, well-being, and adaptability, anticipating the evolution of workplace "
            "culture and technology. The ensemble creates a dialogue between built form and public realm "
            "through carefully framed open spaces and shaded pedestrian areas that soften the transition "
            "between infrastructure and city. Sustainability principles inform both form and performance: "
            "passive strategies, efficient envelopes, and resource-conscious systems reflect a commitment "
            "to embedding life-cycle thinking and environmental responsibility."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Qatar Railways HQ proposal integrates sustainability at multiple scales: passive "
            "environmental strategies and efficient envelopes reduce energy demand in Doha's extreme "
            "climate; shaded pedestrian areas and landscaped public spaces improve microclimate "
            "conditions and reduce urban heat island effects; and the integrated parking and service "
            "areas avoid surface sprawl, concentrating footprint and preserving civic space. Life-cycle "
            "thinking informed material and structural choices throughout."
        ),
        "status": "Competition entry — year not disclosed",
        "tender_result": "Competition entry for SETEC TPI / Siemens",
        "scope": "Competition design — 15,000 m² Qatar Railways Headquarters in Doha, integrating offices, parking, public space, and institutional civic presence",
        "program": (
            "• Headquarters offices — 15,000 m²\n"
            "• Integrated parking and service facilities\n"
            "• Shaded pedestrian areas and landscaped civic spaces\n"
            "• Public-facing institutional ground floor\n"
            "• Passive environmental systems and efficient building envelope for Doha's climate"
        ),
        "fun_facts": (
            "• The Qatar Railways HQ was conceived as an open, civic institution — a deliberate departure from the fortified, isolated compounds typical of large institutional buildings in Qatar.\n"
            "• The project was delivered under the brand name '1M2' — an earlier iteration of 1PAX — reflecting the studio's long history in Qatar's major infrastructure projects.\n"
            "• Qatar Railways (now Mowasalat / Karwa) operates the Doha Metro — one of the most technologically advanced metro systems in the world, opened in 2019 and serving the 2022 FIFA World Cup infrastructure."
        ),
    },

    "montijo_airport_commercial": {
        "display_name": "Montijo Airport – Passenger Experience Design of Commercial Areas",
        "category": "Interior Design",
        "location": "Montijo, Portugal",
        "year": "2020",
        "client": "Vinci Airports / ANA Aeroportos",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "Not disclosed",
        "capacity": "Not disclosed",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Reinterpreting Lisbon's cultural heritage to create an immersive, contemporary "
            "retail experience within a new airport gateway."
        ),
        "overview": (
            "In 2020, 1PAX was commissioned by Vinci Airports / ANA Aeroportos to design the passenger "
            "experience for the commercial areas of Montijo Airport. The project focused on shaping a "
            "distinctive retail environment that goes beyond functionality, positioning commercial spaces "
            "as cultural ambassadors that introduce passengers to the spirit of Lisbon and Portugal from "
            "the moment they enter the terminal. The project redefined the role of airport commercial "
            "areas as immersive, culture-driven spaces rather than purely transactional environments, "
            "enhancing passenger engagement, strengthening local identity, and elevating the overall "
            "airport experience."
        ),
        "key_challenge": (
            "The challenge was to design commercial areas that would deliver a strong sense of place "
            "while remaining flexible, technologically integrated, and aligned with contemporary airport "
            "operations. The spaces needed to balance retail performance with experiential quality, "
            "creating an environment that resonates emotionally with passengers and supports evolving "
            "commercial formats."
        ),
        "approach": (
            "1PAX developed a design concept inspired by Lisbon's Art Nouveau heritage and traditional "
            "Portuguese architecture. Storefronts were conceived as portico-like façades, evoking the "
            "rhythm and character of Lisbon's historic streets. Materials such as steelwork and marble "
            "were combined with a vibrant colour palette. The façades were designed as adaptable "
            "surfaces capable of hosting digital projections, video mapping, and LED content, with "
            "integrated flight information, cultural storytelling, and immersive media experiences "
            "transforming retail zones into dynamic environments. A central plaza and perimeter nature "
            "area were conceived as experiential anchors blending architecture, light, and digital media."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Montijo Airport commercial design integrates natural and traditional materials — steelwork "
            "and marble — alongside adaptable digital surface technologies, reducing the need for "
            "full physical refurbishment when commercial concepts change. The central nature area "
            "introduces biophilic elements into the retail environment, improving passenger well-being "
            "and supporting the airport's environmental identity. The design's adaptability ensures "
            "long-term commercial relevance without resource-intensive renovations."
        ),
        "status": "Design completed — 2020",
        "tender_result": "Direct commission by Vinci Airports / ANA Aeroportos",
        "scope": "Passenger experience design for commercial areas — Art Nouveau-inspired retail concept with digital façades, cultural storytelling, and central nature plaza for Montijo Airport",
        "program": (
            "• Retail storefronts as portico-like façades inspired by Lisbon's Art Nouveau heritage\n"
            "• Adaptable façade surfaces hosting digital projections, video mapping, and LED content\n"
            "• Integrated flight information and cultural storytelling systems\n"
            "• Central plaza as experiential anchor\n"
            "• Perimeter nature area combining architecture, light, and biophilic elements"
        ),
        "fun_facts": (
            "• Montijo Airport was proposed as Lisbon's second airport — intended to relieve pressure on the overcrowded Humberto Delgado Airport — making this commercial design part of a politically significant infrastructure project.\n"
            "• The retail concept draws directly on Lisbon's Art Nouveau heritage — a subtle cultural thread connecting airport passengers to the city's architectural identity before they even leave the terminal.\n"
            "• The adaptable digital façade system allows commercial content to change without physical renovation — a genuinely circular design approach for a retail environment."
        ),
    },

    "jorge_chavez_food_hall": {
        "display_name": "Jorge Chávez International Airport – Food Hall Design",
        "category": "Interior Design",
        "location": "Callao, Peru",
        "year": "Under construction (delivery 2025)",
        "client": "Lagardère Travel Retail",
        "architect": "1PAX",
        "partners": "Altavia Travel Retail",
        "area": "1,800 m²",
        "capacity": "Supporting an airport of 37.5 million passengers annually",
        "cost": "2.1 million USD",
        "video_url": "https://vimeo.com/1166383973/7fd9589f2b?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Designing a vibrant, legible food hall that elevates passenger experience "
            "within a major airport expansion."
        ),
        "overview": (
            "This project forms part of the major expansion of Jorge Chávez International Airport, "
            "commissioned by Lagardère Travel Retail with Altavia Travel Retail as partner. 1PAX "
            "developed the architectural design for a new 1,800 m² Food Hall serving one of Latin "
            "America's fastest-growing aviation hubs, with a projected capacity of 37.5 million "
            "passengers annually. The Food Hall design delivers a coherent, high-capacity dining "
            "destination that balances strong architectural identity with operational performance, "
            "contributing a distinctive and memorable food experience to the new terminal and "
            "reinforcing Jorge Chávez International Airport's ambition to offer a world-class "
            "passenger journey."
        ),
        "key_challenge": (
            "The primary challenge was to design a large-scale food hall capable of handling very "
            "high passenger volumes while remaining intuitive, welcoming, and operationally efficient. "
            "The space needed to offer diversity and choice without visual or functional congestion, "
            "ensure clear orientation, and support seamless back-of-house operations for multiple "
            "brands within a constrained airport environment."
        ),
        "approach": (
            "1PAX conceived the Food Hall as a clearly structured, panoramic space organised into "
            "five distinct zones. The entrance is anchored by Sazón Nation — a strong spatial landmark "
            "defined by sculptural, tree-like elements that establish identity and visibility from the "
            "outset. Passengers benefit from clear sightlines across all kiosks, arranged to showcase a "
            "diverse culinary offer supported by legible directional signage. A generous general seating "
            "area accommodates varied user preferences and dwell times. Five branded kiosks — KO Asian "
            "Kitchen, La Lucha, Las Reyes, Burger Boy, and Tori — are supported by a carefully planned "
            "shared back-of-house ensuring efficient logistics and operational continuity."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Jorge Chávez Food Hall is designed for operational efficiency and long-term "
            "adaptability. The shared back-of-house infrastructure for all five kiosks reduces "
            "redundant equipment and energy use compared to fully independent kitchen setups. The "
            "clear spatial organisation and generous sightlines improve passenger flow, reducing "
            "congestion-related energy waste in HVAC systems. The use of natural, sculptural forms "
            "in key landmark elements connects passengers to Peru's natural heritage."
        ),
        "status": "Under construction — delivery 2025",
        "tender_result": "Direct commission by Lagardère Travel Retail",
        "scope": "Architectural design — 1,800 m² Food Hall for Jorge Chávez International Airport new terminal expansion, serving five branded food kiosks",
        "program": (
            "• Sazón Nation entrance landmark — sculptural tree-like elements establishing identity\n"
            "• Five branded food kiosks: KO Asian Kitchen, La Lucha, Las Reyes, Burger Boy, Tori\n"
            "• Shared back-of-house kitchen and logistics infrastructure\n"
            "• General seating area accommodating varied user preferences\n"
            "• Clear sightlines across all kiosks with legible directional signage"
        ),
        "fun_facts": (
            "• Jorge Chávez International Airport is undergoing one of Latin America's largest terminal expansions, targeting 37.5 million passengers annually — nearly double its previous capacity.\n"
            "• The 'Sazón Nation' entrance landmark celebrates Peru's extraordinary culinary culture — one of the world's most celebrated food destinations — through sculptural architecture.\n"
            "• The shared back-of-house for five distinct food brands is a sophisticated logistical achievement: coordinating separate brand identities, menus, and operational flows within a single efficient kitchen system."
        ),
    },

    "lima_peru_plaza_food_court": {
        "display_name": "Jorge Chávez International Airport – Peru Plaza Food Court Renovation",
        "category": "Interior Design",
        "location": "Callao, Peru",
        "year": "2020 (Built)",
        "client": "Lima Airport Partners / OSITRAN",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "1,030 m²",
        "capacity": "612 seats",
        "cost": "400,000 USD",
        "video_url": "",
        "tagline": (
            "Transforming a landside food court into a high-capacity, comfortable, and well-organized "
            "public space ahead of a major international event."
        ),
        "overview": (
            "Built in 2020, this project followed 1PAX's winning entry in the design competition "
            "organised by Lima Airport Partners in October 2018 to renovate the landside food court "
            "of Jorge Chávez International Airport. Commissioned by Lima Airport Partners and OSITRAN, "
            "the intervention focused on the architectural redesign of the Peru Plaza Food Court — a "
            "1,030 m² public space accommodating over 600 seats. The project responded to an urgent "
            "need to upgrade capacity and quality in anticipation of the Pan-American Games. The "
            "renovation significantly upgraded the food court's functionality and atmosphere, delivering "
            "measurable improvements in capacity, comfort, lighting quality, acoustics, and spatial "
            "legibility for passengers and operators alike."
        ),
        "key_challenge": (
            "The existing food court was no longer able to meet peak demand in terms of capacity, "
            "comfort, and spatial clarity. The challenge was to substantially increase seating and "
            "improve overall performance — acoustic, lighting, and spatial organisation — while ensuring "
            "ease of maintenance and operational efficiency for the airport operator, all within a "
            "constrained landside environment."
        ),
        "approach": (
            "1PAX developed a comprehensive architectural redesign focused on both user experience "
            "and operational robustness. The proposal reinforced seating capacity while carefully "
            "reorganising layouts to improve circulation, visibility, and comfort. Particular attention "
            "was given to acoustic treatment and lighting design to reduce noise levels and create a "
            "more welcoming atmosphere. Materials, furniture, and spatial arrangements were selected "
            "to balance durability, ease of maintenance, and visual coherence, ensuring long-term "
            "performance in a high-traffic public space."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Peru Plaza Food Court renovation prioritises sustainability through refurbishment "
            "over replacement — improving an existing 1,030 m² landside space rather than building new. "
            "The choice of durable, easy-to-maintain materials extends the renovated facility's useful "
            "life, reducing future capital expenditure and waste. Improved lighting design reduces "
            "energy consumption while enhancing comfort, and the acoustic improvements contribute "
            "to a lower-stress environment that benefits both passenger well-being and operational "
            "efficiency."
        ),
        "status": "Built — completed 2020",
        "tender_result": "Winner of design competition organized by Lima Airport Partners (October 2018)",
        "scope": "Architectural redesign of 1,030 m² landside food court at Jorge Chávez International Airport — capacity expansion, acoustic treatment, lighting redesign, and spatial reorganization for 612 seats",
        "program": (
            "• Architectural redesign of 1,030 m² Peru Plaza Food Court\n"
            "• Seating capacity expansion to 612 seats\n"
            "• Acoustic treatment to reduce noise levels\n"
            "• Lighting redesign for comfort and atmosphere\n"
            "• Spatial reorganization for improved circulation and visibility\n"
            "• Durable, easy-to-maintain material selection"
        ),
        "fun_facts": (
            "• The renovation was completed just in time for the 2019 Pan-American Games in Lima — one of the hemisphere's largest multi-sport events — driving urgency and precision in the delivery timeline.\n"
            "• At 612 seats in just 1,030 m², the food court achieves one of the highest seating densities in any airport public space — a testament to the spatial efficiency of the redesign.\n"
            "• 1PAX won the competition organized by Lima Airport Partners in October 2018 and completed construction by 2020 — a rapid design-to-delivery cycle for a high-profile public space."
        ),
    },

    "marseille_commercial_assistance": {
        "display_name": "Aéroport de Marseille Provence – Architectural Assistance for Commercial Facilities",
        "category": "Interior Design",
        "location": "Marseille, Provence-Alpes-Côte d'Azur, France",
        "year": "2024",
        "client": "Marseille Provence Airport",
        "architect": "1PAX / KAIRN Ingénierie",
        "partners": "ODG / ADN (terminal architect: Foster + Partners)",
        "area": "4,950 m²",
        "capacity": "Not disclosed",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Structuring a robust framework for future food and beverage facilities within a "
            "major terminal extension."
        ),
        "overview": (
            "In 2024, 1PAX was commissioned by Marseille Provence Airport to provide architectural "
            "assistance and consulting services for the implementation of new commercial catering "
            "facilities at Terminal 1. Working in collaboration with KAIRN Ingénierie and within the "
            "architectural vision defined by Foster + Partners as Airport Architect, the mission focused "
            "on programming, technical coordination, and strategic support for a key component of the "
            "terminal's extension and modernisation. The assignment provided Marseille Provence Airport "
            "with a structured, actionable foundation for successful implementation of its future "
            "catering facilities, reducing delivery risks and supporting efficient procurement."
        ),
        "key_challenge": (
            "The development of future catering facilities required a clear and anticipatory framework "
            "capable of aligning architectural intent, operational needs, and commercial performance. "
            "The challenge was to define precise technical requirements and spatial principles that "
            "could support diverse food and beverage concepts while remaining fully compatible with "
            "the terminal's expansion, passenger flows, and airport-wide operational constraints."
        ),
        "approach": (
            "1PAX led a programming and consulting mission centred on the definition of technical "
            "specifications for catering areas within Terminal 1. The team translated operational "
            "objectives into clear architectural and technical guidelines, addressing layouts, "
            "servicing requirements, interfaces with public areas, and back-of-house logistics. In "
            "parallel, 1PAX supported the preparation of tender documentation for catering operators, "
            "ensuring future concessions would align with the airport's quality standards, functional "
            "expectations, and long-term development strategy."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "By providing clear technical specifications and programming guidance early in the design "
            "process, 1PAX's advisory role reduces costly design iterations and construction waste "
            "downstream. Well-defined back-of-house requirements ensure efficient energy and water "
            "systems for catering operations from the outset. The procurement support ensures that "
            "future commercial operators are selected with full awareness of the terminal's "
            "sustainability standards and infrastructure constraints."
        ),
        "status": "Consultation completed — 2024",
        "tender_result": "Direct commission by Marseille Provence Airport",
        "scope": "Architectural assistance and consulting — programming, technical coordination, and tender documentation for 4,950 m² catering facilities within Foster + Partners' Terminal 1 extension",
        "program": (
            "• Technical specifications for catering areas within Terminal 1\n"
            "• Back-of-house logistics and servicing requirements definition\n"
            "• Interface coordination with Foster + Partners' terminal architecture\n"
            "• Tender documentation preparation for catering operators\n"
            "• Programming and consulting support throughout commercial procurement"
        ),
        "fun_facts": (
            "• Terminal 1 at Marseille Provence Airport is being extended by Foster + Partners — one of the world's most celebrated airport architects — with 1PAX providing specialized commercial programming expertise within that vision.\n"
            "• 1PAX's role in this project is advisory rather than design-led, demonstrating the breadth of services the firm offers beyond architecture — from strategic programming to operator tender support.\n"
            "• Marseille Provence Airport serves France's second-largest metropolitan area and one of the Mediterranean's most important cultural and commercial cities — making this commercial catering assignment strategically significant."
        ),
    },

    "belgrade_wayfinding": {
        "display_name": "Nikola Tesla International Airport – Wayfinding Signage Design",
        "category": "Interior Design",
        "location": "Belgrade, Serbia",
        "year": "2019",
        "client": "Belgrade Airport",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "92,000 m² (terminal coverage)",
        "capacity": "15 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Enhancing clarity and orientation through a high-visibility wayfinding system "
            "aligned with international airport standards."
        ),
        "overview": (
            "In 2019, 1PAX was commissioned by Belgrade Airport to design the wayfinding signage "
            "system for Nikola Tesla International Airport — a major regional hub serving up to 15 "
            "million passengers annually. The project covered approximately 92,000 m² of terminal "
            "space and focused on improving passenger orientation, gate visibility, and overall "
            "legibility within a complex and evolving airport environment. The new wayfinding system "
            "significantly improved passenger orientation and movement efficiency throughout the "
            "terminal, delivering a robust and adaptable navigation framework that supports smoother "
            "passenger flows and a more confident travel experience."
        ),
        "key_challenge": (
            "The airport required a clear and consistent wayfinding strategy capable of guiding high "
            "passenger volumes efficiently while adapting to operational changes and terminal growth. "
            "The challenge was to enhance visibility and comprehension without overloading the visual "
            "environment, ensuring that signage remained intuitive, readable, and aligned with "
            "international concession and operational standards."
        ),
        "approach": (
            "1PAX developed the wayfinding system using Vinci Airports Concessions charts as a "
            "reference framework, ensuring consistency with global best practices. The system "
            "emphasised improved gate visibility through carefully positioned signage boards and "
            "totems. Backlit elements were integrated to enhance readability in varying lighting "
            "conditions, reinforcing visual hierarchy and supporting effortless navigation across "
            "key passenger decision points throughout the 92,000 m² terminal."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Belgrade wayfinding system uses backlit LED signage elements as a core technology, "
            "significantly reducing energy consumption compared to conventional fluorescent signage "
            "while providing superior visibility and colour rendering. The system's alignment with "
            "Vinci Airports' international standards ensures longevity and compatibility with future "
            "terminal developments, avoiding the need for complete signage replacement as the airport "
            "evolves. Clear wayfinding also reduces passenger congestion, lowering energy demand "
            "from HVAC systems in high-dwell areas."
        ),
        "status": "Design completed — 2019",
        "tender_result": "Direct commission by Belgrade Airport",
        "scope": "Wayfinding signage design — comprehensive system for 92,000 m² terminal at Nikola Tesla International Airport serving up to 15 million passengers annually",
        "program": (
            "• Wayfinding system covering 92,000 m² of terminal space\n"
            "• Improved gate visibility through carefully positioned signage boards and totems\n"
            "• Backlit signage elements for readability in varying lighting conditions\n"
            "• Alignment with Vinci Airports Concessions international standards\n"
            "• Visual hierarchy reinforcing effortless navigation at all passenger decision points"
        ),
        "fun_facts": (
            "• Belgrade Nikola Tesla Airport handles 15 million passengers annually, making clear wayfinding across 92,000 m² of terminal a genuinely complex navigation challenge.\n"
            "• 1PAX's wayfinding design follows Vinci Airports' international concession standards — ensuring the system is immediately familiar to passengers who have used other Vinci-managed airports worldwide.\n"
            "• The project is one of several 1PAX commissions at Belgrade Airport — alongside the terminal expansion, fire station, admin building, and landside design — demonstrating an exceptionally deep relationship with this airport."
        ),
    },

    "nantes_commercial_zone": {
        "display_name": "Nantes Atlantique Airport – Development of the Commercial Zone",
        "category": "Interior Design",
        "location": "Bouguenais (Nantes), France",
        "year": "2017",
        "client": "Aéroport de Nantes Atlantique / Vinci Airports",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "2,000 m²",
        "capacity": "Supporting an airport of 7.2 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Reorganizing airport retail to create a coherent, attractive, and brand-aligned "
            "passenger experience."
        ),
        "overview": (
            "In 2017, 1PAX was commissioned by Aéroport de Nantes Atlantique, part of the Vinci "
            "Airports network, to develop the commercial zone of Nantes Atlantique Airport. The project "
            "addressed approximately 2,000 m² of retail space within an airport serving over 7 million "
            "passengers annually. Beyond commercial planning, the scope extended to defining a shared "
            "architectural and technical language for the terminal's main public areas. The project "
            "delivered a clearer, more engaging commercial environment that enhances the passenger "
            "journey and reinforces the airport's brand identity, providing a long-term framework for "
            "cohesive development across Halls 1, 2, and 3."
        ),
        "key_challenge": (
            "The existing commercial areas lacked clarity, coherence, and a strong spatial identity. "
            "The challenge was to reorganise the retail offer to improve legibility and passenger flow "
            "while establishing a unified aesthetic framework capable of guiding future developments "
            "across Halls 1, 2, and 3 — without disrupting ongoing airport operations."
        ),
        "approach": (
            "1PAX developed a strategic layout for the commercial zone, optimising visibility, "
            "circulation, and commercial performance. In parallel, the team defined an aesthetic and "
            "technical charter establishing clear guidelines for materials, lighting, signage, and "
            "architectural details. This charter was conceived as a flexible yet robust tool, ensuring "
            "consistency across different halls while allowing adaptability to evolving commercial and "
            "operational needs."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Nantes Atlantique commercial zone design charter promotes long-term sustainability by "
            "establishing a coherent material and design language that reduces the need for disruptive "
            "full renovations as commercial tenants change. By focusing on adaptable frameworks rather "
            "than bespoke fit-outs, the charter minimises construction waste and embodied carbon over "
            "successive commercial cycles. The strategic layout improves passenger flow efficiency, "
            "reducing dwell congestion and HVAC energy demand."
        ),
        "status": "Design completed — 2017",
        "tender_result": "Direct commission by Aéroport de Nantes Atlantique / Vinci Airports",
        "scope": "Commercial zone development — strategic layout for 2,000 m² retail space and aesthetic/technical charter for terminal public areas (Halls 1, 2, and 3)",
        "program": (
            "• Strategic commercial layout optimization for 2,000 m² retail zone\n"
            "• Aesthetic and technical charter for materials, lighting, signage, and architectural details\n"
            "• Design guidelines applicable across Halls 1, 2, and 3\n"
            "• Framework ensuring consistency and adaptability across future commercial cycles"
        ),
        "fun_facts": (
            "• Nantes Atlantique Airport serves over 7 million passengers annually — making it one of France's most significant regional airports and a key hub for western France.\n"
            "• The design charter 1PAX created functions as a living document — guiding all future commercial developments across three terminal halls without requiring 1PAX's direct involvement in each successive fitout.\n"
            "• Nantes was at the centre of one of France's most controversial airport debates — the abandoned Notre-Dame-des-Landes project — making Atlantique Airport's modernization a politically sensitive investment in the city's established infrastructure."
        ),
    },

    "lyon_retail_shell": {
        "display_name": "Retail Shell – Lyon Airport Commercial Design",
        "category": "Interior Design",
        "location": "Lyon, France",
        "year": "2019",
        "client": "Vinci Airports",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "Not disclosed",
        "capacity": "Not disclosed",
        "cost": "400,000 €",
        "video_url": "",
        "tagline": (
            "A flexible retail framework designed to diversify airport commerce and empower "
            "independent brands."
        ),
        "overview": (
            "In 2019, 1PAX was commissioned by Vinci Airports to develop a commercial design concept "
            "for Lyon Airport, responding to an innovative retail strategy aimed at diversifying the "
            "terminal's commercial offer. The brief focused on creating a 'ready-made shop' shell that "
            "could accommodate short-term sub-concession contracts, enabling smaller and independent "
            "brands to enter an environment traditionally dominated by large international retailers. "
            "The project delivered a highly flexible and cost-effective retail solution that supports "
            "commercial diversity and experimentation, receiving positive feedback from both clients "
            "and users as a replicable model for future airport retail environments."
        ),
        "key_challenge": (
            "Airport retail environments often suffer from visual and experiential uniformity due to "
            "standardised global brands and rigid fit-out models. Lyon Airport sought to break this "
            "monotony by introducing a system that could adapt quickly to different tenants, brand "
            "identities, and spatial requirements — without requiring extensive construction works or "
            "long implementation times."
        ),
        "approach": (
            "1PAX proposed a modular furniture-based retail concept capable of generating multiple "
            "shop typologies within a single architectural framework. The system was designed to be "
            "fully customisable, allowing each tenant to express a distinct atmosphere while maintaining "
            "overall coherence within the terminal. A key feature was a mobile partition system that "
            "enabled the retail surface to expand or contract, adapting the shop's footprint to "
            "operational needs and commercial strategies."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Lyon Retail Shell is a fundamentally circular retail concept: by designing for "
            "adaptability and reuse, the modular system dramatically reduces construction waste and "
            "embodied carbon compared to traditional full fit-out renovations with each tenant change. "
            "The mobile partition system and modular furniture can be reconfigured without demolition, "
            "directly reducing resource consumption. Lowering barriers for independent, local brands "
            "also supports economic diversity and reduces reliance on high-carbon global supply chains "
            "for retail fitment."
        ),
        "status": "Design completed — 2019",
        "tender_result": "Direct commission by Vinci Airports",
        "scope": "Retail concept design — modular 'ready-made shop' shell for Lyon Airport, enabling short-term sub-concession contracts and diversified retail with mobile partition system",
        "program": (
            "• Modular furniture-based retail concept generating multiple shop typologies\n"
            "• Mobile partition system enabling retail surface expansion and contraction\n"
            "• Customisable framework allowing each tenant to express distinct identity\n"
            "• Short-term sub-concession contract compatibility\n"
            "• Design for independent and smaller brands — not just large international retailers"
        ),
        "fun_facts": (
            "• The Lyon Retail Shell challenges the traditional airport retail model — dominated by large international chains with expensive, fixed fit-outs — by creating a system accessible to independent and local brands.\n"
            "• The mobile partition system means the shop can literally change size depending on the tenant or season — without any demolition or construction work.\n"
            "• Lyon Airport (Saint-Exupéry) is named after Antoine de Saint-Exupéry — the author of 'The Little Prince' and himself a pioneering aviator — making commercial innovation in its terminal a particularly resonant pursuit."
        ),
    },

    "aik_bank_design": {
        "display_name": "AIK Bank – Branches and ATM Network Design",
        "category": "Interior Design",
        "location": "Serbia (nationwide)",
        "year": "2025",
        "client": "AIK Bank",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "Over 60 offices and 400 ATMs nationwide",
        "capacity": "Serving over 300,000 clients",
        "cost": "Not disclosed",
        "video_url": "https://vimeo.com/1166381476/cebca128a9?share=copy&fl=sv&fe=ci",
        "tagline": (
            "Translating a renewed brand identity into a coherent, technology-driven customer "
            "experience across a nationwide banking network."
        ),
        "overview": (
            "In 2025, following a major brand transformation, AIK Bank commissioned 1PAX to design "
            "the exterior and interior concept for its entire network of branches and ATMs across "
            "Serbia. The scope encompassed more than 60 offices nationwide and approximately 400 ATMs "
            "— representing the bank's primary physical touchpoints with over 300,000 clients. The "
            "assignment aimed to transform the new brand vision into a consistent, functional, and "
            "recognisable spatial experience. The project delivered a strong, recognisable spatial "
            "identity that successfully translated AIK Bank's brand renewal into built form, improving "
            "customer experience, strengthening brand presence nationwide, and providing a flexible "
            "framework for future growth."
        ),
        "key_challenge": (
            "The core challenge was to ensure uniformity and clarity across a large and diverse "
            "network while allowing each branch and ATM to deliver a modern, welcoming, and efficient "
            "customer experience. The design needed to reflect AIK Bank's renewed identity, integrate "
            "evolving digital banking technologies, and remain adaptable to different urban and "
            "architectural contexts throughout the country."
        ),
        "approach": (
            "1PAX began with an in-depth research and analysis phase, working closely with AIK Bank's "
            "leadership and key stakeholders to understand the institution's culture, values, and "
            "strategic ambitions. Based on this foundation, the team developed a design concept defined "
            "by consistency, simplicity, and legibility. Innovative materials and integrated "
            "technologies were employed to enhance usability and comfort, while a comprehensive signage "
            "system and graphic language ensured visual coherence across all branches and ATMs. Every "
            "element — from façades to interiors and interfaces — was conceived as part of a unified "
            "customer journey."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The AIK Bank nationwide design system embeds sustainability through standardisation: a "
            "single coherent material and design language across 60+ branches reduces procurement "
            "complexity, enables bulk sustainable material sourcing, and ensures consistent "
            "energy-performance standards across the entire network. The integration of digital banking "
            "technologies reduces the need for paper-based processes and physical infrastructure, while "
            "the adaptable design framework allows branches to evolve with technology without full "
            "demolition and reconstruction."
        ),
        "status": "Design completed — 2025",
        "tender_result": "Direct commission by AIK Bank",
        "scope": "Interior and exterior concept design for entire AIK Bank branch and ATM network — 60+ offices and 400 ATMs nationwide across Serbia",
        "program": (
            "• Exterior concept for 60+ branch offices\n"
            "• Interior design concept for all branches\n"
            "• ATM design and integration for approximately 400 units nationwide\n"
            "• Comprehensive signage system and graphic language\n"
            "• Innovative materials and integrated digital banking technologies\n"
            "• Unified customer journey from façade to interface"
        ),
        "fun_facts": (
            "• AIK Bank is one of Serbia's largest and most established banking institutions — the scale of the design commission (60+ offices, 400 ATMs) makes this one of the largest single interior design networks 1PAX has ever undertaken.\n"
            "• The project followed a major brand transformation at AIK Bank — 1PAX's role was to translate that brand renewal into every physical touchpoint of the bank's customer-facing presence.\n"
            "• Designing a consistent experience across 60+ offices in a diverse national context — urban and rural, large and small — required a design system flexible enough to adapt while remaining unmistakably AIK Bank."
        ),
    },

    "cayenne_interior_design": {
        "display_name": "Félix Eboué Cayenne Airport – Interior Design",
        "category": "Interior Design",
        "location": "Cayenne, French Guiana",
        "year": "2023",
        "client": "EDEIS COLAS",
        "architect": "1PAX",
        "partners": "Ingerop",
        "area": "25,000 m²",
        "capacity": "Not disclosed",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Shaping a bioclimatic interior that reflects local identity while enhancing comfort, "
            "orientation, and passenger well-being."
        ),
        "overview": (
            "In 2023, as part of its comprehensive involvement in the Félix Eboué Cayenne Airport "
            "project, 1PAX developed the interior design concept for the passenger terminal. "
            "Commissioned by EDEIS COLAS in collaboration with Ingerop, the scope covered all key "
            "public and operational spaces including departure and arrival halls, boarding areas, "
            "commercial zones, food court, and the airport health centre. The proposal reinforces the "
            "terminal's architectural coherence while creating a welcoming, climate-responsive "
            "environment rooted in the context of French Guiana — an interior vision that strengthens "
            "the airport's role as a contemporary, human-centred gateway to French Guiana."
        ),
        "key_challenge": (
            "Designing interior spaces for a tropical airport required balancing passenger comfort "
            "with environmental performance. The challenge lay in creating an identity-rich interior "
            "capable of accommodating diverse functions and passenger flows, while minimising energy "
            "demand and responding effectively to local climatic conditions such as heat, humidity, "
            "and intense sunlight."
        ),
        "approach": (
            "1PAX developed an interior strategy grounded in sustainability and bioclimatic principles. "
            "The design emphasised the use of durable, low-impact materials, integrated vegetation, "
            "and the strategic use of natural ventilation and daylight. Particular attention was given "
            "to the canopy area, where sunlight was carefully modulated and celebrated as a spatial "
            "element, transforming circulation zones into a memorable sensory experience. The overall "
            "layout supported intuitive movement and visual continuity across the terminal."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Cayenne Airport interior design is built on bioclimatic principles suited to French "
            "Guiana's tropical climate. Natural ventilation strategies reduce reliance on mechanical "
            "cooling, while carefully controlled daylighting through the canopy minimises artificial "
            "lighting demand. Integrated vegetation improves indoor air quality and connects passengers "
            "to the natural environment of French Guiana. The use of durable, low-impact materials "
            "extends the interior's service life, reducing the frequency and cost of future renovations."
        ),
        "status": "Design completed — 2023",
        "tender_result": "Direct commission by EDEIS COLAS",
        "scope": "Interior design concept for 25,000 m² passenger terminal at Félix Eboué Cayenne Airport — all public and operational spaces including departure/arrival halls, boarding areas, commercial zones, food court, and health centre",
        "program": (
            "• Departure and arrival halls interior design\n"
            "• Boarding areas and gate zones\n"
            "• Commercial zones and food court\n"
            "• Airport health centre\n"
            "• Canopy area with modulated daylight as spatial design element\n"
            "• Durable, low-impact materials with integrated vegetation throughout"
        ),
        "fun_facts": (
            "• The Cayenne Airport interior design covers 25,000 m² — an unusually large scope for a single interior design commission, spanning every public zone from arrivals to gates.\n"
            "• The canopy area is designed to 'celebrate' natural light — using tropical sunlight as an active spatial element rather than managing it purely as a thermal challenge.\n"
            "• 1PAX's involvement at Cayenne spans five projects: terminal extension, masterplan, Air Guyane hangar, office buildings, and this interior design — making Cayenne Airport arguably the most comprehensive single-site engagement in the firm's portfolio."
        ),
    },

    "santiago_wayfinding": {
        "display_name": "Santiago International Airport – Wayfinding Design & Signage",
        "category": "Interior Design",
        "location": "Santiago de Chile, Chile",
        "year": "2019",
        "client": "Nuevo Pudahuel",
        "architect": "1PAX",
        "partners": "Not disclosed",
        "area": "200,000 m² (terminal coverage)",
        "capacity": "30 million passengers annually",
        "cost": "Not disclosed",
        "video_url": "",
        "tagline": (
            "Creating a clear, intuitive wayfinding system to support seamless navigation in one of "
            "South America's busiest airports."
        ),
        "overview": (
            "In 2019, 1PAX was commissioned by Nuevo Pudahuel to design the wayfinding and signage "
            "system for Santiago International Airport (SCL/AMB) — a major aviation hub serving up "
            "to 30 million passengers annually. The scope focused on developing a coherent visual "
            "guidance strategy across a large-scale 200,000 m² terminal environment, ensuring "
            "consistency, clarity, and ease of navigation for both domestic and international "
            "travellers. The resulting wayfinding system significantly enhanced passenger orientation, "
            "reduced confusion, and improved overall terminal legibility, supporting smoother passenger "
            "journeys and a cohesive airport identity consistent with Santiago's role as a major "
            "regional and global gateway."
        ),
        "key_challenge": (
            "The primary challenge was to deliver a wayfinding system capable of guiding diverse "
            "passenger profiles through a 200,000 m² terminal with efficiency and minimal cognitive "
            "effort. The system needed to balance international best practices with local operational "
            "requirements, integrate multilingual communication, and strictly comply with the ADP "
            "Graphics Manual, while remaining legible, intuitive, and adaptable to changing "
            "passenger flows."
        ),
        "approach": (
            "1PAX developed a comprehensive signage strategy based on clear visual hierarchies, colour "
            "coding, and standardised graphic rules. Flight-related instructions were designed using "
            "black text on yellow backgrounds, while service information employed white text on blue "
            "backgrounds — ensuring immediate recognition. The system integrated ADP lettering "
            "standards alongside VINCI visual references, with precise placement of arrows, text, "
            "pictograms, alphanumeric codes, and time charts. All signage content was presented in "
            "Spanish with English translations, reinforcing accessibility and international usability."
        ),
        "five_star_detail": (
            "N/A — this project does not pursue a 5-Star certification. "
            "For 1PAX's 5-Star airport design expertise, ask about the Sofia Airport project."
        ),
        "sustainability": (
            "The Santiago wayfinding system uses a standardised, colour-coded graphic language that "
            "can be efficiently updated and extended as the airport evolves, avoiding costly full "
            "replacements. The system's alignment with ADP Graphics Manual and VINCI standards ensures "
            "compatibility with future terminal expansions. Effective wayfinding reduces passenger "
            "congestion at key decision points, improving HVAC efficiency in crowded zones and "
            "supporting a more comfortable, lower-stress passenger environment at South America's "
            "busiest international gateway."
        ),
        "status": "Design completed — 2019",
        "tender_result": "Direct commission by Nuevo Pudahuel",
        "scope": "Wayfinding and signage design — comprehensive system for 200,000 m² terminal at Santiago International Airport serving 30 million passengers annually",
        "program": (
            "• Comprehensive wayfinding strategy for 200,000 m² terminal\n"
            "• Colour-coded visual hierarchy: black/yellow for flight instructions, white/blue for services\n"
            "• ADP lettering standards and VINCI visual references integration\n"
            "• Standardized placement of arrows, text, pictograms, alphanumeric codes, and time charts\n"
            "• Bilingual content — Spanish primary, English secondary"
        ),
        "fun_facts": (
            "• Santiago International Airport is South America's second busiest airport, serving 30 million passengers annually — making wayfinding clarity across 200,000 m² a mission-critical design challenge.\n"
            "• The colour-coding system — black text on yellow for flight information, white on blue for services — follows internationally proven cognitive principles that allow passengers to locate information in under 3 seconds.\n"
            "• 1PAX designed wayfinding systems for both Santiago (SCL) and Belgrade (BEG) in the same year (2019) — demonstrating the firm's expertise in large-scale airport navigation design at both European and South American scales."
        ),
    },

    # ── Add next project below ─────────────────────────────────────────────────
    # "project_key": {
    #     "display_name": "Full Project Name",
    #     "category": "Category Name",
    #     "location": "City, Country",
    #     "year": "YYYY–YYYY",
    #     "client": "Client Name",
    #     "architect": "1PAX + Partners",
    #     "partners": "Partner Firm",
    #     "area": "XX,XXX m²",
    #     "capacity": "...",
    #     "cost": "XX million €",
    #     "video_url": "https://...",
    #     "tagline": "...",
    #     "overview": "...",
    #     "key_challenge": "...",
    #     "approach": "...",
    #     "five_star_detail": "...",
    #     "sustainability": "...",
    # },
}

# Official public project pages and cover images from 1pax.com.
# Values are injected into every PROJECTS entry below as:
#   project_url, cover_image_url
PROJECT_MEDIA = {
    "sofia_airport": (
        "https://www.1pax.com/projects/sofia-airport-terminal-3-international-terminal-2-refurbishment",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b731a42dd546d2c4ab4c40_Sofia_2.webp",
    ),
    "belgrade_airport": (
        "https://www.1pax.com/projects/nikola-tesla-international-airport-phase-1-phase-2",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72d78c81fa27714a14af9_Belgrade_1.webp",
    ),
    "velana_airport": (
        "https://www.1pax.com/projects/velana-international-airport-new-terminal-building",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d620e795a4130c5cac9436_velana_night.webp",
    ),
    "bordeaux_airport": (
        "https://www.1pax.com/projects/new-stainless-steel-and-glazed-facades-bordeaux-international-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d64a0bd611f475c8bec76c_Bordeaux%204.webp",
    ),
    "cayenne_terminal": (
        "https://www.1pax.com/projects/felix-eboue-airport-new-terminal",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72cb5619866dcc244016a_Cayenne-Exterior-02.webp",
    ),
    "nice_airport": (
        "https://www.1pax.com/projects/nice-cote-dazur-airport-terminal-boarding-gates-expansion",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b731f435af8d0cca357cb3_Nice_2.webp",
    ),
    "pointe_a_pitre_t1": (
        "https://www.1pax.com/projects/pointe-a-pitre-international-airport-new-extension",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72f97ec7dba6c9452347e_Vue%203D%201%20-%20Hall%20D%C3%A9parts.webp",
    ),
    "pointe_a_pitre_t2": (
        "https://www.1pax.com/projects/pointe-a-pitre-international-airport-t2-extension",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d610336cab42ba47db2676_guadeloupe_aerial_render.webp",
    ),
    "annecy_airport": (
        "https://www.1pax.com/projects/annecy-general-aviation-terminal",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72e5180d08e6d6e510972_Annecy_2.webp",
    ),
    "conakry_airport": (
        "https://www.1pax.com/projects/conakry-international-airport-expansion",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72dbae6d9b9532301b1e7_Conakrys_2.webp",
    ),
    "papeete_airport": (
        "https://www.1pax.com/projects/papeete-faa-a-international-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7316fdb6fe97935439f29_Papeete_4.webp",
    ),
    "amilcar_cabral_airport": (
        "https://www.1pax.com/projects/cabo-verde-assistance-for-the-concession-of-7-airports",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b727a49925d9a7b373b7e0_Amilcar_1%20(1).webp",
    ),
    "nelson_mandela_airport": (
        "https://www.1pax.com/projects/cabo-verde-assistance-for-the-concession-of-7-airports",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b727a49925d9a7b373b7e0_Amilcar_1%20(1).webp",
    ),
    "aristides_pereira_airport": (
        "https://www.1pax.com/projects/cabo-verde-assistance-for-the-concession-of-7-airports",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b727a49925d9a7b373b7e0_Amilcar_1%20(1).webp",
    ),
    "lille_airport": (
        "https://www.1pax.com/projects/lille-international-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72f688d878d06e00234dc_Lille_2.webp",
    ),
    "fuzhou_airport": (
        "https://www.1pax.com/projects/fuzhou-airport-international-airport-terminal-rail-integration-",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72a8988365294c2f38404_Fuzhou_1.webp",
    ),
    "euroairport_modernization": (
        "https://www.1pax.com/projects/euroairport-terminal-modernization",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72a5a8f681919e0a217b6_Mulhouse_6.webp",
    ),
    "lanzhou_airport": (
        "https://www.1pax.com/projects/lanzhou",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7301579e21070d9c173a3_lanzhou1.webp",
    ),
    "mashhad_airport": (
        "https://www.1pax.com/projects/new-mashad-international-airport-extension-terminal",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b731c5e1292ea5e551606c_Mashad-01.webp",
    ),
    "almaty_airport": (
        "https://www.1pax.com/projects/almaty-international-airport-masterplanning-new-terminal-design",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72e724700d7158543d179_Almaty.webp",
    ),
    "euroairport_south_gates": (
        "https://www.1pax.com/projects/euroairport-extension-terminal-south-gates",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72a6f069714d69034a913_Euroair_2.webp",
    ),
    "kigali_airport": (
        "https://www.1pax.com/projects/kigali-new-passenger-terminal-building-consultancy-for-redesign-construction",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2be542976bbd777155517_Kigali_1.jpg",
    ),
    "tocumen_airport": (
        "https://www.1pax.com/projects/tocumen-international-airport-consultancy-fire-safety-strategy-review",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b3fafbf3969991400e90d7_Tocumen_2.jpg",
    ),
    "cusco_airport": (
        "https://www.1pax.com/projects/alejandro-velasco-astete-airport-rehabilitation-extension-diagnostic-",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d7b4449f60716e22551587_google_earth_cusco.webp",
    ),
    "jaipur_airport": (
        "https://www.1pax.com/projects/jaipur-international-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d6ac4e0dd895bc1d0da1a5_google_earth_jaipur.webp",
    ),
    "ahmedabad_airport": (
        "https://www.1pax.com/projects/ahmedabad-airport-consultancy",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d6acb773d69e3bc4a7f594_google_earth_ahmedabad.webp",
    ),
    "pachacamac_metro_station": (
        "https://www.1pax.com/projects/intermodal-metro-station-pachacamac-line-1-extension",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d8b2a87755f2a8d574c03b_Metro_Per_1%20(1).webp",
    ),
    "belgrade_metro_line1": (
        "https://www.1pax.com/projects/belgrade-metro-network-line-1-phase-1",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7343bb732de7af410ceb5_bgmetro.webp",
    ),
    "cergy_vertiport": (
        "https://www.1pax.com/projects/first-european-taxidrone-vertiport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d4dfccb94d9642209085d5_vertiport_4.webp",
    ),
    "singapore_vertiport": (
        "https://www.1pax.com/projects/vertiport-in-singapore",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b44d9cd3afdad6dce9a72e_singapore1.png",
    ),
    "paris_heliport": (
        "https://www.1pax.com/projects/heliport-de-paris-issy-les-molineaux",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d76245f8aabbfab1b6b5df_issy-heliport.webp",
    ),
    "cabo_verde_airports": (
        "https://www.1pax.com/projects/cabo-verde-assistance-for-the-concession-of-7-airports",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b727a49925d9a7b373b7e0_Amilcar_1%20(1).webp",
    ),
    "belgrade_nikola_tesla_landside": (
        "https://www.1pax.com/projects/nikola-tesla-airport-landside-design-vehicles-simulation",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d615b56c1e2de287a3369f_Belgrade_Landside_2.webp",
    ),
    "lima_metro_line1_stations": (
        "https://www.1pax.com/projects/lima-metro-line-1-multimodal-station-sizing-urban-insertion--1w2pu",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d8b295f2040f9d17241d8f_google_earth_pachacamac.webp",
    ),
    "cayenne_airport_masterplan": (
        "https://www.1pax.com/projects/feliz-eboue-airport-masterplan",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69dcf4f2db67f97b2d5459be_google_earth_cayenne.webp",
    ),
    "doha_metro_depot": (
        "https://www.1pax.com/projects/qatar-railways-alwakrah-metro-depot-masterplan",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69de74420ca661665cea20ad_al-whakra.webp",
    ),
    "chateauroux_atct_mro": (
        "https://www.1pax.com/projects/chateauroux-atct-mro",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2afe492addfb0541456e2_chateroux-02.png",
    ),
    "riga_control_tower": (
        "https://www.1pax.com/projects/riga-international-airport-new-control-tower-offices",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69c552917361e01b677045ae_Riga_1.webp",
    ),
    "belgrade_fire_station": (
        "https://www.1pax.com/projects/belgrade-airport-main-fire-station-architectural-design",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2ba7de00d9e5080393719_Belgrade_1.jpg",
    ),
    "cdg_baggage_building": (
        "https://www.1pax.com/projects/design-building-for-baggage-handling-charles-de-gaulle-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2afa3621256fe7061c72d_Baggage_1.jpg",
    ),
    "le_bourget_fire_station": (
        "https://www.1pax.com/projects/new-fire-station-paris-le-bourget-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b2b9ddc150ff948a740ce0_Paris_3.jpg",
    ),
    "air_guyane_hangar": (
        "https://www.1pax.com/projects/hangar-for-air-guyanne-cayenne-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72bf63ca1a998b25176fe_Cayenne-Hangar-01.webp",
    ),
    "belgrade_admin_building": (
        "https://www.1pax.com/projects/belgrade-airport-administration-building",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b733d28c80a0d49cb846ed_Belgrade_Adm_4.webp",
    ),
    "tokyo_eu_delegation": (
        "https://www.1pax.com/projects/european-commission-building-new-delegation-building-architectural-design",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b733a7646bd86ef340abda_Europe_Comm_3.webp",
    ),
    "french_embassy_bangkok": (
        "https://www.1pax.com/projects/french-embassy-in-bangkok-architectural-design",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b733809925d9a7b374c1cb_Ambassy_1.webp",
    ),
    "qatar_railways_hq": (
        "https://www.1pax.com/projects/qatar-railways-headquarters",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7334adf2e8e3a6210d367_hqqatar.webp",
    ),
    "montijo_airport_commercial": (
        "https://www.1pax.com/projects/montijo-airport-passenger-experience-design-commercial-areas",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7366186bba992b516bd74_Montijo%203.webp",
    ),
    "jorge_chavez_food_hall": (
        "https://www.1pax.com/projects/food-hall-design-jorge-chavez-international-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69d7832fed48e1679fac071b_perufood.webp",
    ),
    "lima_peru_plaza_food_court": (
        "https://www.1pax.com/projects/peru-airport-food-court-look-and-feel",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b737d507c7d17ce8c931e6_Plaza%2010.webp",
    ),
    "marseille_commercial_assistance": (
        "https://www.1pax.com/projects/aeroport-de-marseille-provence-architectural-assistance-for-the-commercial-facilities-implementation",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7368dd93944d5c17044c5_Marseille%203.webp",
    ),
    "belgrade_wayfinding": (
        "https://www.1pax.com/projects/nikola-tesla-international-airport-wayfinding-signage-design",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7376c20d86875e8bbc19d_Nikola%201.webp",
    ),
    "nantes_commercial_zone": (
        "https://www.1pax.com/projects/nantes-atlantique-airport-development-of-the-commercial-zone",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b7363e2dd546d2c4abb90f_Nantes%205.webp",
    ),
    "lyon_retail_shell": (
        "https://www.1pax.com/projects/retail-shell-lyon-airport-commercial-design",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b735152e926afdfcea29ee_Retail%201.webp",
    ),
    "aik_bank_design": (
        "https://www.1pax.com/projects/aik-bank-branches-atm-network-design",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b735673d3153253073c288_Bank%203.webp",
    ),
    "cayenne_interior_design": (
        "https://www.1pax.com/projects/felix-eboue-cayenne-airport",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b72aae415b59c2d80a939c_Int%C3%A9rieures%205.webp",
    ),
    "santiago_wayfinding": (
        "https://www.1pax.com/projects/santiago-international-airport-wayfinding-design-signage",
        "https://cdn.prod.website-files.com/698a41cf3248593467beb7ef/69b737fb18420a09e87493df_Santiago%201.webp",
    ),
}

for _key, _project in PROJECTS.items():
    _url, _cover_image = PROJECT_MEDIA.get(_key, ("", ""))
    _project["project_url"] = _url
    _project["cover_image_url"] = _cover_image

# Category index — automatically built from PROJECTS, no manual maintenance needed.
# Maps category name → list of project keys.
CATEGORIES: dict = {}
for _key, _project in PROJECTS.items():
    _cat = _project["category"]
    CATEGORIES.setdefault(_cat, []).append(_key)
