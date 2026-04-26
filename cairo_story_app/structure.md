# Structure · the 14-chapter narrative + Evidence mode

## Story mode · 14 chapters

| # | Act | Title | Arabic | Map action | Chart | Layla | Metric |
|---|---|---|---|---|---|---|---|
| 0 | — | A story about what Cairo built and who was left out | القاهرة · نظامان | City overview · zoom 9.8 | — | pulse Imbaba · dim | 1.4M |
| 1 | I | Layla lives in Imbaba | ليلى · إمبابة · ٦:١٥ | Close zoom Imbaba · pitch 55° | — | fixed · bright | 63,000 /km² |
| 2 | I | Her office is in Maadi · 11 km away | المعادي · ١١ كم | Crow-flies line · pitch 40° | — | fixed · bright | 11 km |
| 3 | I | The real route is 83 minutes each way | الرحلة الحقيقية · ٨٣ دقيقة | Chaos route reveal · pitch 45° | — | on chaos route (prog 0.15) | 83 min |
| 4 | II | What Cairo built since 2014 | ١٠ مليار دولار | Metro + LRT + BRT fade-in · pitch 45° | — | dim | $10B |
| 5 | II | 84% of Phase-1 ghost terminals are beyond 2 km | المحطات المنسيّة · ٨٤٪ | Ghost overlay + metro | — | dim | 84% |
| 6 | II | Cairo is a city of two densities | مدينتان مختلفتان | District choropleth | — | dim | 21× |
| 7 | I | At 6:15 AM she stands at the mawfaq | الموقف · ٦:١٥ | Close zoom mawfaq · pitch 55° | — | fixed · bright · image | 60+ / hr |
| 8 | II | Dense districts get 12× fewer stations per capita | عدم التوافق · ح١ | District + station overlay | **h1_box** | dim | ε² = 0.16 |
| 9 | II | The LRT median catchment is zero residents | قطار خفيف في الصحراء · ح٢ | East pan · LRT highlight | **h2_bar** | dim | δ = −0.99 |
| 10 | II | The BRT is the one thing they got right | النقل السريع · ح٣ | Ring Road + informal | **h3_bar** | dim | δ = +0.83 |
| 11 | II | No cell in this matrix is above 25% | الحُكم · ١٨ب | Reset view | **q18b_matrix** | dim | 25% |
| 12 | III | Masari · one route planner for both systems | مَسَارِي · تطبيق واحد | **Animated 10 s** microbus → metro → return | — | **animated along polyline** | 18M |
| 13 | III | 08:55 — she arrives on time | وصلت في الموعد | Maadi office · pitch 55° | — | fixed Maadi · brightest · image | 08:55 |

## Evidence mode · 25 question pages + 4 gaps + 3 hypotheses + 2 hero maps

### Phase 1 (12 questions + 4 gaps)

Each page embeds its existing Plotly HTML exports from `/Exports/` (40 HTML files total). Q1 through Q12; G1 through G4 reuse Q11/Q10/Q12/Q9 exports plus custom Python bars.

| Page | HTMLs embedded | Key KPI |
|---|---|---|
| Q1 · jobs | 2 (Q1a, Q1b) | r = 0.261 morning×jobs |
| Q2 · symmetry | 2 (Q2a, Q2b) | per-terminal asymmetry index |
| Q3 · adherence | 2 (Q3a, Q3b) | 88.0% within 120 m |
| Q4 · formal vs informal | 5 (Q4a–Q4e) | informal dominates |
| Q5 · pop × terminals | 2 (Q5a, Q5b) | weak positive association |
| Q6 · routes | 4 (Q6a, Q6b×2, Q6c) | linear, no plateau |
| Q7 · AM/PM | 2 (Q7a, Q7b) | AM/PM ratio classifier |
| Q8 · spatial | 2 (Q8a, Q8b) | HH/LL clusters |
| Q9 · underserved | 1 (Q9a) | 79 hexes · score > 0.5 |
| Q10 · empty returns | 3 (Q10, Q10a, Q10b) | 19 critical · 208 healthy |
| Q11 · ghosts | 7 (Q11 slider + Q11a–d) | 115 · 69/17/29 |
| Q12 · vehicle fit | 5 (Q12a–e) | 75% microbus on >50 km |
| G1 · ghosts | Python bar + Q11 reuse | 115 · 60% recovery at 500 m |
| G2 · empty returns | Python bar + Q10 reuse | 19 critical |
| G3 · vehicle mismatch | Python bar + Q12 reuse | microbus-heavy mix |
| G4 · underserved | Python gauge + Q9 reuse | 79 hexes |

### Phase 2 (4 showcase questions)

| Page | Charts | Key KPI |
|---|---|---|
| Q14 · ghosts vs new metro | Python distance-bucket bar | 84% beyond 2 km |
| Q18b · gap-closure matrix | Python heatmap | no cell > 25% |
| Q22 · Adly Mansour | Embed `adly_mansour_zoom.html` | 4 modes · 83rd pctile |
| Q24 · K-Means | Python cluster-size bar + CAGR bubble | ARI = 1.00 |

### Hypotheses (3 + 2 hero maps)

| Page | Charts | Key KPI |
|---|---|---|
| H1 · coverage-need mismatch | Python box + Moran's I bar | H = 12.5 · ε² = 0.16 |
| H2 · LRT catchment deficit | Python comparison bar | δ = −0.993 |
| H3 · BRT corridor match | Python comparison bar | δ = +0.826 |
| HERO · Two Cairos | Embed `two_cairos_map.html` | spatial overlay |
| HERO · Coverage-Need | Embed `headline_coverage_need_map.html` | final synthesis |

Total: 16 + 4 + 5 = 25 evidence pages.

## Layout decisions

- Story mode: `st.columns([2, 8, 4])` (nav · map · panel)
- Evidence mode: `st.columns([2, 12])` (nav · content scroll)
- Map: PyDeck Carto `dark_no_labels` basemap, glow layers (outer 40 α + inner 255 α), Layla IconLayer + pulse ScatterplotLayer
- Charts: Plotly with notebook-matched palette (`#0D1117` bg, `#161B22` panel); Share Tech Mono body, Orbitron titles
- Cards: frosted glassmorphism (`backdrop-filter: blur(18px) saturate(140%)`), 1 px rgba border, corner L-brackets (shimmer matches notebook)
- CSS: injected via `st.markdown` from `style/dark_theme.css` (pure-CSS — no JS)
