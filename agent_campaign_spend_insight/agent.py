import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from tools import get_campaign_data, get_distribution_matrices
import os
from dotenv import load_dotenv

load_dotenv()
# The API key and platform settings are now loaded from the .env file automatically.
# hidden API key
# Attempt to import SessionService from possible locations
try:
    from google.adk.services.session_service import SessionService
except ImportError:
    try:
        from google.adk.session_service import SessionService
    except ImportError:
        # Fallback/Mock if absolutely necessary, but usually it's in one of the above
        class SessionService:
            pass

# Define the agent
campaign_insight_agent = Agent(
    name="CampaignInsightAgent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a marketing analyst providing insights into campaign spend distribution. "
        "Use the 'get_distribution_matrices' tool to fetch the 2D spending matrices (row-wise and column-wise %). "
        "Analyze these matrices and present the following to the user: "
        "1. A markdown table for the Row-wise Distribution (Ads across Channels), summarizing where each ad allocates its budget. "
        "2. A markdown table for the Column-wise Distribution (Campaigns within Channels), summarizing the competition within each channel. "
        "3. A brief interpretation of the key findings, such as which channel is dominated by which ad, or which ad is most diversified."
    ),
    tools=[get_distribution_matrices]
)

async def main():
    # Attempt Runner initialization with common patterns
    try:
        session_service = SessionService()
        runner = Runner(agent=campaign_insight_agent, session_service=session_service)
    except Exception:
        # Some versions might use different keyword arguments
        try:
             runner = Runner(root_agent=campaign_insight_agent)
        except Exception:
             # Last resort, let adk handles it via CLI if this fails
             print("Error initializing Runner programmatically. Try running via: adk run")
             return

    result = await runner.run_async("Provide the 2D spending distribution analysis.")
    print("\n--- AGENT ANALYSIS ---\n")
    print(result.text)

if __name__ == "__main__":
    asyncio.run(main())
