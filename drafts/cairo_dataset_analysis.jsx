import { useState } from "react";

const DATASETS = {
  boarding: {
    short: "Boarding",
    full: "Cairo Daily Boarding & Alighting",
    file: "Cairo_Daily_Boarding.json",
    records: 1302,
    geometry: "Point",
    color: "#bd6048",
    keyFields: [
      "stop_name",
      "alight_daily_int",
      "board_daily_int_*_{morning/evening} (by mode)",
      "board_alight_daily_int_*_{morning/evening}",
      "routes_*_{morning/evening} (route counts by mode)",
      "daily_formal/informal_{morning}_ba",
      "daily_all_morning_ba / daily_all_ba",
    ],
  },
  population: {
    short: "Population",
    full: "Population & Employment Access",
    file: "Population___Employment_Access_.json",
    records: 1525,
    geometry: "MultiPolygon (H3 hexagons)",
    color: "#2A9D8F",
    keyFields: [
      "pop_18 (population estimate)",
      "pop_male / pop_female",
      "jobs_count",
      "jobs_count_access_60mins",
      "jobs_perc_access_60mins",
      "id (H3 hex cell ID)",
    ],
  },
  terminals: {
    short: "Terminals",
    full: "Public Transport Terminals",
    file: "Public_Transport_Terminals.json",
    records: 280,
    geometry: "MultiPolygon",
    color: "#E9C46A",
    keyFields: ["gid (terminal ID — joins to Routes o_id/d_id)", "name", "name_ar"],
  },
  routes: {
    short: "Routes",
    full: "Public Transport Routes",
    file: "Public_Transport_Routes.json",
    records: 1784,
    geometry: "LineString",
    color: "#264653",
    keyFields: [
      "route_id / trip_id",
      "vehicle_name (Microbus, Bus, Minibus, etc.)",
      "passenger_capacity",
      "o_id / d_id (terminal gid)",
      "origin / destination (terminal name)",
      "len_km (route length)",
      "agency_id (mode code)",
      "direction_id",
    ],
  },
  passengerFlow: {
    short: "Passenger Flow",
    full: "Public Transport Passenger Flow",
    file: "Public_Transport_Passenger_Flow.json",
    records: 9258,
    geometry: "LineString (segments)",
    color: "#F4A261",
    keyFields: ["passengers_mpp (passengers/hour/direction)"],
  },
  vehicleFlow: {
    short: "Vehicle Flow",
    full: "Public Transport Vehicles Flow",
    file: "Public_Transport_Vehicles_Flow.json",
    records: 5592,
    geometry: "LineString (segments)",
    color: "#7B2D8E",
    keyFields: ["vehicles_per_hour (vehicles/hour/direction)"],
  },
  speeds: {
    short: "Speeds",
    full: "Public Transport Commercial Speeds",
    file: "Public_Transport_Commercial_Speeds_2.json",
    records: 26154,
    geometry: "LineString",
    color: "#457B9D",
    keyFields: ["o_id / d_id", "vehicle_name", "dist", "duration", "speed (km/h)"],
  },
};

const QUESTIONS = [
  {
    id: 1,
    question:
      "Is there a relationship between morning alighting counts at a stop and the job accessibility score (jobs_count_access_60mins)?",
    datasets: ["boarding", "population"],
    mergeStrategy: "Spatial Join",
    mergeDetail:
      "Join Boarding stop points into Population H3 hexagons using a spatial point-in-polygon operation. Each stop gets the hex's jobs_count_access_60mins. Then correlate morning alighting (sum of board_alight columns for morning) vs. the job accessibility score.",
    fieldsUsed: {
      boarding: ["alight_daily_int", "board_alight_daily_int_*_morning", "geometry (Point)"],
      population: ["jobs_count_access_60mins", "geometry (H3 hexagon)"],
    },
    complexity: "medium",
  },
  {
    id: 2,
    question:
      "Is there a relation between population density and the passenger-per-vehicle ratio at terminals?",
    datasets: ["population", "passengerFlow", "vehicleFlow", "terminals"],
    mergeStrategy: "Spatial Join (multi-step)",
    mergeDetail:
      "Step 1: Spatially join Passenger Flow and Vehicle Flow segments that intersect Terminal polygons to compute total passengers and vehicles at each terminal, then derive a passenger/vehicle ratio. Step 2: Spatially join Terminal centroids into Population H3 hexagons to attach pop_18. Step 3: Correlate population density vs. passenger/vehicle ratio. Low ratios in high-pop areas may indicate car dependency.",
    fieldsUsed: {
      population: ["pop_18", "geometry"],
      passengerFlow: ["passengers_mpp", "geometry"],
      vehicleFlow: ["vehicles_per_hour", "geometry"],
      terminals: ["gid", "name", "geometry"],
    },
    complexity: "high",
  },
  {
    id: 3,
    question: "Do people actually follow the designated drop points?",
    datasets: ["boarding", "routes"],
    mergeStrategy: "Spatial Proximity Analysis",
    mergeDetail:
      "Buffer each Route's LineString geometry by a small distance and check which Boarding stop points fall on or near the route vs. which have alighting activity far from any route. Compare the spatial distribution of alighting (alight_daily_int) relative to route paths. High alighting far from routes = people not following drop points.",
    fieldsUsed: {
      boarding: ["stop_name", "alight_daily_int", "geometry (Point)"],
      routes: ["route_id", "trip_id", "geometry (LineString)"],
    },
    complexity: "medium",
  },
  {
    id: 4,
    question:
      'When does the difference between formal and informal arise — when do people prefer one over the other?',
    datasets: ["boarding"],
    mergeStrategy: "No merge needed — single dataset",
    mergeDetail:
      "The Boarding dataset already contains pre-aggregated fields: daily_formal_morning_ba, daily_informal_morning_ba, daily_formal_all_ba, daily_informal_all_ba. Compare formal vs. informal boarding+alighting across morning/evening and across stops. Identify spatial and temporal patterns where one dominates.",
    fieldsUsed: {
      boarding: [
        "daily_formal_morning_ba",
        "daily_informal_morning_ba",
        "daily_formal_all_ba",
        "daily_informal_all_ba",
        "board_alight columns by mode & time",
      ],
    },
    complexity: "low",
  },
  {
    id: 5,
    question:
      "The relation between population density and terminal locations — does it matter?",
    datasets: ["population", "terminals"],
    mergeStrategy: "Spatial Join",
    mergeDetail:
      "Spatially join Terminal polygon centroids into Population H3 hexagons. Count terminals per hexagon and compare against pop_18. Identify high-population hexagons with few/no terminals and vice versa.",
    fieldsUsed: {
      population: ["pop_18", "geometry"],
      terminals: ["gid", "name", "geometry"],
    },
    complexity: "medium",
  },
  {
    id: 6,
    question: "Does providing more routes mean a higher passenger count?",
    datasets: ["boarding"],
    mergeStrategy: "No merge needed — single dataset",
    mergeDetail:
      "The Boarding dataset has route counts per mode (routes_cta_morning, routes_p_o_14_morning, etc.) alongside boarding+alighting totals (daily_all_morning_ba, daily_all_ba). Sum route counts across modes per stop and correlate with total passenger activity.",
    fieldsUsed: {
      boarding: ["routes_*_morning/evening (all modes)", "daily_all_morning_ba", "daily_all_ba"],
    },
    complexity: "low",
  },
  {
    id: 7,
    question:
      "Is there a relationship between morning and evening boarding, while knowing the route?",
    datasets: ["boarding"],
    mergeStrategy: "No merge needed — single dataset",
    mergeDetail:
      "Compare morning vs. evening boarding columns (board_daily_int_*_morning vs. board_daily_int_*_evening) per stop and per mode. Scatter-plot morning vs. evening totals. Check if stops with high morning boarding also have high evening boarding (commuter pattern) or inverse (residential vs. commercial).",
    fieldsUsed: {
      boarding: [
        "board_daily_int_*_morning (all modes)",
        "board_daily_int_*_evening (all modes)",
        "daily_all_morning_ba",
      ],
    },
    complexity: "low",
  },
  {
    id: 8,
    question:
      'Is there a relation between boarding areas themselves — does a high-passenger area mean neighbors also have high counts?',
    datasets: ["boarding"],
    mergeStrategy: "Spatial Autocorrelation (single dataset)",
    mergeDetail:
      "Using the Boarding point locations and daily_all_ba values, perform spatial autocorrelation analysis (e.g., Moran's I or simple KNN neighbor averaging). Build a spatial weights matrix from stop coordinates and test whether nearby stops have correlated passenger counts.",
    fieldsUsed: {
      boarding: ["daily_all_ba", "geometry (Point coordinates)"],
    },
    complexity: "medium",
  },
  {
    id: 9,
    question:
      "Are there areas with very high population but low boardings — and if so, is it due to a pattern or deficiency?",
    datasets: ["boarding", "population"],
    mergeStrategy: "Spatial Join",
    mergeDetail:
      "Spatially join Boarding stops into Population H3 hexagons. Aggregate total boarding per hexagon (sum of daily_all_ba). Compare pop_18 vs. total boarding. Flag hexagons with high population but low/zero boarding as potential underserved areas. Cross-reference with jobs_count to see if they're residential-only zones.",
    fieldsUsed: {
      boarding: ["daily_all_ba", "geometry"],
      population: ["pop_18", "jobs_count", "geometry"],
    },
    complexity: "medium",
  },
  {
    id: 10,
    question:
      "What is the relation between the number of vehicles that return empty and the terminal location?",
    datasets: ["vehicleFlow", "passengerFlow", "terminals", "routes"],
    mergeStrategy: "Spatial Join + Attribute Join",
    mergeDetail:
      'Step 1: Spatially identify segments near each Terminal. Step 2: Compare vehicles_per_hour vs. passengers_mpp on those segments — segments where vehicles >> passengers indicate "empty returns." Step 3: Aggregate this imbalance per terminal. Optionally join Routes (via terminal gid) to see which routes feed these terminals. Map terminal locations with the empty-return ratio.',
    fieldsUsed: {
      vehicleFlow: ["vehicles_per_hour", "geometry"],
      passengerFlow: ["passengers_mpp", "geometry"],
      terminals: ["gid", "name", "geometry"],
      routes: ["o_id", "d_id", "origin", "destination"],
    },
    complexity: "high",
  },
  {
    id: 11,
    question:
      "What is the relation between terminals that are not used and the routes they provide?",
    datasets: ["terminals", "routes", "boarding"],
    mergeStrategy: "Attribute Join + Spatial Join",
    mergeDetail:
      "Step 1: Join Routes to Terminals via o_id/d_id = terminal gid. Count routes per terminal. Step 2: Spatially join Boarding stops near each Terminal to get total passenger activity. Step 3: Identify terminals with routes assigned but low/zero boarding activity. Analyze route characteristics (vehicle_name, len_km) for underused terminals.",
    fieldsUsed: {
      terminals: ["gid", "name", "geometry"],
      routes: ["o_id", "d_id", "vehicle_name", "len_km", "route_id"],
      boarding: ["daily_all_ba", "geometry"],
    },
    complexity: "high",
  },
  {
    id: 12,
    question: "Is there a relation between the vehicle type and the route length?",
    datasets: ["routes"],
    mergeStrategy: "No merge needed — single dataset",
    mergeDetail:
      "The Routes dataset contains both vehicle_name (Microbus, Bus, Minibus, Box, Tomnaya) and len_km per trip. Group by vehicle_name and analyze the distribution of len_km. Box plot or violin plot to compare route lengths across vehicle types.",
    fieldsUsed: {
      routes: ["vehicle_name", "len_km", "passenger_capacity"],
    },
    complexity: "low",
  },
];

const JOIN_METHODS = [
  {
    name: "Spatial Point-in-Polygon",
    desc: "Drop stop points into H3 hexagons to attach population/jobs data",
    icon: "◎",
    usedIn: [1, 9],
  },
  {
    name: "Spatial Intersection (Line ∩ Polygon)",
    desc: "Clip flow segments to terminal areas to get per-terminal metrics",
    icon: "⬡",
    usedIn: [2, 10],
  },
  {
    name: "Attribute Join (gid = o_id / d_id)",
    desc: "Routes link to Terminals via matching terminal IDs",
    icon: "⟷",
    usedIn: [10, 11],
  },
  {
    name: "Spatial Proximity / Buffer",
    desc: "Find stops near routes or terminals using distance thresholds",
    icon: "◉",
    usedIn: [3, 11],
  },
  {
    name: "Spatial Autocorrelation",
    desc: "Analyze clustering of values among neighboring features",
    icon: "⬢",
    usedIn: [8],
  },
];

const COMPLEXITY_COLORS = {
  low: "#2A9D8F",
  medium: "#E9C46A",
  high: "#E86F51",
};

export default function CairoDatasetAnalysis() {
  const [selectedQ, setSelectedQ] = useState(null);
  const [view, setView] = useState("questions");

  const summaryStats = {
    singleDataset: QUESTIONS.filter((q) => q.datasets.length === 1).length,
    twoDatasets: QUESTIONS.filter((q) => q.datasets.length === 2).length,
    threeOrMore: QUESTIONS.filter((q) => q.datasets.length >= 3).length,
  };

  return (
    <div
      style={{
        fontFamily: "'Crimson Pro', 'Georgia', serif",
        background: "#0D1117",
        color: "#C9D1D9",
        minHeight: "100vh",
        padding: "0",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        * { box-sizing: border-box; }
        
        .nav-btn {
          background: transparent;
          border: 1px solid #30363D;
          color: #C9D1D9;
          padding: 8px 20px;
          cursor: pointer;
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          letter-spacing: 1px;
          text-transform: uppercase;
          transition: all 0.2s;
        }
        .nav-btn:hover { border-color: #58A6FF; color: #58A6FF; }
        .nav-btn.active { background: #58A6FF; color: #0D1117; border-color: #58A6FF; }
        
        .q-card {
          background: #161B22;
          border: 1px solid #21262D;
          padding: 20px;
          cursor: pointer;
          transition: all 0.25s;
          position: relative;
          overflow: hidden;
        }
        .q-card:hover { border-color: #58A6FF; transform: translateY(-2px); }
        .q-card.selected { border-color: #58A6FF; background: #1C2333; }
        
        .ds-pill {
          display: inline-block;
          padding: 3px 10px;
          border-radius: 2px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px;
          margin: 2px 3px;
          border: 1px solid;
        }
        
        .merge-badge {
          display: inline-block;
          padding: 2px 8px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 10px;
          letter-spacing: 0.5px;
          border-radius: 2px;
        }
        
        .detail-panel {
          background: #161B22;
          border: 1px solid #30363D;
          padding: 28px;
          margin-top: 16px;
          animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .field-tag {
          display: inline-block;
          background: #21262D;
          padding: 2px 8px;
          margin: 2px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px;
          color: #8B949E;
          border-left: 2px solid;
        }
        
        .dataset-card {
          background: #161B22;
          border: 1px solid #21262D;
          padding: 20px;
          transition: border-color 0.2s;
        }
        .dataset-card:hover { border-color: #30363D; }
        
        .matrix-cell {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          transition: all 0.15s;
        }

        .section-divider {
          height: 1px;
          background: linear-gradient(90deg, transparent, #30363D, transparent);
          margin: 40px 0;
        }
      `}</style>

      {/* Header */}
      <div style={{ padding: "40px 32px 20px", borderBottom: "1px solid #21262D" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 8 }}>
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#58A6FF", letterSpacing: 2, textTransform: "uppercase" }}>
              Cairo Transport Analysis
            </span>
            <span style={{ color: "#30363D" }}>—</span>
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#484F58" }}>
              7 datasets · 12 questions
            </span>
          </div>
          <h1 style={{ fontSize: 32, fontWeight: 300, margin: "8px 0 16px", letterSpacing: -0.5 }}>
            Dataset Merge Analysis
          </h1>
          <p style={{ color: "#8B949E", fontSize: 16, lineHeight: 1.6, maxWidth: 700, margin: 0 }}>
            A systematic breakdown of which datasets to combine — and how — 
            to answer each research question about Cairo's congestion patterns.
          </p>

          {/* Quick stats */}
          <div style={{ display: "flex", gap: 32, marginTop: 24 }}>
            {[
              { label: "Single Dataset", value: summaryStats.singleDataset, color: "#2A9D8F" },
              { label: "2-Dataset Merge", value: summaryStats.twoDatasets, color: "#E9C46A" },
              { label: "3+ Dataset Merge", value: summaryStats.threeOrMore, color: "#E86F51" },
            ].map((s) => (
              <div key={s.label} style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                <span style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.value}</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#8B949E", letterSpacing: 0.5 }}>
                  {s.label}
                </span>
              </div>
            ))}
          </div>

          {/* Navigation */}
          <div style={{ display: "flex", gap: 0, marginTop: 28 }}>
            {[
              { key: "questions", label: "Questions" },
              { key: "datasets", label: "Datasets" },
              { key: "matrix", label: "Merge Matrix" },
              { key: "methods", label: "Join Methods" },
            ].map((tab) => (
              <button
                key={tab.key}
                className={`nav-btn ${view === tab.key ? "active" : ""}`}
                onClick={() => setView(tab.key)}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: "32px", maxWidth: 1100, margin: "0 auto" }}>

        {/* === QUESTIONS VIEW === */}
        {view === "questions" && (
          <div>
            <div style={{ display: "grid", gap: 12 }}>
              {QUESTIONS.map((q) => (
                <div key={q.id}>
                  <div
                    className={`q-card ${selectedQ === q.id ? "selected" : ""}`}
                    onClick={() => setSelectedQ(selectedQ === q.id ? null : q.id)}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                          <span style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: 12,
                            color: "#58A6FF",
                            minWidth: 24,
                          }}>
                            Q{q.id}
                          </span>
                          <span className="merge-badge" style={{
                            background: `${COMPLEXITY_COLORS[q.complexity]}18`,
                            color: COMPLEXITY_COLORS[q.complexity],
                            border: `1px solid ${COMPLEXITY_COLORS[q.complexity]}40`,
                          }}>
                            {q.complexity}
                          </span>
                          <span className="merge-badge" style={{
                            background: "#21262D",
                            color: "#8B949E",
                          }}>
                            {q.mergeStrategy}
                          </span>
                        </div>
                        <p style={{ margin: 0, fontSize: 15, lineHeight: 1.5, color: "#E6EDF3" }}>
                          {q.question}
                        </p>
                        <div style={{ marginTop: 12 }}>
                          {q.datasets.map((ds) => (
                            <span
                              key={ds}
                              className="ds-pill"
                              style={{
                                borderColor: `${DATASETS[ds].color}60`,
                                color: DATASETS[ds].color,
                                background: `${DATASETS[ds].color}10`,
                              }}
                            >
                              {DATASETS[ds].short}
                            </span>
                          ))}
                        </div>
                      </div>
                      <span style={{ color: "#484F58", fontSize: 18, marginLeft: 12, transform: selectedQ === q.id ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}>
                        ▾
                      </span>
                    </div>
                  </div>

                  {selectedQ === q.id && (
                    <div className="detail-panel">
                      <h3 style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, color: "#58A6FF", letterSpacing: 1, textTransform: "uppercase", margin: "0 0 16px" }}>
                        Merge Strategy
                      </h3>
                      <p style={{ fontSize: 14, lineHeight: 1.7, color: "#C9D1D9", margin: "0 0 24px" }}>
                        {q.mergeDetail}
                      </p>

                      <h3 style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, color: "#58A6FF", letterSpacing: 1, textTransform: "uppercase", margin: "0 0 16px" }}>
                        Fields Required
                      </h3>
                      {Object.entries(q.fieldsUsed).map(([ds, fields]) => (
                        <div key={ds} style={{ marginBottom: 14 }}>
                          <span style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: 12,
                            color: DATASETS[ds].color,
                            fontWeight: 500,
                          }}>
                            {DATASETS[ds].short}
                          </span>
                          <div style={{ marginTop: 6 }}>
                            {fields.map((f, i) => (
                              <span key={i} className="field-tag" style={{ borderLeftColor: DATASETS[ds].color }}>
                                {f}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* === DATASETS VIEW === */}
        {view === "datasets" && (
          <div style={{ display: "grid", gap: 16 }}>
            {Object.entries(DATASETS).map(([key, ds]) => {
              const usedIn = QUESTIONS.filter((q) => q.datasets.includes(key));
              return (
                <div key={key} className="dataset-card">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                        <div style={{ width: 12, height: 12, background: ds.color, borderRadius: 2 }} />
                        <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: "#E6EDF3" }}>
                          {ds.short}
                        </h3>
                      </div>
                      <p style={{ margin: "4px 0 0 22px", fontSize: 13, color: "#8B949E" }}>{ds.full}</p>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 20, color: ds.color }}>
                        {ds.records.toLocaleString()}
                      </div>
                      <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#484F58" }}>
                        records
                      </div>
                    </div>
                  </div>

                  <div style={{ marginTop: 14, marginLeft: 22 }}>
                    <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#484F58", marginBottom: 4 }}>
                      GEOMETRY: {ds.geometry} &nbsp;|&nbsp; FILE: {ds.file}
                    </div>
                    <div style={{ marginTop: 8 }}>
                      {ds.keyFields.map((f, i) => (
                        <span key={i} className="field-tag" style={{ borderLeftColor: ds.color }}>
                          {f}
                        </span>
                      ))}
                    </div>
                    <div style={{ marginTop: 12 }}>
                      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#8B949E" }}>
                        Used in:{" "}
                      </span>
                      {usedIn.map((q) => (
                        <span key={q.id} style={{
                          fontFamily: "'JetBrains Mono', monospace",
                          fontSize: 11,
                          color: "#58A6FF",
                          marginRight: 8,
                          cursor: "pointer",
                        }}
                          onClick={() => { setView("questions"); setSelectedQ(q.id); }}
                        >
                          Q{q.id}
                        </span>
                      ))}
                      {usedIn.length === 0 && (
                        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#484F58" }}>
                          (none directly)
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* === MATRIX VIEW === */}
        {view === "matrix" && (
          <div>
            <p style={{ color: "#8B949E", fontSize: 14, marginBottom: 24 }}>
              Which datasets are needed for each question. Filled cells indicate the dataset is required.
            </p>
            <div style={{ overflowX: "auto" }}>
              <table style={{ borderCollapse: "collapse", width: "100%" }}>
                <thead>
                  <tr>
                    <th style={{ padding: "8px 12px", textAlign: "left", fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#484F58", borderBottom: "1px solid #21262D" }}>
                      
                    </th>
                    {Object.entries(DATASETS).map(([key, ds]) => (
                      <th key={key} style={{
                        padding: "8px 4px",
                        textAlign: "center",
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 10,
                        color: ds.color,
                        borderBottom: "1px solid #21262D",
                        whiteSpace: "nowrap",
                        letterSpacing: 0.5,
                      }}>
                        {ds.short}
                      </th>
                    ))}
                    <th style={{ padding: "8px 12px", textAlign: "center", fontFamily: "'JetBrains Mono', monospace", fontSize: 10, color: "#484F58", borderBottom: "1px solid #21262D" }}>
                      Strategy
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {QUESTIONS.map((q) => (
                    <tr key={q.id} style={{ cursor: "pointer" }} onClick={() => { setView("questions"); setSelectedQ(q.id); }}>
                      <td style={{
                        padding: "8px 12px",
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 12,
                        color: "#58A6FF",
                        borderBottom: "1px solid #161B22",
                        whiteSpace: "nowrap",
                      }}>
                        Q{q.id}
                      </td>
                      {Object.keys(DATASETS).map((dsKey) => (
                        <td key={dsKey} style={{ borderBottom: "1px solid #161B22", textAlign: "center", padding: 2 }}>
                          <div className="matrix-cell" style={{
                            margin: "0 auto",
                            background: q.datasets.includes(dsKey) ? `${DATASETS[dsKey].color}25` : "transparent",
                            color: q.datasets.includes(dsKey) ? DATASETS[dsKey].color : "transparent",
                            borderRadius: 3,
                          }}>
                            {q.datasets.includes(dsKey) ? "●" : "·"}
                          </div>
                        </td>
                      ))}
                      <td style={{
                        padding: "8px 12px",
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 10,
                        color: "#8B949E",
                        borderBottom: "1px solid #161B22",
                        textAlign: "center",
                      }}>
                        {q.mergeStrategy.replace(" — single dataset", "")}
                      </td>
                    </tr>
                  ))}
                  {/* Footer: usage count */}
                  <tr>
                    <td style={{ padding: "12px 12px 8px", fontFamily: "'JetBrains Mono', monospace", fontSize: 10, color: "#484F58", borderTop: "1px solid #21262D" }}>
                      Times used
                    </td>
                    {Object.keys(DATASETS).map((dsKey) => {
                      const count = QUESTIONS.filter((q) => q.datasets.includes(dsKey)).length;
                      return (
                        <td key={dsKey} style={{ textAlign: "center", padding: "12px 4px 8px", fontFamily: "'JetBrains Mono', monospace", fontSize: 14, color: count > 0 ? DATASETS[dsKey].color : "#21262D", fontWeight: 600, borderTop: "1px solid #21262D" }}>
                          {count}
                        </td>
                      );
                    })}
                    <td style={{ borderTop: "1px solid #21262D" }} />
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* === JOIN METHODS VIEW === */}
        {view === "methods" && (
          <div>
            <p style={{ color: "#8B949E", fontSize: 14, marginBottom: 24 }}>
              The five spatial and attribute join techniques needed across all 12 questions.
            </p>
            <div style={{ display: "grid", gap: 16 }}>
              {JOIN_METHODS.map((m, i) => (
                <div key={i} className="dataset-card">
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
                    <div style={{
                      width: 44, height: 44,
                      display: "flex", alignItems: "center", justifyContent: "center",
                      background: "#58A6FF15",
                      color: "#58A6FF",
                      fontSize: 22,
                      borderRadius: 4,
                      flexShrink: 0,
                    }}>
                      {m.icon}
                    </div>
                    <div>
                      <h3 style={{ margin: "0 0 4px", fontSize: 16, color: "#E6EDF3" }}>{m.name}</h3>
                      <p style={{ margin: "0 0 10px", fontSize: 13, color: "#8B949E", lineHeight: 1.5 }}>{m.desc}</p>
                      <div>
                        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#484F58" }}>
                          Used in:{" "}
                        </span>
                        {m.usedIn.map((qid) => (
                          <span key={qid} style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: 11,
                            color: "#58A6FF",
                            marginRight: 8,
                            cursor: "pointer",
                          }}
                            onClick={() => { setView("questions"); setSelectedQ(qid); }}
                          >
                            Q{qid}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="section-divider" />

            <h3 style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, color: "#58A6FF", letterSpacing: 1, textTransform: "uppercase", margin: "0 0 16px" }}>
              Key Join Relationships
            </h3>
            <div style={{ background: "#161B22", border: "1px solid #21262D", padding: 24, fontFamily: "'JetBrains Mono', monospace", fontSize: 12, lineHeight: 2.2, color: "#8B949E" }}>
              <div><span style={{ color: "#E9C46A" }}>Terminals.gid</span> <span style={{ color: "#484F58" }}>═══</span> <span style={{ color: "#264653" }}>Routes.o_id / Routes.d_id</span> <span style={{ color: "#484F58" }}>// attribute join — exact match</span></div>
              <div><span style={{ color: "#E86F51" }}>Boarding.geometry</span> <span style={{ color: "#484F58" }}>∈∈∈</span> <span style={{ color: "#2A9D8F" }}>Population.geometry</span> <span style={{ color: "#484F58" }}>// spatial — point in H3 hex</span></div>
              <div><span style={{ color: "#E9C46A" }}>Terminals.geometry</span> <span style={{ color: "#484F58" }}>∈∈∈</span> <span style={{ color: "#2A9D8F" }}>Population.geometry</span> <span style={{ color: "#484F58" }}>// spatial — centroid in H3 hex</span></div>
              <div><span style={{ color: "#F4A261" }}>PassengerFlow.geometry</span> <span style={{ color: "#484F58" }}>∩∩∩</span> <span style={{ color: "#7B2D8E" }}>VehicleFlow.geometry</span> <span style={{ color: "#484F58" }}>// spatial — overlapping segments</span></div>
              <div><span style={{ color: "#E86F51" }}>Boarding.geometry</span> <span style={{ color: "#484F58" }}>≈≈≈</span> <span style={{ color: "#264653" }}>Routes.geometry</span> <span style={{ color: "#484F58" }}>// spatial — proximity / nearest</span></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
