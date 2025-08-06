import asyncio
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use import Agent, Browser, Controller, ActionResult
from browser_use.llm import ChatGoogle
from prompts.ET_login_prompt import PROMPT as ET_PROMPT
from utils.otp_utils import get_otp_from_gmail
# === Global Variables ===
GLOBAL_EMAIL = None
GLOBAL_PASSWORD = None
GLOBAL_OTP_SENDERS = []

# === Controller Setup ===
controller = Controller()

@controller.action('Ask human for OTP', domains=['economictimes.indiatimes.com'])
def provide_otp_automatically(question: str) -> ActionResult:
    """
    Handles OTP fetch using get_otp_from_gmail() and fallback to manual input.
    """
    if GLOBAL_EMAIL and GLOBAL_PASSWORD and GLOBAL_OTP_SENDERS:
        print(f"🤖 Trying automatic OTP fetch for: {GLOBAL_EMAIL}")
        otp = get_otp_from_gmail(
            email_address=GLOBAL_EMAIL,
            password=GLOBAL_PASSWORD,
            valid_senders=GLOBAL_OTP_SENDERS,
            max_wait=120
        )
        if otp:
            return ActionResult(
                extracted_content=f"The OTP retrieved automatically is: {otp}",
                include_in_memory=True
            )
        else:
            print("❌ Auto OTP failed. Asking for manual input.")
    
    answer = input(f"{question} > Please enter OTP manually: ")
    return ActionResult(
        extracted_content=f"The human responded with OTP: {answer}",
        include_in_memory=True
    )


# === EconomicTimesLoginWithOTP Class ===
class EconomicTimesLoginWithOTP:
    def __init__(self, email: str, password: str, gmail_app_password: str, api_key: str, otp_senders: list):
        self.email = email
        self.password = password
        self.gmail_password = gmail_app_password
        self.api_key = api_key
        self.otp_senders = otp_senders

        self.llm = ChatGoogle(
            model="gemini-2.0-flash-exp",
            api_key=self.api_key
        )

    def get_prompt(self) -> str:
        return ET_PROMPT.format(
            email=self.email,
            password=self.password
        )
    async def login(self):
        """
        Uses browser agent to automate login and extract session.
        """
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
            print("🤖 Logging in to Economic Times...")
            result = await agent.run()
            print("✅ Login successful. Extracted content:\n", result.extracted_content())
        finally:
            await browser.close()


# === Main Async Function ===
async def main():
    global GLOBAL_EMAIL, GLOBAL_PASSWORD, GLOBAL_OTP_SENDERS

    # === 🔐 Credentials Setup ===
    ECONOMIC_TIMES_EMAIL = os.getenv("GMAIL_EMAIL")
    ECONOMIC_TIMES_PASSWORD = os.getenv("ECONOMIC_TIMES_PASSWORD")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OTP_SENDERS = ["noreply@economictimes.com", "info@economictimes.com"]

    # === 🌍 Set Globals for OTP action ===
    GLOBAL_EMAIL = ECONOMIC_TIMES_EMAIL
    GLOBAL_PASSWORD = GMAIL_APP_PASSWORD
    GLOBAL_OTP_SENDERS = OTP_SENDERS

    # === 🤖 Start Login Bot ===
    login_bot = EconomicTimesLoginWithOTP(
        email=ECONOMIC_TIMES_EMAIL,
        password=ECONOMIC_TIMES_PASSWORD,
        gmail_app_password=GMAIL_APP_PASSWORD,
        api_key=GOOGLE_API_KEY,
        otp_senders=OTP_SENDERS
    )
    await login_bot.login()


# === Entrypoint ===
if __name__ == "__main__":
    try:
        print("🚀 Starting Automation at", datetime.now().strftime("%c"))
        asyncio.run(main())
    except Exception as e:
        print(f"💥 Fatal Error: {e}")
