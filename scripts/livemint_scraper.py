import asyncio
import time
import re
import imaplib
import email
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the Python path to allow imports from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    
from datetime import datetime, timedelta 
from utils.otp_utils import get_otp_from_gmail
from browser_use import Agent, Browser, Controller, ActionResult
from browser_use.llm import ChatGoogle, ChatOpenAI
from prompts.livemint_login_prompt import PROMPT
# Global variables to store credentials.
GLOBAL_LIVEMENT_EMAIL = None
GLOBAL_PASSWORD = None

# Initialize the Controller
controller = Controller()

# The action name must match what the agent is instructed to use in the prompt.
# Corrected action name to match the prompt's instruction.
@controller.action('provide_otp_automatically', domains=['livemint.com'])
def provide_otp_automatically(question: str) -> ActionResult:

    if GLOBAL_LIVEMENT_EMAIL and GLOBAL_PASSWORD:
        print(f"🤖 Agent asked: '{question}'. Attempting to retrieve OTP automatically...")
        valid_senders = [
            'alerts@accounts.hindustantimes.com'
        ]
        # Try to get OTP automatically
        otp = get_otp_from_gmail(
            GLOBAL_LIVEMENT_EMAIL, 
            GLOBAL_PASSWORD, 
            valid_senders,
        )
        if otp:
            print("✅ OTP successfully retrieved automatically.")
            return ActionResult(extracted_content=f'The OTP retrieved automatically is: {otp}', include_in_memory=True)
        else:
            print("❌ Automatic OTP retrieval failed. Please check your email manually or increase wait time.")
            answer = input(f'{question} > sachin please fill the otp (Automatic retrieval failed)')
            return ActionResult(extracted_content=f'The human responded with OTP: {answer}', include_in_memory=True)
    else:
        print("❌ Email credentials not configured for automatic OTP retrieval. Asking human for OTP.")
        answer = input(f'{question} > sachin please fill the otp')
        return ActionResult(extracted_content=f'The human responded with OTP: {answer}', include_in_memory=True)

print("start the code", datetime.now().strftime("%c"))

class LivementLoginWithOTP:
    def __init__(self, LIVEMENT_EMAIL: str, password: str, api_key: str):
        self.LIVEMENT_EMAIL = LIVEMENT_EMAIL
        self.password = password
        self.api_key = api_key
        self.llm = ChatGoogle(
            model="gemini-2.0-flash-exp",
            api_key=self.api_key
        )

    def get_login_prompt(self) -> str:
        return PROMPT.format(LIVEMENT_EMAIL=self.LIVEMENT_EMAIL)

    async def login(self):
        browser = Browser()
        try:
            agent = Agent(
                task=self.get_login_prompt(),
                llm=self.llm,
                browser=browser,
                use_vision=True,
                max_actions_per_step=30,
                controller=controller
            )

            print("🤖 Logging into Livement...")
            result = await agent.run()
            print("✅ Login result:", result)
            print("📦 Raw extracted content:\n", result.extracted_content())
        finally:
            await browser.close()

async def main():
    global GLOBAL_LIVEMENT_EMAIL, GLOBAL_PASSWORD

    LIVEMENT_EMAIL = os.getenv("GMAIL_EMAIL")
    PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    GLOBAL_LIVEMENT_EMAIL = LIVEMENT_EMAIL
    GLOBAL_PASSWORD = PASSWORD

    login_bot = LivementLoginWithOTP(LIVEMENT_EMAIL, PASSWORD, GOOGLE_API_KEY)
    await login_bot.login()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal Error: {e}")