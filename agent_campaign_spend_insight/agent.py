import asyncio
import os
import sys
import time
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from .tools import get_distribution_matrices_data

load_dotenv()

# Define the agent
campaign_insight_agent = Agent(
    name="CampaignInsightAgent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a marketing analyst providing insights into campaign spend distribution. "
        "Use the 'get_distribution_matrices_data' tool to fetch the 2D spending matrices. "
        "Analyze these matrices and present a clear breakdown to the user."
    ),
    tools=[get_distribution_matrices_data]
)

async def run_analysis():
    print("Initializing Agent Runner...")
    session_service = InMemorySessionService()
    app_name = "campaign_analytics"
    user_id = "default_user"
    session_id = "default_session"
    
    await session_service.create_session(
        app_name=app_name, 
        user_id=user_id, 
        session_id=session_id
    )
    
    runner = Runner(
        agent=campaign_insight_agent, 
        app_name=app_name, 
        session_service=session_service
    )
    
    query = "Provide the 2D spending distribution analysis from my data."
    
    max_retries = 3
    retry_delay = 40 # Seconds (matching the ~36s requested by the API error)
    
    for attempt in range(max_retries):
        print(f"Running Analysis (Attempt {attempt + 1}/{max_retries})...")
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=genai_types.Content(
                    role="user", 
                    parts=[genai_types.Part.from_text(text=query)]
                ),
            ):
                if event.is_final_response():
                    print("\n--- AGENT ANALYSIS ---\n")
                    print(event.content.parts[0].text)
                    return True
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "ResourceExhausted" in err_msg:
                if attempt < max_retries - 1:
                    print(f"\n[!] Rate limit hit. Waiting {retry_delay} seconds for API quota reset...")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    print("\n[!] Rate limit persistent. Please try again in a few minutes.")
            else:
                print(f"\n[!] An fatal error occurred: {e}")
            return False
    return False

def main():
    try:
        asyncio.run(run_analysis())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception:
        pass

if __name__ == "__main__":
    main()
