import pandas as pd
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def get_campaign_data() -> str:
    csv_path = "campaign_spend.csv"
    if not os.path.exists(csv_path):
        return "Error: campaign_spend.csv not found."
    df = pd.read_csv(csv_path)
    return df.to_string(index=False)

def get_distribution_matrices_data():
    csv_path = "campaign_spend.csv"
    if not os.path.exists(csv_path):
        return None, None, None

    df = pd.read_csv(csv_path)
    pivot_df = df.pivot_table(index='campaign', columns='channel', values='spend', aggfunc='sum').fillna(0)
    
    # Row-wise distribution
    row_sums = pivot_df.sum(axis=1)
    row_dist = pivot_df.div(row_sums, axis=0) * 100
    row_dist['Total'] = 100.0
    
    # Column-wise distribution
    col_sums = pivot_df.sum(axis=0)
    col_dist = pivot_df.div(col_sums, axis=1) * 100
    col_dist.loc['Total'] = col_dist.sum(axis=0)
    
    return row_dist.round(2), col_dist.round(2), pivot_df

def get_ai_insights(df_matrix, analysis_type="row") -> str:
    """Generates dynamic insights for a specific matrix."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Dynamic logic for fallback
    insights = []
    if analysis_type == "row":
        # Drop the 'Total' column for analysis
        data = df_matrix.drop(columns=['Total'])
        for campaign, rows in data.iterrows():
            top_channel = rows.idxmax()
            percentage = rows.max()
            insights.append(f"• **{campaign}** focuses primarily on **{top_channel}** with {percentage}% budget allocation.")
        fallback = "**Ad Strategy Summary**:<br>" + "<br>".join(insights)
    else:
        # Drop the 'Total' row if it exists
        data = df_matrix.copy()
        if 'Total' in data.index:
            data = data.drop(index=['Total'])
        
        for channel in data.columns:
            top_campaign = data[channel].idxmax()
            percentage = data[channel].max()
            insights.append(f"• **{channel}** is led by **{top_campaign}** holding a {percentage}% share of the channel budget.")
        fallback = "**Channel Share Summary**:<br>" + "<br>".join(insights)

    if not api_key:
        return fallback

    client = genai.Client(api_key=api_key)
    context = "campaign-centric (how ads spend)" if analysis_type == "row" else "channel-centric (who spends in channel)"
    prompt = f"Analyze this {context} distribution matrix and provide 3 punchy bullet points explaining the focus. CRITICAL: Use the exact percentages from the table. Keep it under 50 words.\\n\\nData:\\n{df_matrix.to_string()}"
    
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text.replace('\n', '<br>')
    except:
        return fallback

def generate_html_report(output_file="distribution_report.html"):
    row_dist, col_dist, pivot_df = get_distribution_matrices_data()
    if row_dist is None: return "Error"

    # Get granular insights
    row_insight = get_ai_insights(row_dist, "row")
    col_insight = get_ai_insights(col_dist, "col")

    def df_to_html_section(df, title, insight):
        df_reset = df.reset_index()
        table_html = df_reset.to_html(classes='table table-bordered table-hover text-center align-middle', index=False)
        return f"""
        <div class="row mb-5">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-white py-3">
                        <h3 class="h5 mb-0 fw-bold text-center">{title}</h3>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            {table_html}
                        </div>
                    </div>
                    <div class="card-footer bg-light border-top-0 py-3">
                        <div class="insight-label mb-2"><span class="badge bg-indigo">💡 Insight</span></div>
                        <div class="insight-text center-block text-start">{insight}</div>
                    </div>
                </div>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Campaign Spend Analytics</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Outfit', sans-serif; background-color: #f0f4f8; padding: 60px 0; }}
            .container {{ max-width: 960px; }}
            .card {{ border: none; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; }}
            th {{ background-color: #f8fafc !important; font-weight: 700 !important; color: #475569 !important; border-bottom: 2px solid #e2e8f0 !important; text-align: center; }}
            td {{ color: #64748b; text-align: center; }}
            tr:last-child td, tr:last-child th {{ background-color: #f1f5f9; font-weight: 700; color: #1e293b; border-top: 2px solid #cbd5e1; }}
            .bg-indigo {{ background-color: #4f46e5; }}
            .insight-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
            .insight-text {{ font-size: 0.95rem; color: #334155; line-height: 1.6; padding: 0 10px; }}
            .workflow-box {{ background-color: #ffffff; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 25px; margin-top: 50px; }}
            .step-num {{ width: 24px; height: 24px; background: #4f46e5; color: white; display: inline-flex; align-items: center; justify-content: center; border-radius: 50%; font-size: 0.75rem; font-weight: bold; margin-right: 10px; }}
            .table-responsive {{ display: flex; justify-content: center; }}
            table.table {{ width: auto !important; margin: 0 auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="text-center mb-5">
                <h1 class="display-5 fw-bold text-dark mb-2">Campaign Distribution Analysis</h1>
                <p class="text-muted">Interactive Analytics &bull; 2025 Spending Trends</p>
            </div>
            
            {df_to_html_section(row_dist.applymap(lambda x: f"{x}%"), "Matrix A: How Ads Spend (Row = 100%)", row_insight)}
            {df_to_html_section(col_dist.applymap(lambda x: f"{x}%"), "Matrix B: Channel Budget Share (Column = 100%)", col_insight)}
            
            <div class="workflow-box">
                <h4 class="h6 fw-bold text-dark mb-3 text-center">⚙️ Workflow: How to Update Data</h4>
                <div class="small d-flex justify-content-center flex-column align-items-center">
                    <p class="mb-2"><span class="step-num">1</span> Update <code>campaign_spend.csv</code> with your latest dollar values.</p>
                    <p class="mb-0"><span class="step-num">2</span> Run <code>python visualize.py</code> in your terminal to refresh this report.</p>
                </div>
            </div>

            <p class="text-center text-muted small mt-5">{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}, this report was generated</p>
        </div>
    </body>
    </html>
    """
    with open(output_file, "w", encoding="utf-8") as f: f.write(html_content)
    return os.path.abspath(output_file)
