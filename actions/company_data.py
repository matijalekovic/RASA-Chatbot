"""
1PAX Company Information — Structured Response Data
====================================================
All answers to customer/visitor questions about 1PAX as a studio.
Source: company_info_raw.txt

Each key maps to one or more chatbot response messages.
Multi-part responses are lists; single messages are strings.
"""

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
            "solutions. We don't just respond to the future; we help define it."
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
            "We are proud to maintain long-standing partnerships with many of our clients — relationships "
            "built on genuine collaboration and shared goals, not just project delivery. We embrace "
            "our clients' ambitions as our own and anticipate their future needs so we can grow together."
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
            "We are seeking forward-thinking individuals to join our global studio in:\n\n"
            "Architecture · Interior Design · Planning · Landscape Architecture · Urbanism · "
            "3D & Graphic Design · Innovation\n\n"
            "1PAX is a place for those who believe design can shape a better world — proof that "
            "architecture and innovation can drive social progress, that multidisciplinary collaboration "
            "can solve complex challenges, and that anyone with passion and purpose can make a "
            "meaningful impact."
        ),
        (
            "**What we offer:**\n"
            "• Continuous mentorship from senior team members, including our founder\n"
            "• Real responsibility on major infrastructure projects\n"
            "• Flexible remote-work policies\n"
            "• A collaborative, international, multicultural studio environment\n"
            "• A Graduate Fellowship Program for students and recent graduates\n\n"
            "To apply or learn more, visit [1pax.com](https://1pax.com)."
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
    ],

    "open_roles": [
        (
            "**1PAX is currently seeking talent in:**\n\n"
            "• Architecture\n"
            "• Interior Design\n"
            "• Planning\n"
            "• Landscape Architecture\n"
            "• Urbanism\n"
            "• 3D & Graphic Design\n"
            "• Innovation\n\n"
            "We welcome forward-thinking individuals at all career stages. Students and recent graduates "
            "should explore our **Graduate Fellowship Program**. "
            "To see open positions, visit [1pax.com](https://1pax.com)."
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
