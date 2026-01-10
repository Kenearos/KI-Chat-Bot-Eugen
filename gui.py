"""
Dashboard GUI for Eugen Bot
Live monitoring interface using FreeSimpleGUI
"""
import FreeSimpleGUI as sg
import threading
from datetime import datetime
from queue import Queue


class Dashboard:
    """Live monitoring dashboard for bot activity"""

    def __init__(self, bot=None):
        """
        Initialize dashboard

        Args:
            bot: Reference to the main bot instance
        """
        self.bot = bot
        sg.theme('DarkBlue3')

        # Event queue for thread-safe updates
        self.event_queue = Queue()
        self.window = None
        self.is_running = False

        # Statistics
        self.stats = {
            "messages": 0,
            "api_calls": 0,
            "errors": 0,
            "start_time": datetime.now()
        }

    def log_event(self, event_type, data):
        """
        Add event to queue for display

        Args:
            event_type (str): Type of event (chat_message, api_call, etc.)
            data (dict): Event data
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        if event_type == "chat_message":
            msg = f"{timestamp} | {data['username']}: {data['content']}"
            self.stats["messages"] += 1
        elif event_type == "mention_detected":
            msg = f"{timestamp} | [MENTION] Bot addressed by {data['username']}"
        elif event_type == "api_call":
            msg = f"{timestamp} | [API] → Perplexity ({data.get('model', 'sonar-pro')})"
            self.stats["api_calls"] += 1
        elif event_type == "api_response":
            preview = data['content'][:60] + "..." if len(data['content']) > 60 else data['content']
            msg = f"{timestamp} | [RESPONSE] {preview}"
        elif event_type == "bot_response":
            preview = data['content'][:60] + "..." if len(data['content']) > 60 else data['content']
            msg = f"{timestamp} | Eugen: @{data['username']} {preview}"
        elif event_type == "error":
            msg = f"{timestamp} | ❌ ERROR: {data['error']}"
            self.stats["errors"] += 1
        elif event_type == "info":
            msg = f"{timestamp} | ℹ {data['message']}"
        elif event_type == "warning":
            msg = f"{timestamp} | ⚠ {data['message']}"
        elif event_type == "context_loaded":
            msg = f"{timestamp} | [CONTEXT] Loaded {data['count']} messages for {data['username']}"
        else:
            msg = f"{timestamp} | {event_type}: {data}"

        self.event_queue.put(msg)

    def create_layout(self):
        """Create the GUI layout"""
        # Header
        header = [
            [sg.Text("EUGEN BOT - LIVE DASHBOARD", font=("Arial", 16, "bold"))],
            [sg.Text("Status: 🟢 RUNNING", key="-STATUS-", font=("Arial", 10))],
            [sg.Text("Uptime: 00:00:00", key="-UPTIME-", size=(20, 1)),
             sg.Text("Messages: 0", key="-MSG-COUNT-", size=(20, 1)),
             sg.Text("API Calls: 0", key="-API-COUNT-", size=(20, 1)),
             sg.Text("Errors: 0", key="-ERROR-COUNT-", size=(20, 1))],
            [sg.HorizontalSeparator()]
        ]

        # Live feed
        feed = [
            [sg.Text("LIVE ACTIVITY FEED", font=("Arial", 12, "bold"))],
            [sg.Multiline(
                size=(140, 25),
                key="-LOG-",
                disabled=True,
                autoscroll=True,
                font=("Courier New", 9)
            )]
        ]

        # Control buttons
        controls = [
            [sg.HorizontalSeparator()],
            [
                sg.Button("Clear Log", key="-CLEAR-"),
                sg.Button("Reset Stats", key="-RESET-"),
                sg.Button("Stop Bot", key="-STOP-", button_color=("white", "red"))
            ]
        ]

        # Combine all sections
        layout = header + feed + controls

        return layout

    def run(self):
        """Run the dashboard GUI in main thread"""
        layout = self.create_layout()
        self.window = sg.Window(
            "Eugen Bot Dashboard",
            layout,
            finalize=True,
            size=(1000, 650)
        )
        self.is_running = True

        # Main event loop
        while self.is_running:
            event, values = self.window.read(timeout=100)

            # Handle window close
            if event == sg.WINDOW_CLOSED or event == "-STOP-":
                self.is_running = False
                if self.bot:
                    self.bot.stop()
                break

            # Handle clear log
            if event == "-CLEAR-":
                self.window["-LOG-"].update("")

            # Handle reset stats
            if event == "-RESET-":
                self.stats = {
                    "messages": 0,
                    "api_calls": 0,
                    "errors": 0,
                    "start_time": datetime.now()
                }

            # Update log with queued events
            while not self.event_queue.empty():
                try:
                    msg = self.event_queue.get_nowait()
                    self.window["-LOG-"].print(msg)
                except Exception:
                    break

            # Update statistics
            self._update_stats()

        self.window.close()

    def _update_stats(self):
        """Update statistics display"""
        if not self.window:
            return

        # Calculate uptime
        uptime = datetime.now() - self.stats["start_time"]
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # Update displays
        self.window["-UPTIME-"].update(f"Uptime: {uptime_str}")
        self.window["-MSG-COUNT-"].update(f"Messages: {self.stats['messages']}")
        self.window["-API-COUNT-"].update(f"API Calls: {self.stats['api_calls']}")
        self.window["-ERROR-COUNT-"].update(f"Errors: {self.stats['errors']}")

    def show_error(self, title, message):
        """Show error popup"""
        sg.popup_error(message, title=title)

    def show_info(self, title, message):
        """Show info popup"""
        sg.popup(message, title=title)

    def stop(self):
        """Stop the dashboard"""
        self.is_running = False
        if self.window:
            self.window.close()


class SetupWizard:
    """Configuration wizard for first-time setup"""

    def __init__(self):
        sg.theme('DarkBlue3')

    def run(self):
        """
        Run the setup wizard

        Returns:
            dict: Configuration values or None if cancelled
        """
        layout = [
            [sg.Text("EUGEN CONFIGURATION WIZARD", font=("Arial", 16, "bold"))],
            [sg.HorizontalSeparator()],

            [sg.Text("TWITCH CONFIGURATION", font=("Arial", 12, "bold"))],
            [sg.Text("Bot Nickname:", size=(20, 1)), sg.Input("Eugen", key="-BOT-NAME-")],
            [sg.Text("OAuth Token:", size=(20, 1)), sg.Input("oauth:", key="-OAUTH-", password_char="*")],
            [sg.Text("Channel:", size=(20, 1)), sg.Input("#", key="-CHANNEL-")],

            [sg.HorizontalSeparator()],

            [sg.Text("PERPLEXITY CONFIGURATION", font=("Arial", 12, "bold"))],
            [sg.Text("API Key:", size=(20, 1)), sg.Input("pplx-", key="-API-KEY-", password_char="*")],
            [sg.Text("Model:", size=(20, 1)),
             sg.Combo([
                 "sonar-pro",
                 "sonar",
                 "sonar-reasoning",
                 "sonar-reasoning-pro",
                 "sonar-deep-research"
             ], default_value="sonar-pro", key="-MODEL-", size=(25, 1)),
             sg.Button("?", key="-MODEL-INFO-", size=(2, 1))],
            [sg.Text("", size=(20, 1)),
             sg.Text("Recommended: sonar-pro (chat bots)", font=("Arial", 8), text_color="gray")],
            [sg.Text("Max Tokens:", size=(20, 1)), sg.Input("450", key="-TOKENS-")],

            [sg.HorizontalSeparator()],

            [sg.Checkbox("Enable Debug Mode", default=True, key="-DEBUG-")],
            [sg.Checkbox("Auto Reconnect", default=True, key="-RECONNECT-")],

            [sg.HorizontalSeparator()],

            [sg.Button("Save & Start", key="-SAVE-"), sg.Button("Cancel", key="-CANCEL-")]
        ]

        window = sg.Window("Eugen Setup", layout)

        config = None
        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == "-CANCEL-":
                break

            # Show model info
            if event == "-MODEL-INFO-":
                model_info = """PERPLEXITY API MODELS (2026):

🔵 sonar-pro (RECOMMENDED FOR CHAT BOTS)
   - Deeper content understanding
   - 2x more search results than sonar
   - Enhanced search accuracy
   - Best for complex, multi-step queries
   - Built on Llama 3.3 70B
   ➜ Use this for chat bots!

🟢 sonar
   - Lightweight and fast
   - Lower cost
   - Simple question-answer features
   - Good for speed-optimized applications
   - Built on Llama 3.3 70B

🧠 sonar-reasoning
   - Real-time reasoning with search
   - Shows reasoning process
   - Good for problem-solving
   - Moderate speed

⚡ sonar-reasoning-pro
   - Powered by DeepSeek-R1
   - Advanced reasoning capabilities
   - Visible reasoning content via API
   - Best for complex logical tasks
   - Higher cost

📊 sonar-deep-research
   - Long-form research reports
   - Source-dense output
   - Best for detailed analysis
   - Slower, comprehensive responses

RECOMMENDATION:
• Chat Bots: sonar-pro
• Quick answers: sonar
• Complex reasoning: sonar-reasoning-pro
• Research: sonar-deep-research"""
                sg.popup_scrolled(model_info, title="Model Information", size=(70, 30))
                continue

            if event == "-SAVE-":
                # Validate inputs
                if not values["-OAUTH-"].startswith("oauth:"):
                    sg.popup_error("Twitch OAuth token must start with 'oauth:'")
                    continue

                if not values["-CHANNEL-"].startswith("#"):
                    sg.popup_error("Channel must start with '#'")
                    continue

                if not values["-API-KEY-"].startswith("pplx-"):
                    sg.popup_error("Perplexity API key must start with 'pplx-'")
                    continue

                # Build config
                config = {
                    "TWITCH_BOT_NICKNAME": values["-BOT-NAME-"],
                    "TWITCH_OAUTH_TOKEN": values["-OAUTH-"],
                    "TWITCH_CHANNEL": values["-CHANNEL-"],
                    "PERPLEXITY_API_KEY": values["-API-KEY-"],
                    "PERPLEXITY_MODEL": values["-MODEL-"],
                    "MAX_TOKENS": values["-TOKENS-"],
                    "DEBUG_MODE": "true" if values["-DEBUG-"] else "false",
                    "AUTO_RECONNECT": "true" if values["-RECONNECT-"] else "false"
                }
                break

        window.close()
        return config
