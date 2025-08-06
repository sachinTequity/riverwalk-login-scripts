import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

os.environ["ANONYMIZED_TELEMETRY"] = "false"

# Add the parent directory to the Python path to allow imports from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use import Agent, Browser, Controller, ActionResult
from browser_use.llm import ChatOpenAI, ChatGoogle
from utils.otp_utils import get_otp_from_gmail
from prompts.TMC_login_prompt import PROMPT
# Global credentials for OTP function
GLOBAL_EMAIL = None
GLOBAL_APP_PASSWORD = None

controller = Controller()

@controller.action('Ask human for OTP', domains=['themorningcontext.com'])
def provide_otp_automatically(question: str) -> ActionResult:
    """
    Automatically fetch OTP from Gmail or ask user for manual input
    """
    if GLOBAL_EMAIL and GLOBAL_APP_PASSWORD:
        print(f"🤖 Fetching OTP automatically for {GLOBAL_EMAIL}")
        
        # Define valid senders for The Morning Context
        valid_senders = [
            'noreply@themorningcontext.com',
            'hello@themorningcontext.com',
            'support@themorningcontext.com',
            'no-reply@themorningcontext.com'
        ]
        # Try to get OTP automatically
        otp = get_otp_from_gmail(
            GLOBAL_EMAIL, 
            GLOBAL_APP_PASSWORD, 
            valid_senders,
        )
        
        if otp:
            print(f"✅ OTP retrieved automatically: {otp}")
            return ActionResult(
                extracted_content=f"The OTP retrieved automatically is: {otp}",
                include_in_memory=True
            )
        else:
            print("⚠️ OTP not retrieved automatically. Asking user.")
    
    # Fallback to manual input
    print(f"📝 {question}")
    otp_input = input("Please enter OTP manually: ")
    return ActionResult(
        extracted_content=f"The human responded with OTP: {otp_input}",
        include_in_memory=True
    )

class MorningContextLoginWithOTP:
    def __init__(self, email, app_password, api_key):
        self.email = email
        self.app_password = app_password
        self.api_key = api_key
        self.llm = ChatGoogle(model="gemini-2.0-flash-exp", api_key=api_key)

    def load_prompt(self) -> str:
        return PROMPT
    async def login(self):
        browser = Browser()
        try:
            agent = Agent(
                task=self.load_prompt(),
                llm=self.llm,
                browser=browser,
                use_vision=True,
                max_actions_per_step=30,
                controller=controller
            )
            print("🤖 Logging in to The Morning Context...")
            result = await agent.run()
            print("✅ Login Successful.")
            print("📦 Extracted Content:\n", result.extracted_content())
        finally:
            await browser.close()

async def main():
    global GLOBAL_EMAIL, GLOBAL_APP_PASSWORD

    # Credentials from environment variables
    email = os.getenv("GMAIL_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    # Set globals for OTP access
    GLOBAL_EMAIL = email
    GLOBAL_APP_PASSWORD = app_password

    login = MorningContextLoginWithOTP(email, app_password, google_api_key)
    await login.login()

if __name__ == "__main__":
    print("🚀 Starting:", datetime.now().strftime("%c"))
    asyncio.run(main()) 
