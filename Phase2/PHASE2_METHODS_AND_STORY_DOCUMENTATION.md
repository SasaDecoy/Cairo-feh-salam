# Phase 2 Methods And Story Documentation

## Purpose Of This Document

This report explains the logic behind the two Phase 2 notebooks:

- `Phase2_Scraping_Cleaning.ipynb`
- `Phase2_Analysis_Hypothesis.ipynb`

The goal is not only to say **what** the code does, but also:

- **why** each source, method, question, and hypothesis was used
- **how** each part helps build the notebook
- **what kind of insight** each part gives us
- **how** those insights support the final story of the project

This is the document you can use when writing your report, explaining your notebook in class, or defending your choices in a presentation or viva.

---

## 1. The Big Logic Of Phase 2

Phase 2 is designed as a two-notebook pipeline:

1. **Notebook 1: Scraping, Cleaning, Integration**
   - collect data from multiple real-world sources
   - clean and standardize it
   - build outputs that can be trusted and reused
   - integrate new-mode transport data with Phase 1 terminal data

2. **Notebook 2: Analysis, Questions, Hypotheses**
   - consume the cleaned outputs from Notebook 1
   - answer research questions
   - test formal hypotheses
   - produce visuals and insights
   - connect the technical analysis to the project story

So the full research flow is:

**real data -> cleaned datasets -> integrated transport layer -> questions -> hypotheses -> insights -> story**

That is why this is a real data-science project: it includes data collection, cleaning, feature building, integration, analysis, testing, interpretation, and storytelling.

---

## 2. Why We Split The Work Into Two Notebooks

We do not mix scraping with analysis in one notebook because that would make the project harder to understand and harder to debug.

### Why Notebook 1 exists

Notebook 1 exists to answer:

- Where did the data come from?
- How was it scraped?
- How was it cleaned?
- What assumptions were made?
- What files were produced for later analysis?

### Why Notebook 2 exists

Notebook 2 exists to answer:

- What does the cleaned data mean?
- What patterns are visible?
- Are the project claims supported statistically?
- Which findings help the story?

### Why this split helps the project

- It makes the workflow reproducible.
- It separates engineering work from analytical work.
- It allows Notebook 2 to depend only on outputs, not on live scraping.
- It makes the project easier to explain in a report.

---

## 3. Notebook 1: Why Each Source Was Used

Notebook 1 is the evidence-building notebook. Every source was selected because it fills a specific gap in the story.

### S1. TfC GTFS

**What it is:**
Transport for Cairo GTFS feed, mainly used for stops, routes, trips, shapes, and fare data.

**Why we use it:**

- to get structured public transport data in machine-readable format
- to support later questions about route coverage and fare per kilometer
- to provide a formal-network baseline

**Why GTFS is useful in the notebook:**

- it already has a tabular structure
- it is standardized
- it is easier to clean than free text or HTML

**What it gives us:**

- `gtfs_stops.csv`
- `gtfs_routes.csv`
- `gtfs_trips.csv`
- `gtfs_shapes.csv`
- `gtfs_fare_attributes.csv`

**How it helps the story:**

GTFS helps us compare the **formal published network** with the lived transport reality from Phase 1. It supports the idea that data availability and official transport structure are not the same thing as accessibility on the ground.

---

### S3. Wikipedia Metro Master List

**What it is:**
A station list for Cairo Metro with English names, Arabic names, coordinates, and opening dates.

**Why we use it:**

- to build the metro station inventory
- to identify lines and phases
- to support timeline and coverage questions

**Why this source is useful:**

- it gives both names and coordinates
- it includes opening dates, which are important for historical analysis
- it helps separate older metro investments from newer expansions

**What it gives us:**

- `metro_stations.csv`

**How it helps the story:**

Metro is central to the project story because it represents the formal state-led expansion of transport infrastructure. This dataset allows us to ask whether new metro phases actually reached high-demand areas.

---

### S4. Wikipedia LRT

**What it is:**
A station list for Cairo LRT, including operational and planned stations.

**Why we use it:**

- to build an LRT inventory
- to compare LRT with newer metro lines
- to test whether LRT serves strong or weak catchments

**Why it is useful:**

- it gives named stations even when other official structured files are not available
- it supports a major project question about whether LRT serves real population demand

**What it gives us:**

- `lrt_stations.csv`

**How it helps the story:**

LRT is one of the most important systems in the story because it symbolizes eastward investment. It helps us examine whether infrastructure was built where population demand already existed, or where demand is still speculative.

---

### S5. Google Maps BRT Scrape

**What it is:**
A custom scraping workflow using Google Maps search results to find BRT stations.

**Why we use it:**

- because BRT is very new and not well documented in clean official table form
- because OSM and Wikipedia coverage are incomplete
- because we still need a BRT station list to include it in the analysis

**Why this method was chosen:**

- Google Maps often indexes real stations before formal structured sources are updated
- it can reveal names and coordinates through search-result HTML

**What supporting techniques are used here:**

- regex parsing of coordinates
- canonical URL parsing
- Arabic and English search queries
- transliteration
- deduplication

**What it gives us:**

- `brt_stations.csv`

**How it helps the story:**

BRT helps answer whether all new infrastructure is equally weak, or whether some of it may actually align with existing demand. It is important because it gives a contrast to the LRT story.

---

### S6. citypopulation.de

**What it is:**
Administrative population data for Egypt and Greater Cairo districts across multiple years.

**Why we use it:**

- to measure population size
- to measure district growth
- to support density and underservedness analysis

**Why it is useful:**

- it provides multi-year population data
- it allows growth calculations
- it gives district-level demographic context

**What it gives us:**

- `districts.csv`
- `districts_wide.csv`

**How it helps the story:**

This source lets us connect transport investments to people. Without population data, we cannot ask whether infrastructure went where growth and need actually existed.

---

### S7. Vehicle Data: Wikipedia + World Bank

**What it is:**
A national vehicle total from Wikipedia and historical per-capita indicators from the World Bank.

**Why we use it:**

- to approximate motorization levels
- to study whether private vehicle availability relates to informal transport dependence

**Why this source is needed:**

- direct governorate-level transport vehicle data is hard to scrape consistently
- these two sources provide a usable fallback for national and historical context

**What it gives us:**

- `vehicles_by_governorate.csv`

**How it helps the story:**

Vehicle ownership helps frame transport choice. If motorization is high in some places and informal share is low there, it helps explain substitution patterns. If not, it shows informal transport is not just a poor substitute but a structural necessity.

---

### S8. OpenStreetMap Overpass

**What it is:**
OSM transport nodes queried through Overpass.

**Why we use it:**

- to independently verify station coordinates
- to provide an external transport-feature layer
- to help recover missing location information

**Why it is useful:**

- OSM gives a separate source from Wikipedia and Google Maps
- it acts as a cross-verification layer
- it helps check whether scraped locations are plausible

**What it gives us:**

- `osm_features.geojson`

**How it helps the story:**

OSM makes the project more credible because it is not relying on only one source family. It adds triangulation.

---

## 4. Notebook 1: Why We Use These Methods

Notebook 1 is not just scraping. It uses several methods because raw transport data is messy, multilingual, and spatial.

### 4.1 CRS handling

**Why we use `EPSG:32636`:**

- because distance-based work must be done in meters
- because nearest-neighbor joins and buffers need a projected CRS

**Why we keep `EPSG:4326`:**

- because web maps and many scraped coordinates arrive in lat/lon

**What this gives us:**

- correct distance calculations
- consistent geospatial logic across notebooks

---

### 4.2 Bounding box filtering

**Why we use a Cairo bounding box:**

- to remove irrelevant national or regional transport points
- to make the cleaned data focused on the study area

**What this gives us:**

- a more relevant dataset
- less noise
- faster downstream analysis

---

### 4.3 Transliteration with uroman

**Why we use transliteration instead of translation:**

- place names need phonetic matching, not meaning matching
- "المرج" should become something like "almrj", not a semantic English word

**What it gives us:**

- better Arabic/English name comparison
- better deduplication of station names

**Why this matters for the project:**

Without transliteration, multilingual station matching becomes much weaker.

---

### 4.4 Deduplication

**Why we deduplicate BRT and other scraped rows:**

- one station can appear multiple times in different languages
- slightly different pins can describe the same location
- repeated rows distort later counts and maps

**What dedup gives us:**

- a cleaner station inventory
- more believable counts
- less map clutter

---

### 4.5 KNN nearest-neighbor matching

**Why we use KNN in integration:**

- because many transport features need to be compared spatially
- because the nearest known terminal is often the best first spatial candidate

**What it gives us:**

- Stage 1 spatial pairing
- a first pass on whether new-mode stations sit near old terminals

**Why this helps the story:**

It helps answer whether new infrastructure overlaps with or bypasses the transport geography identified in Phase 1.

---

### 4.6 OSM cross-verification

**Why we verify against OSM:**

- scraped coordinates can be wrong
- Wikipedia or Google hits may be approximate
- independent validation is necessary for credibility

**What it gives us:**

- a discrepancy flag
- stronger confidence where sources agree

---

### 4.7 RapidFuzz

**Why we use fuzzy matching:**

- station names often differ slightly
- punctuation, spacing, transliteration, and spelling vary

**What it gives us:**

- a strong baseline for same-script name matching
- a quick and interpretable similarity measure

**Why it is not enough alone:**

- it struggles with cross-script cases
- it cannot fully solve Arabic vs English semantic name differences

---

### 4.8 SBERT multilingual semantic matching

**Why we use SBERT:**

- because fuzzy matching is weak for multilingual and semantic name differences
- because we need a better cross-script matching method

**What it gives us:**

- a semantic similarity score
- a way to compare combined Arabic and English station names

**Why it matters to the notebooks:**

This is the "AI technique" used to improve integration quality. It is included not as decoration, but because record linkage across scripts is one of the real technical problems in the project.

**Important caution:**

This method is useful, but only if thresholds and validation are strong enough. If the threshold is too low, it can create false matches.

---

### 4.9 Null audit

**Why we build a null audit:**

- to see which columns are complete and which are weak
- to understand whether missingness is acceptable or dangerous

**What it gives us:**

- `null_audit.csv`
- a quality summary for each cleaned output

**Why this matters to the story:**

It helps us speak honestly about data quality. That makes the project more defensible.

---

### 4.10 Manifest and final gate

**Why we use a manifest:**

- to show every output file produced by Notebook 1
- to make the handoff to Notebook 2 explicit

**Why we use a final gate:**

- to stop Notebook 2 from running on incomplete outputs

**What it gives us:**

- reproducibility
- cleaner project structure

---

### 4.11 How The Code Is Structured In Notebook 1

This subsection explains the code design itself, not only the methods.

### Why Notebook 1 is written in sections

Notebook 1 is written as a sequence of source blocks because each block answers one technical question:

- how do we fetch this source?
- how do we clean it?
- what file does it produce?
- how will Notebook 2 use it?

This sectioned code design is important because it makes the notebook readable as both:

- a research pipeline
- a technical appendix

### Why code cells are paired with markdown explanation cells

The markdown cells before each code block are used to explain:

- what source or method is being used
- why it is needed
- what assumptions are being made
- what output it should produce

This helps turn the notebook into documentation, not just execution.

### Why many Notebook 1 code cells follow the same pattern

Most source blocks follow the same internal logic:

1. define source URL or query
2. check whether a cached raw file already exists
3. fetch the raw data if needed
4. parse and clean the raw data
5. standardize the schema
6. save the output to `CleanedData/`
7. print a summary for auditing

### Why this repeated pattern is useful

It helps us in four ways:

- makes every source block easy to understand
- makes debugging easier when one source fails
- makes the notebook reproducible
- makes the handoff to Notebook 2 clearer

### Why we save outputs as files instead of keeping everything in memory

We save outputs because:

- Notebook 2 should not depend on rerunning live scraping
- cleaned files are easier to audit than hidden in-memory variables
- the project becomes more modular

### Why the notebook prints row counts and summaries

The print statements are not only for convenience. They are used to:

- check whether a scrape succeeded
- catch obviously wrong row counts
- compare sources before and after cleaning
- create a visible audit trail

### Why the integration code is staged

The integration logic is divided into stages because matching is not one single problem.

- **Stage 1** uses distance
- **Stage 2** uses cross-verification
- **Stage 3** uses fuzzy text matching
- **Stage 4** uses semantic multilingual matching

The code is structured this way because each stage solves a different weakness in the previous one.

### What this code structure gives to the notebook

It gives the notebook:

- technical discipline
- explainability
- reproducibility
- a strong transition into Notebook 2

---

## 5. Why Notebook 2 Uses Questions And Hypotheses

Notebook 2 mixes two kinds of analysis on purpose.

### Questions

Questions are used when we want to:

- explore a pattern
- compare systems
- describe a relationship
- show evidence visually

Questions are more descriptive and exploratory.

### Hypotheses

Hypotheses are used when we want to:

- formally test a claim
- compare groups statistically
- move from story intuition to evidence

Hypotheses are more inferential and argumentative.

### Why both are needed

If we only use questions, the notebook is descriptive but weak on formal testing.  
If we only use hypotheses, the notebook becomes dry and disconnected from the broader story.  
Using both allows the notebook to be both readable and rigorous.

---

### 5.1 How The Code Is Structured In Notebook 2

Notebook 2 is not written as one long analysis stream. It is structured as a sequence of analytical modules.

### Why the notebook opens with shared helpers

The notebook begins with:

- imports
- theme variables
- reusable plotting helpers
- path loading
- core assertions

This is done so that the rest of the notebook can focus on analysis rather than repeating setup code.

### Why the notebook loads outputs from Notebook 1 first

This design is important because Notebook 2 is supposed to be a consumer notebook.

That means:

- Notebook 1 produces the cleaned and integrated datasets
- Notebook 2 uses them as stable inputs

This separation makes the analysis more reliable and easier to explain.

### Why each analytical section follows the same code logic

Most question and hypothesis sections follow this structure:

1. explain the question
2. explain why it matters
3. load or derive the needed subset of data
4. build the metric
5. run the test or comparison
6. visualize the result
7. write an insight paragraph

### Why this structure is useful

It helps the notebook do three jobs at once:

- analysis
- explanation
- storytelling

### Why helper functions are important

Helper functions in Notebook 2 are used to:

- keep figure styling consistent
- reuse projection logic
- reduce repeated code
- make the notebook cleaner to read

### Why some sections use direct calculations and others use models

The notebook deliberately mixes:

- simple descriptive calculations
- spatial joins and buffers
- statistical tests
- clustering models

This mix is useful because not every question needs the same level of method complexity.

### What this code structure gives to the notebook

It gives Notebook 2:

- modularity
- readability
- easier interpretation
- a stronger connection between code and narrative

---

## 6. Notebook 2: Why Each Question Was Used

Below is the role of each question in the notebook.

### Q13. Metro coverage x density

**Why we ask it:**

- to check whether metro expansion followed dense districts
- to see whether newer lines are serving where people already are

**Why we use this method:**

- correlation is appropriate when we want to see whether denser areas align with station placement

**What this gives us:**

- a first look at whether planning and density move together

**How it helps the story:**

It starts the argument about whether investment followed need.

---

### Q14. Ghost terminals near new metro

**Why we ask it:**

- because Phase 1 found underused terminals
- we want to know whether new metro explains that underuse

**Why distance-based analysis is used:**

- this is a spatial substitution question
- proximity is the most direct first test

**What this gives us:**

- evidence about whether new metro relieved old weak terminals

**How it helps the story:**

It connects Phase 1 directly to Phase 2.

---

### Q15. Metro km vs terminal ratio over time

**Why we ask it:**

- to frame changing investment priorities historically
- to compare rail expansion with the older terminal network

**Why we use a time series:**

- because the key question is how the balance evolved, not just a snapshot

**What this gives us:**

- a planning-history view

**How it helps the story:**

It supports the idea that investment direction changed over time.

---

### Q16. Fastest-growing districts and coverage

**Why we ask it:**

- growth is a key sign of where future demand exists
- if fast-growing districts lack coverage, that is an important planning gap

**Why growth is used:**

- because raw population alone does not show momentum
- growth highlights emerging demand

**What this gives us:**

- a demographic demand map

**How it helps the story:**

It helps justify why unmet demand is not only present now, but likely to matter in the future.

---

### Q17. Population density vs underserved score

**Why we ask it:**

- to test whether underservedness is simply a density issue
- or whether it is a deeper coverage mismatch

**Why a monotonic association is used:**

- because we want to know whether denser areas systematically become more underserved

**What this gives us:**

- a clearer definition of the kind of gap the project is studying

**How it helps the story:**

It helps define the core market problem: not just density, but density plus weak coverage.

---

### Q18. Informal transport share by density

**Why we ask it:**

- to understand whether informal transport concentrates only in dense zones or is structurally widespread

**Why this matters:**

- if informal transport is everywhere, then it is not marginal
- it is part of the city's real transport system

**What this gives us:**

- evidence about the scale and structural importance of the informal network

**How it helps the story:**

It strengthens the "two systems" narrative.

---

### Q18b. Motorization vs informal share

**Why we ask it:**

- to see whether private motorization reduces dependence on informal transport

**Why it is included:**

- because transport choice is partly economic and behavioral, not only geographic

**What it gives us:**

- broader socioeconomic context

**How it helps the story:**

It helps explain whether informal transport survives only where private alternatives are weak, or whether it remains important everywhere.

---

### Q19. GTFS coverage: formal vs paratransit

**Why we ask it:**

- to compare how visible formal and informal systems are in published digital transport data

**Why GTFS comparison is useful:**

- because data coverage itself matters for a product or planning story

**What this gives us:**

- evidence on data asymmetry

**How it helps the story:**

It supports the argument that part of the problem is not only transport access, but also transport information access.

---

### Q20. BRT corridor vs informal demand

**Why we ask it:**

- to test whether BRT formalized a corridor that already had real demand

**Why buffer analysis is used:**

- because the question is local corridor overlap
- nearby informal activity is the most direct indicator

**What this gives us:**

- evidence that BRT may be demand-aligned or not

**How it helps the story:**

It lets the project avoid saying "all new infrastructure is bad." It creates contrast.

---

### Q21. Fare per kilometer: formal vs informal

**Why we ask it:**

- because commuters choose modes partly by cost
- because accessibility is not only spatial, but economic

**Why fare/km is useful:**

- it normalizes price by trip length
- it makes mode comparison more meaningful

**What this gives us:**

- an affordability comparison

**How it helps the story:**

It helps explain whether people choose informal modes only because of coverage, or also because of price.

---

### Q22. Metro underperformance relative to population

**Why we ask it:**

- to move from raw counts to coverage expectation
- to ask which areas have less metro than their population suggests they should

**Why residual logic is used:**

- because actual minus predicted coverage is a useful gap measure

**What this gives us:**

- a ranking of under-served areas

**How it helps the story:**

It helps produce the coverage-need map behind the project narrative.

---

### Q23. Adly Mansour as a convergence node

**Why we ask it:**

- because Adly Mansour is symbolically important in the transport system
- it is presented as a major interchange node

**Why local cluster analysis is used:**

- because we want to compare its density with the rest of Cairo

**What this gives us:**

- a concrete case study

**How it helps the story:**

It turns a major symbolic location into an analyzable planning example.

---

### Q24. K-Means coverage-need synthesis

**Why we ask it:**

- because the project needs segmentation, not just single metrics
- we want to identify groups of districts with similar transport-demand patterns

**Why clustering is used:**

- because one variable is not enough to define opportunity
- the market story requires a multidimensional view

**What this gives us:**

- grouped district profiles
- candidate "target markets"

**How it helps the story:**

This is the bridge from transport analysis to product strategy.

---

## 7. Notebook 2: Why Each Hypothesis Was Used

Hypotheses are where the notebook becomes more formal and more defensible.

### H1. Coverage-need mismatch

**Hypothesis idea:**
Dense districts may receive fewer stations per capita than other districts.

**Why this hypothesis exists:**

- it directly tests whether infrastructure aligns with demand
- it turns a visual suspicion into a statistical question

**Why the chosen tests are used:**

- **Kruskal-Wallis** is used because there are more than two groups and the data may not be normally distributed
- **Mann-Whitney** is used for pairwise comparisons
- **epsilon-squared** is used to show effect size
- **Cliff's delta** is used for pairwise effect size
- **Moran's I** is used to ask whether mismatch clusters geographically

**What it gives us:**

- whether the mismatch is statistically visible
- whether it is geographically patterned

**How it helps the story:**

It makes the coverage-need argument more formal.

---

### H2. LRT catchment deficit

**Hypothesis idea:**
LRT stations may serve much weaker surrounding populations than recent metro stations.

**Why this hypothesis exists:**

- because the LRT is central to the story of eastward planning
- because ridership concerns are part of the real-world discussion around it

**Why catchment buffers are used:**

- because station usefulness depends partly on nearby population
- a 2 km area gives a local demand context

**Why Mann-Whitney is used:**

- because we compare two groups
- because population catchments are likely skewed, not normally distributed

**Why Cliff's delta is used:**

- because effect size matters, not just significance

**What it gives us:**

- a formal comparison between LRT and recent metro demand context

**How it helps the story:**

This is one of the strongest statistical foundations for the claim that not all new infrastructure is equally well sited.

---

### H3. BRT corridor match

**Hypothesis idea:**
BRT may align better with existing informal demand than the LRT does.

**Why this hypothesis exists:**

- because the project needs contrast
- if all new projects are weak, the story becomes too simple
- BRT may show a more demand-sensitive case

**Why the comparison uses controls:**

- because BRT buffers alone are not enough
- we need a reference distribution to compare them with

**Why Mann-Whitney and Cliff's delta are used:**

- same reason as H2: skewed distributions and need for effect size

**What it gives us:**

- a formal test of whether BRT is located in stronger pre-existing demand areas

**How it helps the story:**

H3 adds nuance. It shows that the project is not trying to attack every formal investment equally. It strengthens credibility.

---

## 8. Why We Use These Statistical Methods

This section explains the major statistical tools used in the analysis notebook.

### Spearman correlation

**Why we use it:**

- because many relationships are monotonic, not strictly linear
- because the data may be skewed or non-normal

**What it gives us:**

- direction and strength of ranked association

---

### Permutation test

**Why we use it:**

- to compare groups without relying heavily on parametric assumptions

**What it gives us:**

- a flexible significance test

---

### Kruskal-Wallis

**Why we use it:**

- to compare more than two groups when normality is doubtful

**What it gives us:**

- whether at least one group differs from the others

---

### Mann-Whitney U

**Why we use it:**

- for two-group comparison when distributions are not assumed normal

**What it gives us:**

- whether one group's values tend to be higher or lower than the other

---

### Cliff's delta

**Why we use it:**

- because p-values alone do not tell us how large a difference is

**What it gives us:**

- effect size for two-group nonparametric comparisons

---

### Epsilon-squared

**Why we use it:**

- because Kruskal-Wallis significance alone is not enough

**What it gives us:**

- effect size for multi-group comparison

---

### Moran's I

**Why we use it:**

- because some transport inequalities are spatial, not only numeric

**What it gives us:**

- whether similar values cluster geographically

---

### K-Means

**Why we use it:**

- because the final story needs segmentation
- because a product or policy story often depends on identifying types of districts, not just ranked lists

**What it gives us:**

- groups of similar places
- a basis for market-sizing and targeting

---

## 9. Detailed Visualization Documentation

The visualizations in Phase 2 are not decorative. Each one is used because it performs a specific analytical job. Below is a full explanation of what is used, why it is used, and what it gives to the story.

### 9.1 Notebook 1 visualizations

Notebook 1 uses fewer visuals because its main role is data preparation, not final interpretation.

#### Null audit grouped bar chart

**Where it appears:**
Notebook 1, after the cleaned outputs are produced.

**Why we use it:**

- to summarize data quality visually
- to show which sources are strong and which still contain missing values

**Why a grouped bar chart is the right choice:**

- because we compare many columns across multiple sources
- because null percentages are easier to scan visually than in a table

**What it gives us:**

- a compact quality check across the whole cleaned dataset collection

**How it helps the notebooks:**

- helps us know whether Notebook 2 can trust the outputs
- supports honest reporting about data quality

#### Integration Sankey

**Where it appears:**
Notebook 1, integration section.

**Why we use it:**

- to show how data moves through the 4-stage integration pipeline
- to show how many rows survive each stage

**Why a Sankey is the right choice:**

- because this is a flow problem
- because we want to show transitions, not only counts

**What it gives us:**

- a process view of integration yield

**How it helps the story:**

- it makes the technical integration pipeline understandable to non-technical readers
- it proves that the matched layer was built through a structured process

---

### 9.2 Notebook 2 visualizations by section

Notebook 2 uses visuals much more heavily because it is designed to interpret patterns and build the story.

#### Phase 1 recap dashboard

**Why we use it:**

- to remind the reader of the four structural gaps found earlier
- to anchor Phase 2 in Phase 1

**Why indicator panels are used:**

- because the goal is to show headline numbers, not distributions

**What it gives us:**

- a quick summary of the problem being investigated

**Story role:**

- this is the bridge between notebooks and between project phases

#### Hero map: "The Two Cairos"

**Why we use it:**

- to spatially compare formal new modes with the informal/older terminal system

**Why a map is necessary:**

- because the key story is spatial
- because overlap and separation are easier to see geographically than numerically

**What it gives us:**

- visual evidence that multiple systems coexist without full integration

**Story role:**

- this is one of the strongest narrative visuals in the project

#### Q13 scatter plots by metro line

**Why we use them:**

- to compare opening year with nearby density
- to see whether newer expansions are more demand-aligned

**Why scatter plots are used:**

- because they show relationship strength, dispersion, and outliers

**What they give us:**

- a visual sense of whether density and expansion timing move together

**Story role:**

- helps start the planning-versus-demand argument

#### Q14 distance-bucket bar chart

**Why we use it:**

- to show how many ghost terminals are close to or far from new metro

**Why a bucketed bar chart is used:**

- because the core idea is categorical distance ranges, not a continuous trend

**What it gives us:**

- an interpretable summary of whether new metro relieved old weak nodes

**Story role:**

- directly links Phase 1 underuse to Phase 2 infrastructure

#### Q15 dual-axis time series

**Why we use it:**

- to show how metro expansion and terminal ratio evolved through time

**Why a time series is used:**

- because the question is historical change

**What it gives us:**

- a planning trajectory, not just a static comparison

**Story role:**

- supports the argument that transport priorities changed over decades

#### Q16 slope chart

**Why we use it:**

- to show district growth between two time points

**Why a slope chart is used:**

- because it emphasizes change between two years clearly

**What it gives us:**

- a readable visual of where population increased most

**Story role:**

- supports the idea that unmet demand is dynamic, not fixed

#### Q17 scatter / hexbin-style joint plot with marginals

**Why we use it:**

- to examine the relationship between population density and underservedness

**Why this richer plot is used instead of a simple scatter:**

- because the distribution is dense
- because the marginals help show univariate structure
- because the highlighted quadrant helps define a "target zone"

**What it gives us:**

- both relationship and distribution in one figure

**Story role:**

- identifies the primary market condition: dense and underserved

#### Q18 scatter with regression line

**Why we use it:**

- to compare informal share with density

**Why this visual is used:**

- because it shows both spread and trend

**What it gives us:**

- evidence on whether informal dependence rises with density

**Story role:**

- helps define whether informal transport is niche or structural

#### Q18b governorate scatter

**Why we use it:**

- to compare motorization and informal dependence

**Why this simple scatter is used:**

- because the scale is aggregate and the purpose is conceptual comparison

**What it gives us:**

- a broad contextual relationship

**Story role:**

- adds socioeconomic framing to transport behavior

#### Q19 stacked bar chart

**Why we use it:**

- to compare route publication coverage across agencies and bundles

**Why a stacked bar is used:**

- because we compare composition within each agency

**What it gives us:**

- a readable view of formal-data vs paratransit-data asymmetry

**Story role:**

- strengthens the information-gap argument

#### Q20 horizontal bar chart

**Why we use it:**

- to rank BRT stations by nearby informal demand

**Why a horizontal ranked bar chart is used:**

- because station names are easier to read on the y-axis
- because the goal is ranking

**What it gives us:**

- station-level corridor evidence

**Story role:**

- shows that BRT may align with real demand better than LRT

#### Q21 box plot

**Why we use it:**

- to compare fare-per-kilometer distributions by mode or vehicle type

**Why a box plot is used:**

- because we care about spread, median, and outliers

**What it gives us:**

- an affordability comparison, not just a mean comparison

**Story role:**

- supports the idea that commuters make economic as well as spatial choices

#### Q22 residual scatter and ranked under-service bar chart

**Why we use them:**

- the scatter shows residual logic
- the ranked bar chart shows the final under-served district list more clearly

**Why both are used:**

- one explains the model
- one communicates the outcome

**What they give us:**

- a gap measure and a practical ranking

**Story role:**

- one of the strongest direct visuals for the coverage-need story

#### Q23 Adly Mansour map and histogram

**Why we use both:**

- the map shows the spatial cluster
- the histogram compares its density with a broader reference distribution

**What they give us:**

- both a local case-study view and a relative comparison

**Story role:**

- turns Adly Mansour into a symbolic and measurable planning example

#### Q24 K-Means visual set

This section uses multiple visuals because clustering is hard to explain with one chart.

##### Elbow and silhouette charts

**Why we use them:**

- to justify the choice of cluster count

**What they give us:**

- model-selection transparency

##### Cluster size bar chart

**Why we use it:**

- to show the relative scale of each segment

##### Feature z-score heat map

**Why we use it:**

- to compare cluster profiles across variables

**What it gives us:**

- a compact view of how clusters differ

##### Parallel coordinates plot

**Why we use it:**

- to show each district across all cluster features at once

**What it gives us:**

- a view of cluster shape, not only cluster average

##### Radar chart

**Why we use it:**

- to compare cluster signatures in a memorable way

**What it gives us:**

- an intuitive pattern comparison between segment types

**Story role of all K-Means visuals together:**

- they convert technical segmentation into a product and market story

#### H1 box plot and LISA map/scatter

**Why we use them:**

- the box plot shows group differences
- the spatial plot shows whether mismatch clusters geographically

**What they give us:**

- statistical and spatial views of the same hypothesis

**Story role:**

- supports the argument that mismatch is not random

#### H2 box plot and ranked station bar chart

**Why both are used:**

- the box plot summarizes group difference
- the ranked bar chart shows station-by-station evidence

**What they give us:**

- a strong visual comparison between LRT and recent metro catchments

**Story role:**

- one of the clearest and strongest visuals supporting the LRT claim

#### H3 violin plot

**Why we use it:**

- to compare the shape of corridor-demand distributions

**Why a violin plot is useful:**

- because it shows spread and density better than a single summary value

**What it gives us:**

- a fuller view of BRT-vs-control distribution differences

**Story role:**

- helps argue that BRT may represent a more demand-sensitive intervention

#### Final headline coverage-need map

**Why we use it:**

- to bring the whole project into one synthesis visual

**What it combines:**

- cluster information
- new-mode infrastructure
- key annotated locations

**What it gives us:**

- the final visual summary of planning axis vs demand axis

**Story role:**

- this is the best single visual summary of the project

#### Animated metro expansion map

**Why we use it:**

- to show the temporal direction of investment

**Why animation is useful here:**

- because expansion is a sequence, not only a final map

**What it gives us:**

- a historical-spatial story in one figure

**Story role:**

- reinforces the narrative of how Cairo's formal investment moved over time

#### Market-sizing bar chart

**Why we use it:**

- to show the population scale of each cluster

**Why a bar chart is used:**

- because the message is comparative size

**What it gives us:**

- a direct estimate of the primary market's scale

**Story role:**

- turns the analysis into an opportunity statement

#### Sunburst

**Why we use it:**

- to show governorate -> cluster -> district hierarchy

**Why a sunburst is useful:**

- because it shows nested structure more clearly than a flat chart

**What it gives us:**

- a hierarchical view of how market structure is distributed geographically

**Story role:**

- helps connect administrative geography to strategic segmentation

---

## 10. How The Methods Build The Story

The project story is not produced by one result. It is built step by step.

### Story claim 1:
There are two overlapping but not fully integrated transport systems in Cairo.

**Built by:**

- Phase 1 outputs
- GTFS formal network data
- informal transport context from Phase 1
- hero maps in Notebook 2

### Story claim 2:
New infrastructure does not always align with existing demand.

**Built by:**

- metro coverage questions
- growth and underservedness questions
- H1 coverage mismatch
- H2 LRT catchment deficit

### Story claim 3:
Not all new infrastructure is equally weak.

**Built by:**

- Q20 BRT corridor overlap
- H3 BRT corridor test

### Story claim 4:
There is a real unmet market opportunity.

**Built by:**

- Q17 density + underservedness
- Q22 residual undercoverage
- Q24 K-Means segmentation
- final market-sizing section

### Why this matters

The notebook story works because it does not jump directly from raw data to a startup or policy conclusion. It builds intermediate logic:

- where demand is
- where infrastructure is
- where the mismatch is
- which mismatch matters most
- why that mismatch is a real opportunity

---

## 11. What Is Strong In The Current Design

### Strong parts

- strong pipeline separation between engineering and analysis
- real multi-source data integration
- good use of spatial methods
- good use of nonparametric tests
- strong narrative structure
- credible use of AI techniques where they solve a real problem

### Why that matters

These strengths make the project feel like a complete applied data-science study, not just a notebook collection.

---

## 12. What Must Be Explained Carefully In The Final Report

Some methods are useful but must be presented honestly.

### Matching quality

Semantic matching is useful, but it must not be described as perfect if the validation set is still small.

### BRT completeness

BRT scraping is helpful, but it should be described as partial if the station list is not fully complete.

### LRT coordinates

If some coordinates come from fallback methods, they should be described as approximate or partially verified.

### District proxies

If district-level geography is approximated, the report should say so clearly.

### Why this honesty matters

Projects become stronger, not weaker, when they clearly separate:

- what is measured strongly
- what is estimated approximately
- what is exploratory

---

## 13. How To Explain The Difference Between Question Results And Hypothesis Results

You can explain it like this:

> The question sections are used to explore and describe the transport system from multiple angles: density, distance, cost, growth, and corridor overlap. The hypothesis sections are used to formally test the strongest claims that emerge from those descriptive patterns.

That means:

- **questions** help us discover and frame the problem
- **hypotheses** help us defend the problem with stronger evidence

---

## 14. Suggested Final Summary For Your Report

You can use this wording directly or adapt it:

> Phase 2 was structured as a two-stage analytical pipeline. The first notebook collected, cleaned, and integrated transport, population, and mobility-related data from multiple sources including GTFS, Wikipedia, OpenStreetMap, Google Maps, citypopulation.de, and World Bank data. The second notebook used these cleaned outputs to answer descriptive research questions and test formal hypotheses about transport coverage, demand alignment, and infrastructure mismatch in Greater Cairo. Descriptive questions were used to build the analytical narrative, while hypothesis tests were used to validate the strongest claims statistically. Spatial methods, nonparametric statistics, and clustering were included because the project studies a geographically uneven and non-normally distributed urban transport system. Together, these methods support the project's central story: Cairo's formal transport investments do not always align with the spatial distribution of current mobility need, creating a measurable coverage-need gap and a clear case for integrated transport intelligence.

---

## 15. Final Conclusion

Every major method in the notebooks has a role:

- **scraping methods** build the raw evidence base
- **cleaning methods** make the data usable
- **integration methods** connect new infrastructure to older transport geography
- **question sections** reveal patterns
- **hypothesis sections** test the strongest claims
- **visualizations** make the analysis understandable
- **story sections** turn technical findings into a coherent argument

So the notebooks are not just code. They are a structured argument:

1. this is the real transport data we could gather
2. this is how we cleaned and linked it
3. this is what the patterns look like
4. this is what we can test formally
5. this is why those results matter for Cairo and for the final project story

If you want, the next step I can do is create:

1. a **shorter polished version** for direct inclusion in your report, or
2. a **presentation version** with slide-style bullet points for each question and hypothesis.
