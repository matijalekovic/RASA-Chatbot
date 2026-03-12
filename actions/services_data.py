"""
1PAX Services Information — Structured Response Data
=====================================================
All answers to customer/visitor questions about 1PAX's service offerings.
Source: services_raw.txt

Each key maps to one or more chatbot response messages.
Multi-part responses are lists; single messages are strings.
"""

SERVICES_INFO = {

    # ── Meta / full list ──────────────────────────────────────────────────────

    "services_list": [
        (
            "**1PAX offers eight core service areas**, spanning the full lifecycle of "
            "mobility infrastructure and architectural projects:"
        ),
        (
            "**1. Airports & Railstations** — Terminal programming, flow design, BHS feasibility, "
            "multimodal hubs, fire safety, and station design.\n\n"
            "**2. Urbanism & Masterplan** — Development strategy, airport city planning, traffic "
            "simulation, construction phasing, and security reviews.\n\n"
            "**3. Innovation & Patents** — Patented cart and furniture systems, licensing, passenger "
            "experience consulting, and commercial roll-out of proprietary innovations.\n\n"
            "**4. Future Mobility** — Vertiport and eVTOL facility design, urban mobility hubs, "
            "MaaS integration, and smart city advisory.\n\n"
            "**5. Control Towers & Ancillary Buildings** — ATCT site selection, visibility analysis, "
            "control room fit-out, and ancillary building design.\n\n"
            "**6. Interior Design & Retail** — Passenger journey guidelines, commercial strategy, "
            "\"Red Wire\" retail concept, wayfinding, and furniture design.\n\n"
            "**7. Working & Living** — Offices, embassies, mixed-use buildings, shopping centres, "
            "resorts, and urban regeneration projects.\n\n"
            "**8. BIM Project Management** — Revit modelling, clash detection, digital twins, "
            "BIM consulting, and work package delivery."
        ),
        (
            "Which area would you like to explore further? Just ask — for example: "
            "*\"What airport design services do you offer?\"* or *\"Tell me about your BIM capabilities.\"*"
        ),
    ],

    # ── 1. Airports & Railstations ────────────────────────────────────────────

    "airports": [
        (
            "**Airports & Railstations** is 1PAX's core service area — the domain we were built for."
        ),
        (
            "We provide end-to-end design and consulting services for airports, terminals, and "
            "rail/metro stations:\n\n"
            "- **Functional programming** — terminal capacity analysis, space allocation, and design briefs\n"
            "- **Passenger flow simulation** — peak-hour modelling, queue analysis, level-of-service optimisation\n"
            "- **Airside & landside masterplanning** — aircraft stands layout, taxiways, aprons, road access\n"
            "- **BHS feasibility** — baggage handling system layout, capacity sizing, and technology assessment\n"
            "- **Fire safety strategy** — compartmentation, evacuation routes, smoke control principles\n"
            "- **Multimodal hub design** — seamless integration of air, rail, metro, bus, and road\n"
            "- **Station design** — train and metro stations, circulation sizing, depot layout\n"
            "- **Greenfield & brownfield** — new-build terminal design and retrofit/extension of existing infrastructure\n"
            "- **Check-in, security, boarding gate & lounge sizing** — functional area programming throughout\n"
            "- **Wayfinding strategy** — circulation logic integrated from concept stage"
        ),
        (
            "Our airport portfolio spans 26 projects across 4 continents — from the "
            "**Sofia Airport T3** to **Bordeaux**, **Belgrade**, **Maldives**, **Tahiti**, and beyond.\n\n"
            "Want to know more about a specific aspect of our airport services, or see relevant project examples?"
        ),
    ],

    # ── 2. Urbanism & Masterplan ──────────────────────────────────────────────

    "urbanism": [
        (
            "**Urbanism & Masterplan** services at 1PAX address the broader strategic and planning "
            "dimensions of mobility infrastructure — from a single airport site to an entire airport city."
        ),
        (
            "Our urbanism and masterplanning capabilities include:\n\n"
            "- **Development strategy** — long-term land-use and infrastructure growth planning\n"
            "- **Airport city / aerotropolis planning** — mixed-use development around aviation hubs\n"
            "- **Road access & kerb-front planning** — vehicle access, drop-off/pick-up, parking strategy\n"
            "- **Aircraft circulation study** — taxiway geometry, apron layout, aircraft movement optimisation\n"
            "- **Vehicle swept-path & turn simulation** — service vehicle access and emergency route compliance\n"
            "- **Traffic forecast & modelling** — future demand projections to inform infrastructure sizing\n"
            "- **Construction phasing** — sequenced build programmes that maintain full airport operations\n"
            "- **Airport security review** — perimeter, access control, and checkpoint strategy consulting\n"
            "- **Urban regeneration** — planning and design around mobility infrastructure nodes\n"
            "- **Ancillary building coordination** — hotels, cargo facilities, maintenance zones"
        ),
        (
            "Examples include the **Greyfoot Paris** urban innovation district and masterplanning "
            "components embedded across our larger airport projects.\n\n"
            "Interested in a specific urban challenge or project type? Let me know."
        ),
    ],

    # ── 3. Innovation & Patents ───────────────────────────────────────────────

    "innovation": [
        (
            "**Innovation & Patents** is a distinctive service area that sets 1PAX apart — "
            "we don't just design spaces, we develop and commercialise proprietary solutions."
        ),
        (
            "Our innovation and patent services include:\n\n"
            "- **PAX (Passenger Assisted Experience)** — 1PAX's patented all-in-one mobility product: seat, cart, "
            "stroller, and stacking system in one elegant object. Patent: EU 4096986B1. Ask *'tell me about the PAX cart'* for full details.\n"
            "- **Modular airport furniture systems** — adaptable, scalable furniture solutions designed "
            "specifically for high-traffic airport environments\n"
            "- **Patent licensing** — we license our innovations to airport operators, retailers, and "
            "furniture manufacturers worldwide\n"
            "- **Passenger experience optimisation** — consulting on how spatial and product design "
            "can improve passenger satisfaction scores\n"
            "- **Commercial roll-out support** — from prototype to production, we support clients in "
            "deploying our patented designs\n"
            "- **Design research & prototyping** — R&D services for new mobility-related product concepts"
        ),
        (
            "If you are an airport operator, retailer, or manufacturer interested in licensing our "
            "innovations or commissioning bespoke product design, we'd love to talk.\n\n"
            "Would you like to know more about a specific patent or how licensing works?"
        ),
    ],

    # ── 4. Future Mobility ────────────────────────────────────────────────────

    "future_mobility": [
        (
            "**Future Mobility** is one of 1PAX's most forward-looking service areas — "
            "designing the infrastructure for how people will move tomorrow. "
            "This includes **Ecoport**, 1PAX's patented modular vertiport system (ask *'tell me about Ecoport'* for details)."
        ),
        (
            "Our future mobility services cover:\n\n"
            "- **Vertiport design** — full architectural design for eVTOL take-off and landing pads, "
            "passenger terminals, and ground-level facilities\n"
            "- **Heliport & urban air facility design** — existing and next-generation rotorcraft infrastructure\n"
            "- **Urban mobility hub integration** — seamlessly connecting air taxis, public transit, "
            "cycling, and pedestrian flows in a single hub\n"
            "- **AAM feasibility studies** — site selection, regulatory pathway, and business case "
            "for advanced air mobility operations\n"
            "- **Carbon-neutral infrastructure** — designing for net-zero operations from day one\n"
            "- **MaaS (Mobility as a Service)** — planning for digital integration between transport modes\n"
            "- **Smart city connectivity** — digital infrastructure advisory for connected mobility ecosystems\n"
            "- **Collaborative innovation** — working with eVTOL manufacturers and operators to define "
            "the operational and spatial requirements for next-gen facilities\n"
            "- **Passenger-centric design** — human-centred design principles applied to novel "
            "mobility typologies where no established precedent exists"
        ),
        (
            "Our portfolio includes the **Cergy Vertiport** (Paris region), **Singapore Vertiport**, "
            "and **Paris Heliport** — among the first dedicated vertiport design projects in Europe.\n\n"
            "Want to know more about eVTOL design standards, our approach, or a specific project?"
        ),
    ],

    # ── 5. Control Towers & Ancillary Buildings ───────────────────────────────

    "control_towers": [
        (
            "**Control Towers & Ancillary Buildings** — 1PAX designs the technical heart of airports: "
            "air traffic control towers and the specialist support buildings that keep operations running."
        ),
        (
            "Our services in this area include:\n\n"
            "- **ATCT site selection & masterplan** — determining the optimal tower location within "
            "the airport footprint based on operational and regulatory requirements\n"
            "- **Visibility cone analysis** — ensuring unobstructed line-of-sight to all runways and "
            "taxiways per ICAO/national authority standards\n"
            "- **Tower height determination** — technical calculations to meet visibility requirements\n"
            "- **Control room (cab) design** — ergonomics, console layout, glass specification, "
            "lighting, and acoustic design for the operational cab\n"
            "- **Technical block layout** — equipment rooms, UPS, comms, and services coordination\n"
            "- **Ancillary facilities** — carpark, access roads, emergency generator buildings\n"
            "- **Fire safety strategy** — egress design and compartmentation for tall structures\n"
            "- **Operational consulting** — collaborating with ANSP (air navigation service providers) "
            "to translate operational requirements into spatial design"
        ),
        (
            "Our portfolio includes the **Riga Control Tower** and **Châteauroux ATCT/MRO** complex.\n\n"
            "Interested in a specific technical aspect — visibility standards, cab ergonomics, "
            "or the procurement process for a new tower?"
        ),
    ],

    # ── 6. Interior Design & Retail ───────────────────────────────────────────

    "interior": [
        (
            "**Interior Design & Retail** — 1PAX shapes the experience passengers have from the moment "
            "they enter a terminal to the moment they board."
        ),
        (
            "Our interior design and retail services include:\n\n"
            "- **Passenger journey mapping** — defining the ideal experience at every touchpoint, "
            "from kerbside to gate\n"
            "- **Visual identity integration** — translating a terminal's brand and cultural identity "
            "into spatial and material language\n"
            "- **Commercial strategy (\"Red Wire\" concept)** — our proprietary method for creating "
            "a continuous commercial thread that guides passengers naturally through retail, F&B, and "
            "services zones — maximising dwell time and spend-per-passenger\n"
            "- **Wayfinding & signage** — complete sign systems designed for clarity, multilingual "
            "environments, and high passenger volumes\n"
            "- **Operational furniture** — check-in counters, information desks, kiosks, service desks "
            "designed for staff ergonomics and passenger interaction\n"
            "- **Lounge & relaxing furniture** — seating systems, gate-area furniture, and lounge "
            "furnishings tailored to dwell-time analysis\n"
            "- **F&B and retail unit layout** — concession planning, unit sizing, back-of-house access\n"
            "- **Fit-out consulting** — specifications and tender support for interior contractors"
        ),
        (
            "Our interior design portfolio includes the **Santiago Wayfinding** project, "
            "**Lima Peru Plaza Food Court**, **Jorge Chávez Food Hall**, and the "
            "**Montijo Airport commercial zone**, among others.\n\n"
            "Would you like to know about our commercial strategy approach, or a specific project?"
        ),
    ],

    # ── 7. Working & Living ───────────────────────────────────────────────────

    "working_living": [
        (
            "**Working & Living** — beyond aviation, 1PAX applies its design excellence to the "
            "buildings where people work, live, and gather."
        ),
        (
            "Our working and living services include:\n\n"
            "- **Head office & corporate campus** — workplace design that balances productivity, "
            "collaboration, and wellbeing\n"
            "- **Embassy & diplomatic mission design** — secure, representative buildings that balance "
            "security requirements with architectural quality and cultural diplomacy\n"
            "- **Mixed-use development** — integrating living, working, leisure, and green space "
            "within airport cities and urban regeneration zones\n"
            "- **Shopping centres & retail complexes** — large-scale retail environments designed "
            "for commercial performance and customer experience\n"
            "- **Resorts & hospitality** — hotel and resort design with a strong sense of place\n"
            "- **Airport city components** — residential, commercial, and civic buildings within "
            "aerotropolis developments\n"
            "- **Urban regeneration** — breathing new life into underused districts, often anchored "
            "by mobility infrastructure\n"
            "- **Public space design** — plazas, parks, and civic spaces that activate communities\n"
            "- **Sustainable design** — BREEAM, LEED, and HQE-aligned design from concept to handover"
        ),
        (
            "Portfolio highlights include the **Tokyo EU Delegation**, **French Embassy Bangkok**, "
            "**Belgrade Admin Building**, and **Qatar Railways HQ**.\n\n"
            "Looking for a specific building type or would you like to explore our approach to "
            "sustainable workplace design?"
        ),
    ],

    # ── 8. BIM Project Management ─────────────────────────────────────────────

    "bim": [
        (
            "**BIM Project Management** — 1PAX delivers fully coordinated digital models and "
            "BIM consulting services alongside our architectural and planning work."
        ),
        (
            "Our BIM capabilities include:\n\n"
            "- **Revit modelling** — architectural BIM in Autodesk Revit 2023/2024, from concept "
            "through to construction documentation\n"
            "- **Existing infrastructure 3D modelling** — survey data (point cloud) to federated BIM model\n"
            "- **Construction & demolition phasing** — 4D sequencing models for phased delivery in "
            "live operational environments\n"
            "- **Clash detection** — multi-discipline coordination (architectural, structural, MEP) "
            "to resolve conflicts before construction\n"
            "- **Discipline coordination** — federated model management across all project consultants\n"
            "- **Digital twin creation** — as-built BIM models configured for facilities management "
            "and asset lifecycle tracking\n"
            "- **BIM project management consulting** — BEP (BIM Execution Plan) preparation, "
            "Common Data Environment (CDE) setup, and BIM governance\n"
            "- **Sizing & design brief** — data-driven space programming fed directly from the BIM model\n"
            "- **Traffic forecast integration** — linking demand modelling outputs to spatial sizing\n"
            "- **Work package preparation** — contractor-ready model extracts, schedules, and "
            "coordination packages\n"
            "- **LOD (Level of Development) management** — clear deliverable standards at each project stage"
        ),
        (
            "Our BIM offer is used both as an integrated part of our architectural services and as "
            "a standalone consulting service for clients who need BIM expertise on complex infrastructure projects.\n\n"
            "Interested in our specific Revit standards, LOD specifications, or how we handle "
            "clash detection on live airport projects?"
        ),
    ],

    # ── Follow-up prompts (used across service responses) ────────────────────

    "follow_up": [
        "Want to know more, or shall I tell you about a specific project in this area?",
        "Any specific aspect you'd like to explore further?",
        "Happy to go deeper — what would be most useful to know?",
    ],

}
