"""
1PAX Team Members — Structured Response Data
=============================================
All answers to customer/visitor questions about the 1PAX team.
Source: team_raw.txt

TEAM_INFO  — group-level responses (overview + 5 groups)
PERSONS    — individual bios keyed by canonical person key
"""

# ── Group responses ────────────────────────────────────────────────────────────

TEAM_INFO = {

    "overview": [
        (
            "**The 1PAX team** brings together architects, planners, engineers, BIM specialists, "
            "visualization experts, and innovators — based in Paris, Belgrade, Shanghai, Barcelona, and Lima."
        ),
        (
            "**Leadership**\n"
            "Mabel Miranda · CEO & Founder  |  Ali Fawaz · Fractional CFO  |  "
            "Fabiola Espinoza · Business Development  |  Bashan Yang · Shanghai & Visualization  |  "
            "Carla Miranda · Communications & Innovation\n\n"
            "**Architects** (13)\n"
            "Claudia Cornejo · Hanh Nguyen · Pedro Martins Branco · Marija Stevanovic · Boris Stojnic · "
            "Diego Alonso Ampuero · Marko Soskic · Renzo Roncalla · Kevin Guzman · Yeniffer Cordero · "
            "Wendy Florian · Deysi Nuñez · Maria Fernanda Bojorquez\n\n"
            "**Specialists**\n"
            "Tiago Cobrado · Architectural Technologist  |  Matija Leković · AI & Digital Specialist\n\n"
            "**Studio Operations**\n"
            "Andreja Zrnovic · Design & Communications  |  Olenka Tamara · Administrative Assistant\n\n"
            "**Collaborators**\n"
            "Helene Henriot · Airport Planner  |  Christos Panagos · Architect & 3D Visualization"
        ),
        (
            "Want to know more about a specific person or group? Ask — for example: "
            "*\"Tell me about Mabel Miranda\"*, *\"Who are the architects?\"*, or *\"Who handles BIM?\"*"
        ),
    ],

    "leadership": [
        (
            "**1PAX Leadership Team** — five people guiding the studio's vision, operations, and growth:"
        ),
        (
            "**Mabel Miranda** — *CEO & Founder*\n"
            "Founded 1PAX in 2016. Educated at ESA and MIT (Urban Development predoctoral research). "
            "Born in Peru, she leads with a global perspective and a conviction that design can "
            "transcend social, economic, and geographic boundaries.\n\n"
            "**Ali Fawaz** — *Fractional CFO*\n"
            "Joined in 2023. Stewards budgets, contract reviews, invoicing, and progress tracking. "
            "Committed to healthy collaboration between architects and engineers.\n\n"
            "**Fabiola Espinoza** — *Business Development Manager*\n"
            "Civil engineer and BD leader. Trained in France and Switzerland. Experience across "
            "multilateral finance, underground engineering, and public-sector advisory in Latin "
            "America and Europe.\n\n"
            "**Bashan Yang** — *Shanghai Representative & Senior Visualization Expert*\n"
            "Over two decades in architectural visualization — from early digital modeling to "
            "real-time engines and AI. For Bashan, visualization is a precise narrative tool, "
            "not mere image-making.\n\n"
            "**Carla Miranda** — *Chief Communications & Innovation Officer / Barcelona Lead*\n"
            "Communications graduate with an MBA from ESADE. Cross-industry experience (retail, "
            "education, telecom, tourism). Leads communications strategy and 1PAX's innovation agenda."
        ),
        (
            "Want the full profile of any leader? Ask — for example: "
            "*\"Tell me about Fabiola Espinoza\"* or *\"Who is the CFO?\"*"
        ),
    ],

    "architects": [
        (
            "**1PAX Architects** — a team of 13 architects, project managers, and BIM specialists:"
        ),
        (
            "**Claudia Cornejo** — *Senior Project Manager* · 9 years at 1PAX · Architect + BIM Manager · Based in France\n"
            "**Hanh Nguyen** — *Architect* · 10 years in airport and terminal design · Multidisciplinary coordination\n"
            "**Pedro Martins Branco** — *Architect & Project Leader* · Lisbon → Amsterdam → Barcelona · Real estate studies\n"
            "**Marija Stevanovic** — *Airport Project Director* · 12+ years in aviation infrastructure · Tech integration specialist\n"
            "**Boris Stojnic** — *Construction Phasing Expert* · 8 years · Live airport delivery · Educated in Sydney\n"
            "**Diego Alonso Ampuero** — *Architect & BIM Modeler* · UPC-trained · Autodesk-certified · Revit / ArchiCAD / Lumion\n"
            "**Marko Soskic** — *Architect & BIM Manager* · ISO 19650 accredited · Chalmers University · 9 years\n"
            "**Renzo Roncalla** — *Architect* · 14 years · ETSAM–UPM Madrid · Retail, hospitality, interiors\n"
            "**Kevin Guzman** — *Architect & BIM Specialist* · Design as storytelling · Conceptual + technical\n"
            "**Yeniffer Cordero** — *BIM Modeler* · Revit specialist · Airports, offices, transport\n"
            "**Wendy Florian** — *Architect* · Airport + AAM projects · eVTOL / drone infrastructure experience\n"
            "**Deysi Nuñez** — *Architect Assistant* · BIM modeler · AutoCAD & Revit · Airport terminals\n"
            "**Maria Fernanda Bojorquez** — *Architectural Assistant* · Urban Design focus · Passenger experience"
        ),
        (
            "Want a full profile? Ask — for example: *\"Tell me about Marija Stevanovic\"* or "
            "*\"Who is the BIM Manager?\"*"
        ),
    ],

    "specialists": [
        (
            "**1PAX Specialists** — technical experts bridging architecture, digital technology, "
            "and construction:"
        ),
        (
            "**Tiago Cobrado** — *Architectural Technologist*\n"
            "Educated in Copenhagen, solid experience in the Danish market. Specializes in "
            "construction solutions, material systems, and technical development. Highly proficient "
            "in BIM workflows with a focus on detailing and buildable solutions.\n\n"
            "**Matija Leković** — *AI & Digital Specialist*\n"
            "Background in product management and full-stack AI development. Leads integration of "
            "intelligent systems across BIM and CAD workflows — developing automation tools, "
            "LLM-based solutions, and advanced visualization platforms. Bridges AI and architecture "
            "with precision and imagination."
        ),
        (
            "For the full profile of either specialist, just ask — "
            "*\"Tell me about Matija Leković\"* or *\"Tell me about Tiago Cobrado.\"*"
        ),
    ],

    "operations": [
        (
            "**Studio Operations** — the people who keep 1PAX running day to day:"
        ),
        (
            "**Andreja Zrnovic** — *Design & Communications*\n"
            "Four years at the intersection of software, industrial design, and architecture. "
            "Works on mobility and airport projects — bridges physical devices and digital "
            "platforms through concept development and UX thinking.\n\n"
            "**Olenka Tamara** — *Administrative Assistant*\n"
            "Background in Global Business Administration. Supports 1PAX's operations through "
            "thoughtful analysis, clear communication, and dependable coordination. Known for "
            "adaptability, empathy, and initiative."
        ),
    ],

    "collaborators": [
        (
            "**Collaborators** — external experts who partner with 1PAX on specific projects:"
        ),
        (
            "**Helene Henriot** — *Airport Planner*\n\n"
            "**Christos Panagos** — *Architect & 3D Visualization Expert*"
        ),
    ],

    "follow_up": [
        "Want to know more about any team member? Just ask!",
        "Curious about a specific person? Ask — for example: *\"Tell me about Boris Stojnic.\"*",
    ],

}


# ── Individual bios ────────────────────────────────────────────────────────────

PERSONS = {

    # ── Leadership ──────────────────────────────────────────────────────────────

    "mabel_miranda": {
        "display_name": "Mabel Miranda",
        "title": "CEO & Founder",
        "group": "Leadership",
        "bio": [
            (
                "**Mabel Miranda** — *CEO & Founder*\n"
                "Mabel Miranda founded 1PAX in 2016 from a conviction that design can meaningfully shape society."
            ),
            (
                "Born in Peru and guided by resilience and curiosity, she transformed early constraints "
                "into momentum for growth and impact.\n\n"
                "Educated at ESA and furthered by predoctoral research in Urban Development at MIT, she leads "
                "1PAX with a global perspective — demonstrating that thoughtful design can transcend social, "
                "economic, and geographic boundaries, and improve people's lives."
            ),
        ],
    },

    "ali_fawaz": {
        "display_name": "Ali Fawaz",
        "title": "Fractional CFO",
        "group": "Leadership",
        "bio": [
            (
                "**Ali Fawaz** — *Fractional CFO*\n"
                "Ali Fawaz joined 1PAX in 2023 as Fractional CFO, guiding financial and contractual "
                "management with steady oversight."
            ),
            (
                "He stewards budgets, contract reviews, invoicing, and progress tracking, while "
                "coordinating with partners to safeguard scope and timely delivery.\n\n"
                "Committed to balanced, healthy collaboration between architects and engineers, Ali helps "
                "create the financial clarity that complex projects require to thrive."
            ),
        ],
    },

    "fabiola_espinoza": {
        "display_name": "Fabiola Espinoza",
        "title": "Business Development Manager",
        "group": "Leadership",
        "bio": [
            (
                "**Fabiola Espinoza** — *Business Development Manager*\n"
                "Fabiola is a civil engineer and business development leader shaping mobility and "
                "infrastructure across Latin America and Europe."
            ),
            (
                "Trained in France and Switzerland, she bridges technical rigor with urban governance insight. "
                "Her experience spans multilateral finance, underground engineering, and public-sector "
                "advisory — guiding transport, energy, and sanitation projects from strategy to delivery.\n\n"
                "She approaches growth as a collaborative, systems-minded endeavor."
            ),
        ],
    },

    "bashan_yang": {
        "display_name": "Bashan Yang",
        "title": "Shanghai Representative & Senior Visualization Expert",
        "group": "Leadership",
        "bio": [
            (
                "**Bashan Yang** — *Shanghai Representative & Senior Visualization Expert*\n"
                "Bashan has over two decades of experience at the forefront of architectural visualization."
            ),
            (
                "Having evolved alongside the discipline — from early digital modeling to real-time engines "
                "and AI — he bridges architectural intent and client emotional buy-in.\n\n"
                "For Bashan, visualization is not mere image-making, but a precise narrative tool that "
                "sharpens design decisions and ensures the built result is both functional and "
                "enduringly compelling."
            ),
        ],
    },

    "carla_miranda": {
        "display_name": "Carla Miranda",
        "title": "Chief Communications & Innovation Officer / Barcelona Lead",
        "group": "Leadership",
        "bio": [
            (
                "**Carla Miranda** — *Chief Communications & Innovation Officer / Barcelona Office Lead*\n"
                "Strategic and socially driven, Carla leads communications with clarity, conviction, and purpose."
            ),
            (
                "A Communications graduate with an MBA from ESADE Business School, she brings a cross-industry "
                "perspective shaped by experience in retail, education, telecom, and tourism.\n\n"
                "As Communications Lead, she advances mission-driven initiatives, shaping narratives that "
                "elevate impact and connect vision to people. She also leads 1PAX's innovation strategy — "
                "transforming complex challenges into forward-thinking initiatives that deliver meaningful, "
                "lasting value."
            ),
        ],
    },

    # ── Architects ──────────────────────────────────────────────────────────────

    "claudia_cornejo": {
        "display_name": "Claudia Cornejo",
        "title": "Senior Project Manager",
        "group": "Architects",
        "bio": [
            (
                "**Claudia Cornejo** — *Senior Project Manager*\n"
                "For nine years, Claudia Cornejo has been a steady force at 1PAX, now serving as "
                "Senior Project Manager."
            ),
            (
                "Trained as an architect and specialized as a BIM Manager, she guides projects with "
                "structured clarity and collaborative spirit.\n\n"
                "Peruvian by birth and based in France since 2014, Claudia values each contribution — "
                "integrating diverse perspectives into cohesive, well-resolved outcomes."
            ),
        ],
    },

    "hanh_nguyen": {
        "display_name": "Hanh Nguyen",
        "title": "Architect",
        "group": "Architects",
        "bio": [
            (
                "**Hanh Nguyen** — *Architect*\n"
                "Hanh is an architect with ten years of experience focused on airport and passenger "
                "terminal design."
            ),
            (
                "She has developed a deep understanding of balancing creative vision with the technical "
                "precision and operational complexity these projects require.\n\n"
                "Passionate about transforming ideas into spaces that serve diverse communities, she "
                "champions collaboration, continuous improvement, and seamless coordination across "
                "disciplines."
            ),
        ],
    },

    "pedro_martins_branco": {
        "display_name": "Pedro Martins Branco",
        "title": "Architect & Project Leader",
        "group": "Architects",
        "bio": [
            (
                "**Pedro Martins Branco** — *Architect & Project Leader*\n"
                "Pedro is an architect and project manager exploring the architecture of contemporary "
                "metropolitan territories."
            ),
            (
                "With advanced studies in real estate investment and valuation, he bridges design vision "
                "and market insight.\n\n"
                "His path — from Lisbon to Amsterdam and Barcelona — reflects a cross-European perspective, "
                "grounding strategic thinking in cultural awareness and urban complexity."
            ),
        ],
    },

    "marija_stevanovic": {
        "display_name": "Marija Stevanovic",
        "title": "Airport Project Director",
        "group": "Architects",
        "bio": [
            (
                "**Marija Stevanovic** — *Airport Project Director*\n"
                "With over twelve years of experience shaping complex aviation infrastructure, Marija "
                "leads airport projects with clarity and precision."
            ),
            (
                "Specialized in airport technology integration and design coordination, she aligns "
                "operations, passenger experience, and innovation to create efficient, future-ready "
                "environments.\n\n"
                "A collaborative and passionate leader, she builds trusted long-term partnerships and "
                "guides multidisciplinary teams toward resilient solutions that support long-term growth "
                "and seamless performance."
            ),
        ],
    },

    "boris_stojnic": {
        "display_name": "Boris Stojnic",
        "title": "Architect & Construction Phasing Expert",
        "group": "Architects",
        "bio": [
            (
                "**Boris Stojnic** — *Architect & Construction Phasing Expert*\n"
                "With 8 years of experience, Boris specializes in construction phasing for complex "
                "aviation projects delivered within live operational environments."
            ),
            (
                "Educated in Sydney and shaped by work around the world, he aligns vision, "
                "functionality, and passenger experience with buildable precision.\n\n"
                "Driven by transforming ambitious concepts into efficient, elegant realities, he "
                "views contributing to aviation as both a privilege and a responsibility — shaping "
                "infrastructures that connect people, cultures, and economies."
            ),
        ],
    },

    "diego_alonso_ampuero": {
        "display_name": "Diego Alonso Ampuero",
        "title": "Architect & BIM Modeler",
        "group": "Architects",
        "bio": [
            (
                "**Diego Alonso Ampuero** — *Architect & BIM Modeler*\n"
                "Diego is an architect and BIM modeler trained at the Peruvian University of Applied "
                "Sciences (UPC), certified in BIM Architecture Modelling by Autodesk."
            ),
            (
                "He combines precise 3D modeling with a photographer's eye, moving fluidly between "
                "ArchiCAD, Revit, AutoCAD, and Lumion.\n\n"
                "Diego approaches design as a dialogue between clarity, technology, and lived experience."
            ),
        ],
    },

    "marko_soskic": {
        "display_name": "Marko Soskic",
        "title": "Architect & BIM Manager",
        "group": "Architects",
        "bio": [
            (
                "**Marko Soskic** — *Architect & BIM Manager*\n"
                "With nine years of experience, Marko bridges architecture and information management "
                "with precision and passion."
            ),
            (
                "As an accredited BIM Manager (ISO 19650), he brings structure to complexity — "
                "overseeing data, documentation, and coordination across projects in Europe, the "
                "Caribbean, South America, and Australia.\n\n"
                "Educated in Belgrade and at Chalmers University of Technology, he pairs technical "
                "rigor with an international perspective shaped by life in Stockholm, Paris, and Belgrade."
            ),
        ],
    },

    "renzo_roncalla": {
        "display_name": "Renzo Roncalla",
        "title": "Architect",
        "group": "Architects",
        "bio": [
            (
                "**Renzo Roncalla** — *Architect*\n"
                "Renzo brings fourteen years of experience and advanced studies at ETSAM–UPM (Madrid)."
            ),
            (
                "Working across retail, hospitality, and interiors, he delivers functional, coherent "
                "design grounded in technical coordination and site leadership.\n\n"
                "Born in Peru and seasoned through international practice, Renzo pairs creativity and "
                "perseverance with a positive, detail-driven mindset — valuing trust, collaboration, "
                "and shared purpose at 1PAX."
            ),
        ],
    },

    "kevin_guzman": {
        "display_name": "Kevin Guzman",
        "title": "Architect & BIM Specialist",
        "group": "Architects",
        "bio": [
            (
                "**Kevin Guzman** — *Architect & BIM Specialist*\n"
                "Kevin is an architect and BIM specialist who bridges technical precision with "
                "creative intent."
            ),
            (
                "He develops projects that are both efficient and conceptually driven, shaping robust "
                "systems that reinforce strong design narratives.\n\n"
                "For Kevin, architecture is a form of storytelling — crafting immersive environments "
                "with distinct identities that prioritize user experience and foster meaningful, "
                "lasting connections between people and place."
            ),
        ],
    },

    "yeniffer_cordero": {
        "display_name": "Yeniffer Cordero",
        "title": "BIM Modeler",
        "group": "Architects",
        "bio": [
            (
                "**Yeniffer Cordero** — *BIM Modeler*\n"
                "Yeniffer specializes in BIM modeling and architectural design, working primarily in Revit."
            ),
            (
                "Engaging with diverse project typologies — from airports and office buildings to "
                "integrated transport systems — she approaches each new challenge as an opportunity "
                "for growth.\n\n"
                "Resilient and collaborative, Yeniffer believes that shared encouragement strengthens "
                "both professional development and collective team success."
            ),
        ],
    },

    "wendy_florian": {
        "display_name": "Wendy Florian",
        "title": "Architect",
        "group": "Architects",
        "bio": [
            (
                "**Wendy Florian** — *Architect*\n"
                "Wendy is an architect and BIM modeler with experience in airport and advanced air "
                "mobility projects, and experience collaborating with international teams on terminals "
                "around the world."
            ),
            (
                "Specialized in modeling, coordination, and technical documentation, she combines "
                "construction precision with clear visual communication.\n\n"
                "Meticulous and collaborative, she has also contributed to 1PAX's innovation projects — "
                "exploring infrastructure for drones and eVTOLs."
            ),
        ],
    },

    "deysi_nunez": {
        "display_name": "Deysi Nuñez",
        "title": "Architect Assistant",
        "group": "Architects",
        "bio": [
            (
                "**Deysi Nuñez** — *Architect Assistant*\n"
                "Deysi is an architect and BIM modeler with focused experience in airport passenger terminals."
            ),
            (
                "Proficient in AutoCAD and Revit, she advances projects through precise drafting, "
                "technical documentation, and graphic development.\n\n"
                "With a keen interest in architectural design and 3D modeling, Deysi prioritizes "
                "accuracy and efficiency — ensuring complex environments are both carefully resolved "
                "and thoughtfully articulated."
            ),
        ],
    },

    "maria_fernanda_bojorquez": {
        "display_name": "Maria Fernanda Bojorquez",
        "title": "Architectural Assistant",
        "group": "Architects",
        "bio": [
            (
                "**Maria Fernanda Bojorquez** — *Architectural Assistant*\n"
                "Maria approaches urban design with clarity, curiosity, and thoughtful intent."
            ),
            (
                "With a strong focus on Urban Design, she contributes at 1PAX to projects shaped by "
                "the complexities of cities and mobility systems.\n\n"
                "Motivated by enhancing passenger experience, she develops interventions that elevate "
                "functionality and efficiency — advancing transportation environments that are "
                "responsive, human-centered, and attuned to contemporary urban life."
            ),
        ],
    },

    # ── Specialists ─────────────────────────────────────────────────────────────

    "tiago_cobrado": {
        "display_name": "Tiago Cobrado",
        "title": "Architectural Technologist",
        "group": "Specialists",
        "bio": [
            (
                "**Tiago Cobrado** — *Architectural Technologist*\n"
                "Educated in Copenhagen and with solid experience in the Danish market, Tiago "
                "specializes in construction solutions, material systems, and technical development."
            ),
            (
                "He is highly proficient in BIM workflows and contributes across all phases of "
                "technical documentation.\n\n"
                "With a particular focus on detailing, he is committed to developing practical, "
                "well-considered, and buildable solutions that combine robustness with visual refinement."
            ),
        ],
    },

    "matija_lekovic": {
        "display_name": "Matija Leković",
        "title": "AI & Digital Specialist",
        "group": "Specialists",
        "bio": [
            (
                "**Matija Leković** — *AI & Digital Specialist*\n"
                "Matija bridges architecture and advanced technology as 1PAX's AI & Digital Specialist."
            ),
            (
                "With a background in product management and full-stack AI development, he leads the "
                "integration of intelligent systems across BIM and CAD workflows — developing automation "
                "tools, LLM-based solutions, and advanced visualization platforms.\n\n"
                "Driven by the evolving intersection of AI and architecture, he balances precision with "
                "imagination, advancing intelligent processes that enhance creativity, improve efficiency, "
                "and generate long-term value."
            ),
        ],
    },

    # ── Studio Operations ────────────────────────────────────────────────────────

    "andreja_zrnovic": {
        "display_name": "Andreja Zrnovic",
        "title": "Design & Communications",
        "group": "Studio Operations",
        "bio": [
            (
                "**Andreja Zrnovic** — *Design & Communications*\n"
                "Andreja brings four years of experience at the intersection of software, industrial "
                "design, and architecture."
            ),
            (
                "With hands-on work in mobility and airport projects, he approaches complex systems "
                "through concept development and UX thinking.\n\n"
                "His human-centered mindset bridges physical devices and digital platforms, shaping "
                "intuitive, efficient solutions grounded in real behavior rather than surface aesthetics."
            ),
        ],
    },

    "olenka_tamara": {
        "display_name": "Olenka Tamara",
        "title": "Administrative Assistant",
        "group": "Studio Operations",
        "bio": [
            (
                "**Olenka Tamara** — *Administrative Assistant*\n"
                "Olenka is an Administrative Assistant with a background in Global Business "
                "Administration and experience across commercial and administrative functions."
            ),
            (
                "She supports 1PAX's operations through thoughtful analysis and dependable coordination.\n\n"
                "Recognized for her adaptability, empathy, and clear communication, she approaches "
                "dynamic environments with focus and initiative — contributing to team goals and "
                "sustainable growth."
            ),
        ],
    },

    # ── Collaborators ────────────────────────────────────────────────────────────

    "helene_henriot": {
        "display_name": "Helene Henriot",
        "title": "Airport Planner",
        "group": "Collaborators",
        "bio": [
            (
                "**Helene Henriot** — *Airport Planner*\n"
                "Helene is an Airport Planner who collaborates with 1PAX on aviation planning projects."
            ),
        ],
    },

    "christos_panagos": {
        "display_name": "Christos Panagos",
        "title": "Architect & 3D Visualization Expert",
        "group": "Collaborators",
        "bio": [
            (
                "**Christos Panagos** — *Architect & 3D Visualization Expert*\n"
                "Christos is an architect and 3D visualization expert who collaborates with 1PAX "
                "on architectural visualization projects."
            ),
        ],
    },

}
