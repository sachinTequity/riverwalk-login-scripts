import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use import Agent, Browser, Controller, ActionResult
from browser_use.llm import ChatGoogle
from prompts.captable_login_prompt import PROMPT as CAPTABLE_PROMPT
controller = Controller()

class CapTableSessionScraper:
    def __init__(self, email: str, password: str, api_key: str):
        self.email = email
        self.password = password
        self.api_key = api_key
        self.llm = ChatGoogle(
            model="gemini-2.0-flash-exp",
            api_key=self.api_key
        )

    def get_prompt(self) -> str:
        return CAPTABLE_PROMPT.format(email=self.email, password=self.password)

    async def run(self):
        browser = Browser()
        try:
            agent = Agent(
                task=self.get_prompt(),
                llm=self.llm,
                browser=browser,
                use_vision=True,
                max_actions_per_step=30,
                controller=controller
            )
            print("🤖 Launching CapTable agent...")
            result = await agent.run()
            print("✅ Agent completed.\n")
            print("📦 Extracted Content:\n", result.extracted_content())
        finally:
            await browser.close()

async def main():
    # Get credentials from environment variables
    CAPTABLE_EMAIL = os.getenv("GMAIL_EMAIL")
    CAPTABLE_PASSWORD = os.getenv("CAPTABLE_PASSWORD")
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

    scraper = CapTableSessionScraper(CAPTABLE_EMAIL, CAPTABLE_PASSWORD, GEMINI_API_KEY)
    await scraper.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
