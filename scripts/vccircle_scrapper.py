import asyncio
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the Python path to allow imports from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use import Agent, Browser, ActionResult
from browser_use.llm import ChatGoogle, ChatOpenAI
from utils.otp_utils import get_otp_from_gmail
from prompts.vccircle_login_prompt import PROMPT
# Global variables for VCCircle credentials
GLOBAL_VCCIRCLE_EMAIL = None
GLOBAL_VCCIRCLE_PASSWORD = None

print("start the code", datetime.now().strftime("%c"))

class VCCircleLogin:
    """
    A class to encapsulate the login process for VCCircle using browser-use Agent.
    This class handles email and password-based login only.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=self.api_key
        )
        # self.llm = ChatGoogle(
        #     model="gemini-2.0-flash-exp",
        #     api_key=self.api_key
        # )

    def get_login_prompt(self) -> str:
        return PROMPT

    async def login(self):
        """
        Executes the login process using the browser-use Agent for VCCircle.
        """
        browser = Browser()
        try:
            agent = Agent(
                task=self.get_login_prompt(),
                llm=self.llm,
                browser=browser,
                use_vision=True,
                max_actions_per_step=30
            )

            print("🤖 Logging into VCCircle...")
            result = await agent.run()
            print("📦 Raw extracted content:\n", result.extracted_content())
        finally:
            await browser.close()

async def main():
    """
    Main function to set up credentials and initiate the login process for VCCircle.
    """
    # Declare global variables to assign values
    global GLOBAL_VCCIRCLE_EMAIL, GLOBAL_VCCIRCLE_PASSWORD

    # 🔒 Get credentials from environment variables
    GOOGLE_API_KEY = os.getenv("OPENAI_API_KEY")

    # --- Run VCCircle Login ---
    login_bot_vcc = VCCircleLogin(GOOGLE_API_KEY)
    print("\n--- Attempting login for VCCircle ---")
    await login_bot_vcc.login()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal Error: {e}")