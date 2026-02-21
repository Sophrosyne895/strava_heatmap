# Strava Heatmap — UI Mockup

## Full Layout (1440px desktop)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ▓▓ Strava Heatmap                                      [Sync Activities ↻]  │  ← top nav bar (dark)
└──────────────────────────────────────────────────────────────────────────────┘
│                                                                               │
│  ┌─────────────────────┐  ┌────────────────────────────────────────────────┐ │
│  │  FILTERS            │  │                                                │ │
│  │─────────────────────│  │                                                │ │
│  │  Sport Type         │  │                   [dark map tiles]             │ │
│  │  ☑ Run              │  │                                                │ │
│  │  ☑ Ride             │  │          ╱╲  glowing orange/blue               │ │
│  │  ☑ Hike             │  │        ╱╱  ╲╲  polylines                      │ │
│  │  ☑ Walk             │  │      ╱╱      ╲╲  overlapping                  │ │
│  │  ☑ Other            │  │    ╱╱    ╱╲    ╲╲  = brighter                 │ │
│  │                     │  │   ╱    ╱╱  ╲╲    ╲                            │ │
│  │─────────────────────│  │  │   ╱╱    ╱╱╲╲   │                           │ │
│  │  Date Range         │  │  │ ╱╱    ╱╱    ╲  │  ← frequently run        │ │
│  │                     │  │   ╲╲  ╱╱      ╱     routes glow brighter      │ │
│  │  From  [2018-01-01] │  │    ╲╲╱╱      ╱╱                               │ │
│  │  To    [2026-02-21] │  │      ╲╲    ╱╱                                 │ │
│  │                     │  │        ╲╲╱╱                                   │ │
│  │─────────────────────│  │                                                │ │
│  │  Stats              │  │                                                │ │
│  │                     │  │                              [+]  zoom control │ │
│  │  Activities:  1,847 │  │                              [-]               │ │
│  │  Total dist:  14,203│  │                                                │ │
│  │             km      │  └────────────────────────────────────────────────┘ │
│  │                     │                                                      │
│  │  Runs:         892  │                                                      │
│  │  Rides:        721  │                                                      │
│  │  Hikes:        134  │                                                      │
│  │  Other:        100  │                                                      │
│  │                     │                                                      │
│  └─────────────────────┘                                                      │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Activity Tooltip (on hover)

```
    ┌──────────────────────────────┐
    │  Morning Run                 │
    │  Mar 15, 2024                │
    │  Distance:  12.3 km          │
    │  Time:      58:42            │
    └──────────────────────────────┘
              ▲
    (appears on route hover)
```

---

## Sync Progress State

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ▓▓ Strava Heatmap                           [Syncing... 847 / 1,847  ████░] │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## First-Time / No Token State

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  ▓▓ Strava Heatmap                                                           │
└──────────────────────────────────────────────────────────────────────────────┘
│                                                                               │
│                                                                               │
│                         ┌─────────────────────────┐                          │
│                         │                         │                          │
│                         │   Connect to Strava to  │                          │
│                         │   get started.          │                          │
│                         │                         │                          │
│                         │  [Connect with Strava]  │  ← orange Strava button  │
│                         │                         │                          │
│                         └─────────────────────────┘                          │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Color Scheme

| Element              | Color                  | Notes                              |
|----------------------|------------------------|------------------------------------|
| Background / map     | `#1a1a2e` (near-black) | CartoDB Dark Matter tiles          |
| Nav bar              | `#0d0d1a`              | Slightly darker than map           |
| Sidebar              | `#12121f` + border     | Subtle separation from map         |
| Run routes           | `#fc4c02` (Strava org) | Semi-transparent, ~30% opacity     |
| Ride routes          | `#4fc3f7` (light blue) | Semi-transparent, ~30% opacity     |
| Hike/Walk routes     | `#81c784` (soft green) | Semi-transparent, ~30% opacity     |
| Other routes         | `#ce93d8` (soft purple)| Semi-transparent, ~30% opacity     |
| Overlap glow         | Natural canvas blend   | More passes = brighter             |
| Accent / buttons     | `#fc4c02`              | Strava brand orange                |
| Text (primary)       | `#e0e0e0`              |                                    |
| Text (secondary)     | `#888`                 |                                    |
```
