# Masari Phase 2 Story
## A Data Science Project That Becomes a Product Pitch

---

## One-Sentence Pitch

**Cairo built new transport systems for the city it wants to become. Twenty million people still move through the city that already exists. We mapped the gap between the two, and found a product opportunity inside it.**

That is the whole project. Every scene below exists to make that sentence feel inevitable.

---

## Scene 1 - The Woman Before the Map
### The point: start with a life, not a dataset

Layla lives in Imbaba.

She works in a clinic in Maadi.

Every morning at 6:15, before Cairo has fully woken up, she starts a commute that a transport analyst would call a "three-transfer intermodal journey." Layla would never call it that. She calls it going to work.

She walks to a microbus stop. She pays cash. No app tells her when the microbus comes. No sign tells her where it stops. No published timetable confirms whether today will be normal or strange. She knows because she has learned, by repetition, which driver waits near which corner, which metro entrance is less crowded, which transfer is bearable, and which one steals fifteen minutes from her day.

Then she reaches Metro Line 2. Then she transfers. Then she walks again.

One trip takes about one hour and forty minutes. Twice a day, five days a week, it becomes more than three hours of daily uncertainty. In a year, Layla gives Cairo the equivalent of weeks of unpaid labor, just by trying to arrive on time.

The important part is not that Layla suffers. The important part is that Layla is skilled.

She holds a private map of Cairo that no authority has captured. Millions of riders do. They know informal routes, cash fares, waiting habits, safe transfers, bad intersections, Friday exceptions, school-day crowding, and the invisible rules that make Cairo move.

That knowledge is not in GTFS.

It is not in Google Maps.

It is not in a government PDF.

It is in people.

**The project begins here: Cairo does not only have a transport gap. It has a knowledge gap.**

---

## Scene 2 - The City Changed Faster Than Its People Could
### The point: show the scale of construction before revealing the mismatch

For fifteen years, Cairo has been building.

Metro Line 3 pushed west and east. The LRT connected the edge of Cairo to the New Administrative Capital. BRT arrived on the Ring Road. Monorail projects promised driverless links to new desert cities. National rail upgrades continued around old spines like Ramses Station.

The official story is easy to tell:

- More stations.
- More corridors.
- More formal systems.
- More investment.
- More maps with clean colored lines.

It looks like progress because, in many ways, it is progress.

But the people did not move as quickly as the concrete.

Imbaba did not become a desert suburb. Shubra did not empty out. Old Cairo did not stop being dense. Informal settlements did not dissolve because a new rail line opened somewhere else. Workers still needed to reach clinics, schools, offices, workshops, malls, kitchens, warehouses, and homes that were not designed around the new network.

The city changed on paper.

The commute changed on foot.

And those are not the same thing.

This is the tension Phase 2 investigates:

**Did Cairo's new infrastructure reach the Cairo that actually exists, or the Cairo planners hope will exist later?**

---

## Scene 3 - Phase 1 Found the Bruises
### The point: connect the old project to the new one

Phase 1 asked a direct question:

**Where are Cairo's transport gaps?**

It did not begin with Masari. It did not begin with a product. It began as an audit.

Phase 1 gave us four kinds of evidence:

- Underserved population cells: places where many people live but service is weak.
- Ghost terminals: terminals that exist in the network but do not attract enough real boarding demand.
- Empty-return pressure: vehicles that return without enough passengers, wasting capacity and money.
- Vehicle-route mismatch: small vehicles doing work that should belong to larger, more efficient systems.

Phase 1 was a diagnosis. It told us where the pain was.

But a diagnosis is not a story yet.

The story starts when we ask what happened next.

Because after the 2018 baseline, Cairo did not sit still. It invested billions in new infrastructure. That gave Phase 2 its sharper question:

**When Cairo built new systems, did those systems close the gaps Phase 1 found?**

That question sounds technical. It is not.

It is Layla asking:

**Did any of this reach me?**

---

## Scene 4 - The First Map Lied Beautifully
### The point: set up expectation, then break it

At first, the maps looked encouraging.

We loaded the formal network: metro stations, LRT stations, BRT stations, GTFS stops, OSM transport features, and integrated formal-mode points. Then we overlaid them on Phase 1's terminals and population data.

The map was full.

There were dots everywhere. Lines, stations, terminals, clusters, corridors. It looked like a city being connected.

That was the first trap.

A full map is not the same as a useful map.

When we separated the layers, the story changed. The formal stations were visible, documented, and often beautifully aligned with planned corridors. The informal network was dense, messy, practical, and closer to where daily demand already exists. The two systems touched, but they did not fully speak.

That is when the project changed direction.

We stopped asking, "How much did Cairo build?"

We started asking:

**Where did Cairo build, compared with where Cairo lives?**

---

## Scene 5 - The Adly Mansour Surprise
### The point: reveal the planning axis

Then one station kept appearing.

Adly Mansour.

Metro Line 3 reaches it. The LRT begins there. BRT connects near it. It sits on the eastern planning axis toward the New Administrative Capital. It has become a symbolic hinge between old Cairo and the Cairo being built in the desert.

On paper, Adly Mansour is a triumph of integration.

One node. Multiple modes. A gateway to the future.

But the data forced a harder question:

**A gateway for whom?**

When we compared the node to population density and Phase 1 demand, the answer was less triumphant. Adly Mansour is important, but it is not where Cairo's highest everyday need concentrates. It is a planned convergence, not necessarily a demand convergence.

That distinction matters.

A planning convergence is where systems meet because institutions decided they should.

A demand convergence is where systems need to meet because people already do.

Adly Mansour tells us what Cairo is planning.

Layla tells us what Cairo is living.

The gap between those two is the project.

---

## Scene 6 - The Empty Train Was Not the Villain
### The point: make the LRT finding nuanced, not simplistic

It would be easy to say the LRT failed because trains ran empty.

That would be too simple.

The better question is not whether the LRT is bad. The better question is whether the LRT was placed in front of existing demand or ahead of future demand.

Our analysis could not measure ridership directly. So we measured something the data could support: population within walking catchment.

For every LRT station, we estimated the population within 2 km using Phase 1 population hexes. Then we compared that with recent Metro Line 3 stations.

The result was the project's first major twist:

**The LRT did not appear to be built for the densest Cairo of today. It was built for a corridor of tomorrow.**

That does not make the LRT useless. It makes it speculative.

It is infrastructure as a bet.

But Layla's commute is not speculative. It happens every morning.

This is the moral tension of the project:

**Cairo is building for future residents while current residents are still solving yesterday's commute by memory.**

---

## Scene 7 - The BRT Complication
### The point: avoid a one-note argument; show that some planning is demand-responsive

Just when the story seemed obvious, BRT complicated it.

If every new mode missed existing demand, the project would be cleaner. It would also be less honest.

BRT along the Ring Road showed signs of a different pattern. When we buffered BRT stations and counted nearby Phase 1 informal demand, some stations landed near real existing corridors. In those places, BRT looks less like a prestige project and more like formalization: the state recognizing where informal movement already existed and trying to structure it.

That matters because it saves the story from becoming lazy.

The claim is not:

**All new infrastructure is wrong.**

The claim is:

**New infrastructure works best when it learns from the informal city instead of pretending the informal city is a problem to erase.**

BRT becomes the proof that formal and informal systems can meet.

It also becomes the template for Masari:

Do not replace local knowledge.

Capture it. Validate it. Route through it. Improve it.

---

## Scene 8 - The Two Cairos
### The point: name the central framework

By this point, the data no longer looked like one transport system.

It looked like two Cairos.

### System A: the planned Cairo

Metro. LRT. BRT. Monorail. National rail. Official stations. Published fares. Project phases. Clean geometries. Press releases. GTFS feeds. Operator pages. Maps that look legible.

System A is visible to institutions.

### System B: the lived Cairo

Microbuses. Minibuses. Informal stops. Cash fares. Driver memory. Passenger memory. Negotiated pickups. Unwritten transfer rules. Corridors that work because people collectively know how to use them.

System B is visible to riders.

The crisis is not that System A exists or that System B exists.

The crisis is that the rider often needs both.

Layla's commute is not formal or informal. It is both. Her trip crosses the boundary, and the boundary is exactly where the information breaks.

This is the deepest finding:

**The gap is not only geographic. The gap is informational.**

The city has routes.

The city has riders.

The city has data.

What it lacks is a bridge.

---

## Scene 9 - The Questions Become Evidence
### The point: make the notebook feel intentional, not like disconnected analysis

Every Phase 2 question serves one piece of the story.

| Question | What it proves for the story |
|---|---|
| Q13 | Metro expansion only partially follows dense population demand. |
| Q14 | New metro did not fully absorb Phase 1 ghost-terminal gaps. |
| Q15 | Metro grew over time, but growth alone does not prove gap closure. |
| Q16 | Fast-growing districts can still have weak new-mode coverage. |
| Q17 | Dense and underserved areas overlap enough to define a target market. |
| Q18 | Informal share is not just a density effect; informal service is citywide infrastructure. |
| Q18b | New modes leave large shares of Phase 1 gaps uncovered. |
| Q19 | The data ecosystem itself favors formal modes over informal reality. |
| Q20 | BRT is the positive exception: some stations align with existing informal demand. |
| Q21 | Informal travel can carry a higher per-km burden despite being the only practical option. |
| Q22 | District residuals reveal where population predicts more coverage than exists. |
| Q23 | Adly Mansour is a planned convergence, but not necessarily the highest-demand convergence. |
| Q24 | Clustering turns the gap into market segments for action. |

The hypotheses test the same story from three angles:

| Hypothesis | What it protects against |
|---|---|
| H1: coverage-need mismatch | Prevents the story from being only anecdotal. |
| H2: LRT catchment deficit | Prevents the LRT claim from being only journalistic. |
| H3: BRT corridor match | Prevents the project from becoming anti-infrastructure. |

Together, the questions say:

**Cairo's problem is not no infrastructure. It is misaligned infrastructure, incomplete information, and missing integration.**

---

## Scene 10 - The Product Was Hiding in the Residuals
### The point: make Masari feel discovered, not invented

At this point, a normal data project would end with recommendations.

Build more stations.

Improve planning.

Integrate informal transport.

Publish better data.

Those are true, but they are not enough.

The analysis points to something more specific:

**The most valuable missing asset is not another line. It is a live, rider-updated map of how Cairo actually moves.**

That is Masari.

Masari is not "Google Maps for Cairo" in the shallow sense. Google Maps already exists.

Masari is different because it starts from the part of Cairo Google Maps cannot see well: System B.

Masari would combine:

- Formal feeds: metro, BRT, LRT, rail, GTFS stops, fares, stations.
- Scraped public records: station lists, openings, operator updates, mode status.
- Phase 1-style demand evidence: population, terminals, boardings, underserved cells.
- Crowdsourced rider traces: actual microbus paths, waiting points, transfer patterns, cash fares, time-of-day reliability.

The product promise is simple:

**Tell Layla the route she can actually take, not the route a clean map wishes existed.**

---

## Scene 11 - What Masari Does
### The point: translate the analysis into product features

Masari answers questions that current tools struggle to answer:

- Which microbus gets me closest to the metro?
- How much cash do I need before I leave?
- Which transfer is fastest at 7:30 AM, not in theory but in practice?
- Is there a safer or less crowded path for this trip?
- If I have EGP 20, what route is still possible?
- If the metro is delayed, what informal alternative actually exists nearby?

The app has four product layers.

### 1. Formal network layer

Metro, LRT, BRT, rail, official stops, fare structures, and known station coordinates.

This is System A.

### 2. Informal route layer

Crowdsourced microbus and minibus paths, pickup points, drop-off zones, fare ranges, and time-of-day reliability.

This is System B.

### 3. Confidence layer

Not every informal route has the same certainty. Masari would show confidence levels:

- confirmed by many riders
- likely route
- low-confidence segment
- recently changed

This turns uncertainty into a feature instead of hiding it.

### 4. Planning intelligence layer

Aggregated, anonymized insights for planners, operators, universities, hospitals, employers, and mobility researchers:

- underserved commute corridors
- feeder demand around metro stations
- BRT stations with weak or strong informal demand
- district-level access gaps
- route-change impacts over time

Masari is free for riders because riders create the data.

The business sells insight, not the rider.

---

## Scene 12 - The Business Inverts the Inequity
### The point: show why the ignored places become the market

Most infrastructure strategies reward already planned places.

Masari does the opposite.

The districts with the weakest formal coverage are the districts where Masari is most useful. Imbaba, Shubra, Old Cairo, dense parts of Giza, and other complex commute districts become not "left behind" areas, but high-value markets.

This is the business inversion:

**The places formal planning underserves are the places where better information is worth the most.**

Masari does not need to wait for a new metro station to create value.

It creates value tomorrow morning by making the existing trip legible.

That is why the product follows naturally from the data.

If infrastructure is slow and expensive, information is fast and scalable.

If official maps lag reality, riders can update reality.

If Cairo already moves through System B, Masari can make System B visible.

---

## Scene 13 - The Three Visuals That Make the Story Land
### The point: define the visuals the presentation must build toward

The story needs many analyses, but only three visuals are climactic.

### Visual 1: The Two Cairos Map

One map with formal stations layered against population density and informal terminals.

The audience should see the split before we explain it:

- formal systems cluster along planned corridors
- dense demand clusters elsewhere
- informal terminals fill the spaces formal maps understate

This is the opening proof.

### Visual 2: The Adly Mansour Zoom

A close-up of the planning convergence:

- Metro Line 3
- LRT
- BRT
- informal terminals nearby
- population and boarding context

This is the emotional peak.

It shows how much infrastructure can meet in one place while the larger city still struggles to connect.

### Visual 3: The Coverage-Need Gap Map

A district map colored by:

`population / need percentile - new-mode coverage percentile`

Interpretation:

- dark red: high need, low coverage
- dark blue: low need, high coverage
- neutral: coverage and need roughly balanced

This is the payoff.

It shows where Masari starts.

---

## Scene 14 - The Pitch Opening
### The point: give the team a spoken hook

Do not open with the dataset.

Open with Layla.

> Layla lives in Imbaba. She works in Maadi. Every day she spends more than three hours getting between the two.
>
> In the last fifteen years, Cairo built new transport systems: metro extensions, LRT, BRT, monorail, and rail upgrades. On paper, the city became more connected.
>
> But when we mapped those systems against where people actually live and how they actually move, we found something unexpected. Cairo did not have one transport network. It had two: the planned network that appears on official maps, and the lived network that millions of riders carry in their heads.
>
> This project maps the gap between them.
>
> And that gap is the opportunity behind Masari.

Then show the hero map.

Let the audience see the gap before you name the product.

---

## Scene 15 - The Final Turn
### The point: end with a memorable thesis

The project began as a data science assignment.

It became a market-research report by accident.

We scraped stations, routes, district populations, GTFS files, vehicle estimates, and OSM transport features. We joined them with Phase 1's population, terminals, boardings, and underserved-score outputs. We tested whether the new city reached the lived city.

The answer was not simple.

Some infrastructure helps. Some infrastructure anticipates future demand. Some infrastructure misses current need. Informal transport is not a failure on the edge of the system. It is the system for millions of people.

That is why Masari is not a side idea.

It is the conclusion.

**Cairo does not need passengers to become data points. Cairo needs the knowledge passengers already have to become shared infrastructure.**

That is the product.

That is the pitch.

That is the story.

---

## Closing Line

**Cairo built the future in concrete. Masari builds the bridge from the present to that future, one real trip at a time.**

