# Weather APIs for Developers: Comprehensive Comparison

## Executive Summary

| API | Best For | Free Tier | Starting Price | Global Coverage | Key Strength |
|-----|----------|-----------|----------------|-----------------|--------------|
| **OpenWeatherMap** | General apps, beginners | 1,000 calls/day | ~$140/mo (Startup) | ✅ Global | Most popular, comprehensive docs |
| **WeatherAPI.com** | Feature-rich apps | 100K calls/mo | $7/mo (Starter) | ✅ Global | Affordable, includes astronomy & sports |
| **Tomorrow.io** | AI/ML applications, enterprise | Generous free tier | Contact Sales | ✅ Global | 60+ data layers, hyperlocal accuracy |
| **Visual Crossing** | Data science, historical data | 1,000 records/day | $0.0001/record | ✅ Global | 50+ years history, CSV/JSON output |
| **Open-Meteo** | Open-source, non-commercial | Unlimited | **FREE** | ✅ Global | Completely free, no API key needed |
| **Weatherbit** | Ag-weather, energy | 50 calls/day | ~$50/mo (Standard) | ✅ Global | Lightning data, Ag/energy specializations |
| **AccuWeather** | Commercial products | Limited | Contact Sales | ✅ Global | Superior accuracy reputation |

---

## 1. OpenWeatherMap

### Pricing
| Plan | Price | Calls/Month | Rate Limit |
|------|-------|-------------|------------|
| Free | $0 | 1,000/day (~30K/mo) | 60/min |
| Startup | ~$140/mo | 10M | 600/min |
| Developer | ~$180/mo | 100M | 3,000/min |
| Professional | ~$470/mo | 1B | 30,000/min |
| Expert | ~$825/mo | 3B | 100,000/min |
| Enterprise | £3,000+/mo | 5B+ | 200,000/min |

**One Call 3.0 (Recommended):** Pay-per-call after 1,000 free daily calls

### Key Features
- **One Call API 3.0**: Single endpoint for current, forecast, historical, and alerts
- **Historical data**: Up to 47+ years back
- **Forecast**: 8-day daily, 48-hour hourly, 1-minute forecast (next hour)
- **Air Pollution API**: CO, NO, NO₂, O₃, SO₂, PM2.5, PM10, NH₃
- **Geocoding API**: Convert city names to coordinates
- **Weather maps**: Radar, satellite, precipitation layers

### Ease of Use
- **Excellent documentation** with examples in multiple languages
- **8+ million developers** using the platform
- Simple RESTful API with JSON/XML output
- ODbL license (requires attribution)

### Data Coverage
- **Global coverage** via lat/lon coordinates
- Data from 100,000+ weather stations
- Government weather alerts (NOAA, EUMETNET)
- Updates: Every 10 min (Pro+), 1-2 hours (Free)

### Popular Use Cases
- Mobile weather apps
- IoT devices
- Travel applications
- Agriculture monitoring

---

## 2. WeatherAPI.com

### Pricing
| Plan | Price | Calls/Month | Features |
|------|-------|-------------|----------|
| Free | $0 | 100K | 3-day forecast, past 1 day history |
| Starter | $7/mo | 3M | 7-day forecast, 7-day history |
| Pro+ | $25/mo | 5M | 300-day future, 365-day history |
| Business | $65/mo | 10M | Full features including solar |
| Enterprise | Custom | Custom | 15-min intervals, wind @100m |

### Key Features
- **Real-time weather**: Updated every 10-15 minutes
- **Forecast**: Up to 14 days (3-day free)
- **History**: From Jan 1, 2010 onwards (on paid plans)
- **Astronomy API**: Sunrise, sunset, moon phases
- **Sports API**: Cricket, football, golf, F1 events
- **Marine Weather**: Tide data, water temperature
- **Air Quality**: CO, O₃, NO₂, SO₂, PM2.5, PM10
- **Pollen Data**: Hazel, Alder, Birch, Grass, etc.
- **30+ languages supported**

### Ease of Use
- Very simple API structure
- Interactive API Explorer
- Swagger/OpenAPI documentation
- GitHub SDKs available
- Bulk request support (Pro+)

### Data Coverage
- **Global coverage** for all locations
- Data from thousands of public and private weather stations
- AI/machine learning-enhanced forecasting
- Forecast updated every 4-6 hours

### Popular Use Cases
- Feature-rich weather apps
- Marine/nautical applications
- Sports event planning
- Health apps (pollen tracking)

---

## 3. Tomorrow.io (formerly ClimaCell)

### Pricing
| Plan | Price | Features |
|------|-------|----------|
| Free | $0 | 5-day forecast, 1 location, 1 alert, 24hr history |
| Enterprise | Contact Sales | 14-day forecast, premium data layers, custom SLAs |

### Key Features
- **60+ data layers**: Weather, air quality, pollen, solar, soil, fire, flood
- **Hyperlocal accuracy**: 500m resolution
- **Historical**: Up to 20 years
- **Forecast**: Up to 14 days (Enterprise)
- **Map tiles**: Integrates with Mapbox, Google Maps
- **Weather Monitoring API**: Alert triggers and webhooks
- **Route API**: Weather along travel routes
- **AI-powered**: Proprietary AI/ML models

### Ease of Use
- Timeline API: Single endpoint for all time ranges
- Comprehensive documentation
- Postman collection available
- Active GitHub community
- LLM-ready natural language API

### Data Coverage
- **Global coverage** with 1-2 km high-res models (US/Europe)
- Satellite constellation (DeepSky) for proprietary data
- Real-time: Updated every minute
- 99.9% uptime guarantee

### Popular Use Cases
- AI/ML weather applications
- Logistics and route optimization
- Renewable energy (solar/wind)
- Aviation and maritime
- Insurance and risk management

---

## 4. Visual Crossing

### Pricing
| Plan | Price | Records/Month | Key Features |
|------|-------|---------------|--------------|
| Free | $0 | 1,000/day | Commercial use OK, attribution required |
| Metered | $0.0001/record | Unlimited | Pay-as-you-go |
| Professional | $35/mo | 10M | 10K records/query, 100 locations/query |
| Corporate | $150/mo | Unlimited | Energy/ag elements, 10 users |
| Enterprise | Custom | Custom | No attribution, external sharing |

### Key Features
- **Unified API**: Historical, current, and forecast in one call
- **Historical depth**: 50+ years of hourly data
- **Forecast**: 15-day with sub-hourly options
- **Output formats**: JSON and CSV
- **Specialized data**: Solar radiation, wind energy, degree days
- **Agriculture elements**: Soil moisture, evapotranspiration
- **Maritime data**: Wave height, swell direction
- **Event tracking**: Hail, tornadoes, earthquakes

### Ease of Use
- **Single API call** for all weather data needs
- Web-based Query Builder
- OData connector (Corporate+)
- Bulk dataset downloads
- Excellent for Excel/Google Sheets integration

### Data Coverage
- **Global coverage** at 10km resolution
- Sources: Ground stations, satellites, RADAR
- 100,000+ weather stations
- Reanalysis data for historical accuracy

### Popular Use Cases
- Data science and analytics
- Historical weather analysis
- Climate research
- Business intelligence (Power BI)
- Agricultural planning

---

## 5. Open-Meteo

### Pricing
| Plan | Price | Limits |
|------|-------|--------|
| **FREE** | $0 | **Unlimited for non-commercial** |
| Commercial | Contact | Custom pricing |

### Key Features
- **Completely free** for non-commercial use
- **No API key required**
- **Forecast API**: Up to 14 days
- **Historical API**: 80+ years (back to 1940)
- **Ensemble Models**: 200+ individual forecasts
- **Climate Change API**: IPCC predictions to 2050
- **Marine API**: Ocean wave forecasts
- **Air Quality API**: Pollution + pollen
- **Flood API**: River discharge forecasts
- **Geocoding + Elevation APIs**: Built-in

### Ease of Use
- Simple JSON API
- No registration needed
- Semantic versioning for stability
- Response time: <10ms
- Multiple language support

### Data Coverage
- **Global coverage** at 10km resolution
- Local 1-2 km models (US/Europe)
- Data from national weather services:
  - DWD (Germany)
  - NOAA (USA)
  - MeteoFrance
  - CMC (Canada)
- Updated hourly

### Popular Use Cases
- Open-source projects
- Academic research
- Personal projects
- Non-profits
- Startups (cost-conscious)

---

## 6. Weatherbit.io

### Pricing
| Plan | Price | Requests/Day |
|------|-------|--------------|
| Free | $0 | 50 |
| Standard | ~$50/mo | 25,000 |
| Plus | ~$150/mo | 250,000 |
| Business | ~$500/mo | 2M |
| Enterprise | Custom | 2M+ |

### Key Features
- **Forecast**: 16-day daily, 240-hour hourly, 60-minute minutely
- **Historical**: 5-25 years depending on plan
- **Air Quality API**: Included in Business+
- **Ag-Weather API**: Agricultural metrics
- **Energy API**: Degree days, heating/cooling
- **Lightning API**: Real-time and historical
- **Maps API**: Weather overlays
- **Climate Normals**: Long-term averages

### Ease of Use
- RESTful API with JSON output
- Good documentation
- 21-day free trial (no card required)
- Subscription usage API for monitoring

### Data Coverage
- **Global coverage**
- Commercial use allowed on all paid plans
- 99.5% uptime on paid plans

### Popular Use Cases
- Agriculture applications
- Energy sector (degree days)
- Lightning tracking apps
- Insurance risk assessment

---

## 7. AccuWeather

### Pricing
| Plan | Price | Notes |
|------|-------|-------|
| Limited Free | $0 | Very restricted |
| Enterprise | Contact Sales | Custom contracts |

### Key Features
- **Superior Accuracy™** reputation
- **MinuteCast®**: Minute-by-minute precipitation
- **Location API**: Rich location database
- **Weather Alarms**: Severe weather alerts
- **Imagery**: Maps and radar
- **Indices**: Health, outdoor, travel indices

### Ease of Use
- Enterprise-focused
- Requires approval for API access
- Comprehensive documentation

### Data Coverage
- **Global coverage**
- **Hyperlocal**: 1-3 minute updates in some areas
- Proprietary forecasting models

### Popular Use Cases
- Commercial weather apps
- Broadcast media
- Large enterprises
- Premium consumer products

---

## Comparison Matrix

### Pricing Value for Different Scenarios

| Scenario | Recommended API | Why |
|----------|-----------------|-----|
| Hobby/Personal | **Open-Meteo** | Completely free, no limits |
| Startup/MVP | **WeatherAPI.com** | $7/mo gets you started |
| Historical Analysis | **Visual Crossing** | Best historical depth, CSV output |
| Mobile App | **OpenWeatherMap** | Best docs, largest community |
| Enterprise/AI | **Tomorrow.io** | 60+ data layers, hyperlocal |
| Agriculture | **Weatherbit** | Dedicated Ag-Weather API |
| Marine/Nautical | **WeatherAPI.com** | Best marine/tide data at low cost |

### API Call Limits (Free Tier Comparison)

| API | Free Calls | Rate Limit |
|-----|------------|------------|
| Open-Meteo | **Unlimited** | Fair use |
| WeatherAPI.com | 100K/mo | ~3/min |
| OpenWeatherMap | 1K/day | 60/min |
| Tomorrow.io | Generous | Unknown |
| Visual Crossing | 1K/day | 1 concurrent |
| Weatherbit | 50/day | 1/sec |

---

## Recommendations by Use Case

### 🏠 Personal Projects / Learning
**Winner: Open-Meteo**
- Zero cost, no registration
- Excellent documentation
- No attribution required
- Full feature set

### 📱 Mobile/Consumer App
**Winner: OpenWeatherMap**
- Most popular = most Stack Overflow answers
- One Call API simplifies development
- Strong community support
- Reliable free tier for testing

### 💼 Small Business / SaaS
**Winner: WeatherAPI.com**
- Most affordable paid plans
- Rich feature set (astronomy, sports, marine)
- Good free tier (100K calls)
- Easy migration path as you grow

### 📊 Data Science / Analytics
**Winner: Visual Crossing**
- CSV output for easy analysis
- 50+ years of historical data
- Query Builder for non-programmers
- Bulk download capabilities

### 🚚 Logistics / Fleet Management
**Winner: Tomorrow.io**
- Route-based weather API
- Hyperlocal accuracy
- Alert webhooks for conditions
- Real-time updates

### 🌾 Agriculture
**Winner: Weatherbit or Tomorrow.io**
- Weatherbit: Dedicated Ag-Weather API, degree days
- Tomorrow.io: Soil moisture, evapotranspiration data

### ⚡ Energy / Solar
**Winner: Visual Crossing or Tomorrow.io**
- Visual Crossing: Solar radiation data at low cost
- Tomorrow.io: Comprehensive energy layer suite

---

## Final Thoughts

1. **Start with Open-Meteo** if cost is a concern and you're building something non-commercial. It's genuinely free with no catches.

2. **OpenWeatherMap** is the safe default for most commercial applications. It's what everyone knows, but pricing scales quickly.

3. **WeatherAPI.com** offers the best bang for buck if you need features like astronomy, sports, or marine data.

4. **Tomorrow.io** is the premium choice for AI/ML applications or when hyperlocal accuracy matters.

5. **Visual Crossing** is unbeatable for historical data analysis and data science workflows.

6. **Avoid AccuWeather** unless you have enterprise budget and need their specific accuracy claims.

*Last updated: March 2026*
