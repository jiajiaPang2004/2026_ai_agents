# Campaign Spend Distribution Insight Agent

This agent provides a detailed analysis of marketing campaign spending across multiple channels, including monthly seasonal trends and 2D distribution matrices.

## 🌟 Application Purpose
The primary purpose of this tool is to transform raw campaign spending data into actionable insights. It calculates:
1.  **Row-wise Distribution**: How each campaign (e.g., ads1) distributes its specific budget across different channels.
2.  **Column-wise Distribution**: The market share of each campaign within a specific channel (e.g., channel1).
3.  **Seasonal Trends**: Visualizes budget allocations tailored for Summer peaks (`ads1`), Holiday peaks (`ads2`), and Always-on strategies (`ads3`).

## ⚙️ Standard Workflow
Follow these steps to maintain and update your spending insights:

1.  **Update Data**: 
    - Open `campaign_spend.csv`.
    - Modify the `spend` column with your latest dollar values.
    - *Optional*: Use `generate_data.py` to reset with random seasonal data.
2.  **Generate Report**:
    - Run the visualization tool:
      ```bash
      python visualize.py
      ```
3.  **review Results**:
    - Open `distribution_report.html` in any browser to see the matrices and AI insights.

## 🛠️ Usage Modes

### 1. Interactive Analytics (HTML Report)
The fastest way to see aligned tables and "Total" percentages:
```bash
python visualize.py
```
*Output: `distribution_report.html`*

### 2. AI Chat (Conversational Analysis)
Chat with the agent to ask specific questions about the data:
- **Web UI**: `adk web`
- **Terminal**: `adk run "Analyze the campaign spend."`

## 📂 Project Structure
- `agent.py`: ADK Agent definition and execution logic.
- `tools.py`: Core logic for matrix calculations, HTML generation, and AI insights.
- `generate_data.py`: Script for generating realistic, seasonally-weighted dummy data.
- `visualize.py`: Entry point for generating the HTML report.
- `requirements.txt`: Project dependencies.
- `campaign_spend.csv`: The source of truth for all data.
