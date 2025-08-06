
import asyncio
import time
import re
import imaplib
import email
import json
import sys
import os
from datetime import datetime, timedelta 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use import Agent, Browser, Controller, ActionResult
from browser_use.llm import ChatGoogle
from utils.otp_utils import get_otp_from_gmail
from prompts.ken_login_prompt import PROMPT
GLOBAL_KEN_EMAIL = None
GLOBAL_PASSWORD = None
GLOBAL_OTP_SENDERS = [
    'no-reply@the-ken.com',
    'info@the-ken.com'
]
controller = Controller()

@controller.action('Ask human for OTP', domains=['the-ken.com'])
def provide_otp_automatically(question: str) -> ActionResult:
    if GLOBAL_KEN_EMAIL and GLOBAL_PASSWORD:
        print(f"🤖 Agent asked: '{question}'. Attempting to retrieve OTP automatically...")
        otp = get_otp_from_gmail(
            email_address=GLOBAL_KEN_EMAIL,
            password=GLOBAL_PASSWORD,
            valid_senders=GLOBAL_OTP_SENDERS
        )
        if otp:
            print("✅ OTP successfully retrieved automatically.")
            # Return the OTP as extracted content for the agent to use
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

class KenLoginWithOTP:
    """
    A class to encapsulate the login process for The Ken using browser-use Agent.
    """
    def __init__(self, KEN_EMAIL: str, password: str, api_key: str):
        self.KEN_EMAIL = KEN_EMAIL
        self.password = password
        self.api_key = api_key
        self.llm = ChatGoogle(
            model="gemini-2.0-flash-exp", # Using the specified LLM model
            api_key=self.api_key
        )

    def get_login_prompt(self) -> str:
        return PROMPT.format(KEN_EMAIL=self.KEN_EMAIL)

    async def login(self):
        """
        Executes the login process using the browser-use Agent.
        """
        browser = Browser()
        try:
            agent = Agent(
                task=self.get_login_prompt(),
                llm=self.llm,
                browser=browser,
                use_vision=True,
                max_actions_per_step=30,
                controller=controller # Pass the configured global controller
            )

            print("🤖 Logging into The Ken...")
            result = await agent.run()
            print("✅ Login result:", result)
            print("📦 Raw extracted content:\n", result.extracted_content())
        finally:
            await browser.close() # Ensure the browser is closed even if an error occurs

async def main():

    global GLOBAL_KEN_EMAIL, GLOBAL_PASSWORD

    KEN_EMAIL = os.getenv("GMAIL_EMAIL")
    PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    GLOBAL_KEN_EMAIL = KEN_EMAIL
    GLOBAL_PASSWORD = PASSWORD

    login_bot = KenLoginWithOTP(KEN_EMAIL, PASSWORD, GOOGLE_API_KEY)
    await login_bot.login()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal Error: {e}")