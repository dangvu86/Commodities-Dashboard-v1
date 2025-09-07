# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based commodity market dashboard that displays real-time commodity price data with interactive charts and analysis. The application features a clean, modern interface with advanced filtering capabilities and performance visualization.

## Architecture

**Main Application Structure:**
- `Home.py` - Main Streamlit app entry point with sidebar filters and main content sections
- `modules/` - Core functionality modules:
  - `data_loader.py` - CSV data loading and preprocessing with caching
  - `calculations.py` - Price change calculations (daily, weekly, monthly, quarterly, YTD)
  - `styling.py` - Clean CSS styling and KPI metrics display
  - `stock_data.py` - Stock price fetching from TCBS API with caching
  - `news_data.py` - News fetching from vnstock API with structured data processing
- `pages/` - Additional Streamlit pages (multi-page app structure)
- `data/` - CSV data files:
  - `Data.csv` - Historical commodity price data
  - `Commo_list.csv` - Commodity metadata (sectors, nations, impact stock codes)

**Key Data Flow:**
1. Data loaded via `load_data()` from CSV files with preprocessing and cleaning
2. Price changes calculated using `calculate_price_changes()` based on latest date
3. Advanced filters applied (sector, nation, change type, commodity)
4. Performance charts generated with tab-based interface
5. Line charts use date range and interval selections from sidebar
6. Stock data fetched from TCBS API based on Impact column stock codes
7. News data fetched from vnstock API and displayed below stock charts with expandable UI

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt
pip install streamlit-aggrid  # Required for advanced table features

# Run the application
streamlit run Home.py

# Run with specific port
streamlit run Home.py --server.port 8501
```

## UI Structure

**Sidebar Organization:**
- **Advanced Filters Section:**
  - Sector multiselect
  - Nation multiselect
  - Change Type multiselect (Positive/Negative/Neutral)
  - Commodity multiselect (filtered by sector selection)
- **Chart Options Section:**
  - Start Date and End Date inputs (side by side)
  - Interval selection (Daily/Weekly/Monthly/Quarterly)

**Main Content Sections:**
1. **Key Market Metrics & Sector Metrics** - 8 KPI cards in 2x4 grid layout:
   - Market: Most Bullish, Most Bearish, Highest Volatility (TBD), Monthly Leader
   - Sector: Strongest Sector, Extreme Moves (>±2%), Future KPI 3, Future KPI 4
2. **Detailed Price Table** - Advanced AG-Grid table with scroll view, conditional formatting, and professional styling
3. **Performance Chart & Impact** - Tab-based charts with split view (decreasing/increasing performance)
4. **Commodity Price Trends** - Interactive line chart with stock impact integration
5. **News Section** - Expandable news items from vnstock API displayed below stock charts when impact stocks are selected

## Key Technical Details

**Data Processing:**
- Uses `@st.cache_data(ttl=3600)` for performance optimization
- **Google Drive Integration:** Loads data from Google Drive URLs with fallback to local files
- **Environment Variables:** Supports both .env files (local) and Streamlit Cloud secrets (production)
- All main sections use latest date from data
- Chart Options (date range/interval) applied to commodity price trends line chart
- Robust data filtering with multiple criteria
- Stock data integration with TCBS API fetching and timezone handling

**Styling System:**
- Clean design with `--primary-teal: #00816D`, `--secondary-red: #e11d48`, `--accent-green: #10b981`
- Light background (`--bg-light: #f8fafc`) with white content containers
- No background images - modern card-based layout
- Responsive design with proper margins and shadows

**Performance Charts:**
- **Tab-based Interface:** 5 tabs (Daily, Weekly, Monthly, Quarterly, YTD)
- **Split View Design:** Left side for decreasing performance, right side for increasing
- **Balanced Layout:** Empty bars added to balance both sides equally
- **Impact Stock Integration:** Uses Direct Impact and Inverse Impact columns from Commo_list.csv
- **Combined Labels:** Single label combining percentage and impact stocks with proper spacing
  - Decreasing: `HPG, HSG, NKG - negative   -2.5%`
  - Increasing: `2.5%   HPG, HSG, NKG - positive`
- **Impact Logic:**
  - Negative charts: Direct Impact → `stock - negative`, Inverse Impact → `stock - positive`
  - Positive charts: Direct Impact → `stock - positive`, Inverse Impact → `stock - negative`
  - Commodities with both impacts show combined: `PLX - negative, VJC, HVN - positive -1.8%`
- **No Axis Display:** X and Y axes completely hidden for clean presentation
- **Text Positioning:** `textposition='outside'` for combined labels on invisible bars
- **Extended Range:** X-axis range multiplied by 2 to prevent label overlap

**Chart Technical Specs:**
- Uses `make_subplots` with `horizontal_spacing=0` for seamless split
- Dynamic height calculation: `max(300, max_items * 40)`
- Margin settings: `l=50, r=50, t=60, b=20` to prevent text cutoff
- Empty bars use `rgba(0,0,0,0)` for transparency
- Hover templates show full commodity information

**Data Dependencies:**
- **Google Drive URLs:** Primary data source via environment variables
  - `DATA_CSV_URL`: Historical commodity price data (Date, Commodities, Price)
  - `COMMO_LIST_CSV_URL`: Commodity metadata (Commodities, Sector, Nation, Impact, Direct Impact, Inverse Impact)
  - `STEEL_DATA_CSV_URL`: Steel production data (en_OrganName, production metrics, consumption data)
- **Fallback:** Local CSV files in `data/` directory if URLs not available
- All date calculations based on latest available data
- Change type calculation uses weekly performance for classification
- Direct Impact and Inverse Impact columns are included in internal data processing but hidden from detailed price table display

**Stock Impact Integration:**
- **Automatic Detection:** Extracts stock codes from Direct Impact and Inverse Impact columns when commodities selected
- **Side-by-Side Charts:** Displays commodity prices (left) and stock prices (right) when impact stocks available
- **Synchronized Options:** Both charts use same date range and interval from sidebar
- **TCBS API Integration:** Fetches Vietnamese stock data with rate limiting and caching
- **Chart Styling:** Clean line charts without markers, using lighter color palette
- **Timezone Handling:** Proper datetime conversion to avoid comparison errors

**KPI Metrics Updates:**
- **Market Metrics:** Most Bullish, Most Bearish, Highest Volatility (placeholder), Monthly Leader
- **Sector Metrics:** Strongest Sector (highest avg %Week), Extreme Moves count (>±2% weekly change)
- **Calculation Logic:** Strongest sector based on average weekly performance, extreme moves count absolute weekly changes > 2%

**News Integration:**
- **vnstock API:** Uses `Vnstock().stock().company.news()` for Vietnamese stock news
- **Caching Strategy:** News cached for 30 minutes (1800 seconds) to balance freshness with performance
- **Progressive Loading:** News fetched after charts are rendered to prevent blocking UI
- **Error Handling:** Graceful fallback when news API fails, with user-friendly error messages
- **Content Processing:** Automatic summary generation, date formatting, and Vietnamese text handling

## Advanced Table Features (AG-Grid)

**Detailed Price Table Implementation:**
- **AG-Grid Integration:** Uses `streamlit-aggrid` for professional table rendering
- **Light Theme:** Clean white background with subtle row striping
- **Scroll View:** No pagination - continuous scroll through all data
- **Conditional Formatting:** 
  - Green background (`rgba(34,197,94,alpha)`) for positive percentage values
  - Red background (`rgba(239,68,68,alpha)`) for negative percentage values  
  - Alpha blending based on absolute value magnitude
- **Number Formatting:**
  - Price columns: Thousand separators with 2 decimal places (e.g., `1,234.56`)
  - Percentage columns: Display as numbers (e.g., `2.34` instead of `2.34%`)
  - All formatting handled via JavaScript formatters
- **Column Configuration:**
  - Sortable and filterable columns
  - Right-aligned numeric columns
  - Icon headers (🌍 Nation, 📈 Impact Stocks, 🏭 Sector, 📦 Commodity)
  - Resizable column widths (default 120px, minimum 100px)
- **Styling Details:**
  - Font family: Manrope, sans-serif
  - Cell padding: 6px 8px for compact layout
  - Row height: 32px, Header height: 40px
  - Font sizes: 13px (cells), 12px (headers)
  - Hover effects and professional borders

**Performance Chart Enhancements:**
- **Soft Color Palette:** Bar colors use 60% opacity for subtle appearance
  - Negative bars: `rgba(225, 29, 72, 0.6)` (soft red)
  - Positive bars: `rgba(16, 185, 129, 0.6)` (soft green)
- **Commodity Selection:** Alphabetically sorted multiselect for easy navigation
- **Interactive Features:** Standard Plotly hover and zoom, no click interactions

**Module Structure:**
- `styling.py` contains `display_aggrid_table()` and `display_news_section()` functions
- Comprehensive CSS theming for AG-Grid components and news UI
- JavaScript conditional formatting with JsCode
- Price and percentage formatters for consistent display
- News styling with expandable containers, Vietnamese time formatting, and responsive design
- `display_aggrid_table()` filters out Direct Impact and Inverse Impact columns from table display
- `calculations.py` includes Direct Impact and Inverse Impact in data processing but separates display columns
## Error Handling and Debugging

**Common Issues:**
- **Data Loading Failures:** Check CSV file paths in `data/` directory and ensure proper column formats
- **Stock Data API Issues:** TCBS API has rate limits - uses caching with 1-hour TTL to prevent excessive requests
- **Performance Issues:** All main data operations use `@st.cache_data(ttl=3600)` - clear cache if data updates needed
- **Chart Rendering:** Plotly charts use specific margin and spacing settings - modify carefully to avoid text cutoff
- **AG-Grid Styling:** Complex CSS theming in `styling.py` - test thoroughly when modifying table appearance

**Development Tips:**
- Use `streamlit run Home.py --server.runOnSave true` for auto-reload during development
- Clear browser cache if CSS changes don't appear
- Check browser console for JavaScript errors related to AG-Grid formatting
- Test with different data sizes - chart layouts dynamically adjust height based on item count

## Data Requirements

**CSV Structure:**
- `Data.csv`: Must contain 'Date', 'Commodities', 'Price' columns with proper formatting
- `Commo_list.csv`: Must contain 'Commodities', 'Sector', 'Nation', 'Impact' columns
- Date format: Ensure consistent date parsing (handled in data_loader.py)
- Commodity names: Must match exactly between both CSV files (whitespace cleaned automatically)
- Impact column: Contains Vietnamese stock codes for TCBS API integration

**Performance Considerations:**
- Data caching expires every 3600 seconds (1 hour)
- Large datasets may require increased chart height calculations
- Stock API calls are rate-limited and cached to prevent timeouts

## Environment Variables & Deployment

**Local Development (.env file):**
```env
DATA_CSV_URL=https://drive.google.com/uc?export=download&id=1277Wt1-eeAJnefUVH1Esjnd5Yju7GcEa
COMMO_LIST_CSV_URL=https://drive.google.com/uc?export=download&id=1ZDlHju9lnCYykAKEeipH_heWG2yqqVOr
STEEL_DATA_CSV_URL=https://drive.google.com/uc?export=download&id=1pGJAID4bprGrxx_4CuxWcs969iYQpMsq
```

**Streamlit Cloud Secrets (Production):**
```toml
DATA_CSV_URL = "https://drive.google.com/uc?export=download&id=1277Wt1-eeAJnefUVH1Esjnd5Yju7GcEa"
COMMO_LIST_CSV_URL = "https://drive.google.com/uc?export=download&id=1ZDlHju9lnCYykAKEeipH_heWG2yqqVOr"
STEEL_DATA_CSV_URL = "https://drive.google.com/uc?export=download&id=1pGJAID4bprGrxx_4CuxWcs969iYQpMsq"
```

**Deployment Process:**
1. **Environment Setup:** Configure secrets in Streamlit Cloud dashboard
2. **Data Source Priority:** Google Drive URLs → Local files fallback
3. **Caching Strategy:** All data loading functions use `@st.cache_data(ttl=3600)`
4. **Error Handling:** Graceful fallback with user-friendly error messages

## Data Loading Functions

**Core Functions in `modules/data_loader.py`:**

- **`load_data()`**: Loads Data.csv and Commo_list.csv with preprocessing and cleaning
  - Supports both Google Drive URLs and local file fallback
  - Cleans column names, handles data types, converts dates
  - Returns: `(df_data, df_list)`

- **`load_steel_data()`**: Loads steel production data from Google Drive
  - Optional dataset for future steel industry analysis
  - Returns: `df_steel` or `None` if URL not configured

- **`load_all_data()`**: Convenience function to load all datasets
  - Combines all data loading with single function call
  - Returns: `(df_data, df_list, df_steel)`

**Integration Details:**
- **python-dotenv**: Loads environment variables from .env file
- **Streamlit Secrets**: Production environment variable management
- **Error Handling**: Try-catch blocks with informative error messages
- **Performance**: All functions cached with 1-hour TTL