
import asyncio
import websockets
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.widgets import TextArea, Frame, Box
from prompt_toolkit.key_binding import KeyBindings

class GraceCockpit:
    def __init__(self):
        self.tabs = [
            "Chat",
            "Cognition",
            "Grace Intelligence",
            "ML/DL",
            "NLP",
            "Causal Analysis",
            "Knowledge Base",
            "Evaluation",
            "Governance",
            "Parliament",
            "Self Healing",
            "Agentic Coding Agent",
            "Ingestion",
            "Memory",
            "Immutable Log",
            "TriggerMesh",
            "Crypto Keys",
            "Fusion",
            "System Status",
        ]
        self.selected_tab = 0

        # UI Components
        self.activity_bar = Frame(title="Activity", body=self._get_activity_bar_content())
        self.chat_content = TextArea(text="", read_only=True)
        self.log_content = TextArea(text="", read_only=True)
        self.status_content = TextArea(text="", read_only=True)
        self.cognition_content = TextArea(text="", read_only=True)
        self.intelligence_content = TextArea(text="", read_only=True)
        self.ml_content = TextArea(text="", read_only=True)
        self.nlp_content = TextArea(text="", read_only=True)
        self.causal_content = TextArea(text="", read_only=True)
        self.knowledge_content = TextArea(text="", read_only=True)
        self.evaluation_content = TextArea(text="", read_only=True)
        self.governance_content = TextArea(text="", read_only=True)
        self.parliament_content = TextArea(text="", read_only=True)
        self.healing_content = TextArea(text="", read_only=True)
        self.ingestion_content = TextArea(text="", read_only=True)
        self.agentic_content = TextArea(text="", read_only=True)
        self.file_explorer = Frame(title="File Explorer", body=Window())
        self.memory_explorer = Frame(title="Memory Explorer", body=Window())
        self.main_content = Frame(title=self.tabs[self.selected_tab], body=self.chat_content)
        self.input_field = TextArea(height=3, prompt="> ", multiline=False)

        # Layout
        self.root_container = HSplit([
            VSplit([
                Box(self.activity_bar, width=20),
                self.main_content,
            ]),
            self.input_field,
        ])

        self.layout = Layout(self.root_container)
        self.app = Application(layout=self.layout, full_screen=True, key_bindings=self._get_key_bindings())

    def _get_activity_bar_content(self):
        content = ""
        for i, tab in enumerate(self.tabs):
            if i == self.selected_tab:
                content += f"> {tab}\n"
            else:
                content += f"  {tab}\n"
        return Window(content=content)

    def _get_key_bindings(self):
        kb = KeyBindings()

        @kb.add("c-c", "c-q")
        def _(event):
            event.app.exit()

        @kb.add("up")
        def _(event):
            self.selected_tab = (self.selected_tab - 1) % len(self.tabs)
            self.update_ui()

        @kb.add("down")
        def _(event):
            self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
            self.update_ui()

        @kb.add("enter")
        def _(event):
            if self.selected_tab == 0: # Chat
                asyncio.create_task(self.send_message(self.input_field.text))
                self.input_field.text = ""
            elif self.selected_tab == 12: # Ingestion
                self.upload_file()
            else:
                self.open_powershell_for_tab()

        return kb

    def update_ui(self):
        self.activity_bar.body = self._get_activity_bar_content()
        self.main_content.title = self.tabs[self.selected_tab]
        if self.selected_tab == 0:
            self.main_content.body = self.chat_content
        elif self.selected_tab == 14: # Immutable Log
            self.main_content.body = self.log_content
        elif self.selected_tab == 1: # Cognition
            self.main_content.body = self.cognition_content
        elif self.selected_tab == 2: # Grace Intelligence
            self.main_content.body = self.intelligence_content
        elif self.selected_tab == 3: # ML/DL
            self.main_content.body = self.ml_content
        elif self.selected_tab == 4: # NLP
            self.main_content.body = self.nlp_content
        elif self.selected_tab == 5: # Causal Analysis
            self.main_content.body = self.causal_content
        elif self.selected_tab == 6: # Knowledge Base
            self.main_content.body = self.file_explorer
        elif self.selected_tab == 13: # Memory
            self.main_content.body = self.memory_explorer
        elif self.selected_tab == 7: # Evaluation
            self.main_content.body = self.evaluation_content
        elif self.selected_tab == 8: # Governance
            self.main_content.body = self.governance_content
        elif self.selected_tab == 9: # Parliament
            self.main_content.body = self.parliament_content
        elif self.selected_tab == 10: # Self Healing
            self.main_content.body = self.healing_content
        elif self.selected_tab == 11: # Agentic Coding Agent
            self.main_content.body = self.agentic_content
        elif self.selected_tab == 12: # Ingestion
            self.main_content.body = self.ingestion_content
        elif self.selected_tab == 18: # System Status
            self.main_content.body = self.status_content
        else:
            self.main_content.body = Window()

        if self.selected_tab == 12: # Ingestion
            self.input_field.text = "Press Enter to select a file to upload."
        else:
            self.input_field.text = ""

    async def send_message(self, message):
        self.append_to_chat(f"You: {message}")
        await self.websocket.send(message)

    def append_to_chat(self, text):
        self.chat_content.text += f"\n{text}"

    def upload_file(self):
        # This is a placeholder. In a real application, you would
        # use a file dialog to select a file and then upload it.
        self.ingestion_content.text = "File upload is not yet implemented."

    def open_powershell_for_tab(self):
        tab_name = self.tabs[self.selected_tab]
        asyncio.create_task(self._open_powershell(f"Set-Location -Path C:\\Users\\aaron\\grace_2; .\\cockpit.ps1; Write-Host 'Welcome to the {tab_name} tab!'"))

    async def _open_powershell(self, command):
        await asyncio.create_subprocess_shell(f"start powershell -NoExit -Command \"{command}\"")

    async def run(self):
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            self.websocket = websocket
            await asyncio.gather(
                self.app.run_async(),
                self.stream_logs(),
                self.receive_messages(),
                self.update_status(),
                self.update_cognition(),
                self.update_intelligence(),
                self.update_ml(),
                self.update_nlp(),
                self.update_causal(),
                self.update_knowledge(),
                self.update_evaluation(),
                self.update_governance(),
                self.update_parliament(),
                self.update_healing(),
                self.update_ingestion(),
                self.update_agentic()
            )

    async def update_agentic(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/agentic/status") as ws:
                    while True:
                        data = await ws.recv()
                        self.agentic_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_ingestion(self):
        while True:
            try:
                # This is a placeholder. In a real application, you would
                # use a file dialog to select a file and then upload it.
                await asyncio.sleep(5)
            except Exception:
                await asyncio.sleep(5)

    async def update_healing(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/healing/status") as ws:
                    while True:
                        data = await ws.recv()
                        self.healing_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_parliament(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/parliament/sessions") as ws:
                    while True:
                        data = await ws.recv()
                        self.parliament_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_governance(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/governance/policies") as ws:
                    while True:
                        data = await ws.recv()
                        self.governance_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_evaluation(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/evaluation/evaluate") as ws:
                    while True:
                        data = await ws.recv()
                        self.evaluation_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_knowledge(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/knowledge/search") as ws:
                    while True:
                        data = await ws.recv()
                        self.knowledge_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_causal(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/causal/visualize") as ws:
                    while True:
                        data = await ws.recv()
                        self.causal_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_nlp(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/terminal/ws") as ws:
                    while True:
                        data = await ws.recv()
                        self.nlp_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_ml(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/ml/status") as ws:
                    while True:
                        data = await ws.recv()
                        self.ml_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_intelligence(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/transcendence/intelligence") as ws:
                    while True:
                        data = await ws.recv()
                        self.intelligence_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_cognition(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8000/api/cognition/status") as ws:
                    while True:
                        data = await ws.recv()
                        self.cognition_content.text = data
            except Exception:
                await asyncio.sleep(5)

    async def update_status(self):
        while True:
            process = await asyncio.create_subprocess_shell(
                ".\\GRACE.ps1 -Status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            self.status_content.text = stdout.decode()
            await asyncio.sleep(5)

    async def receive_messages(self):
        while True:
            message = await self.websocket.recv()
            self.append_to_chat(f"Grace: {message}")

    async def stream_logs(self):
        process = await asyncio.create_subprocess_shell(
            ".\\GRACE.ps1 -Tail",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            self.log_content.text += line.decode()

async def main():
    cockpit = GraceCockpit()
    await cockpit.run()

if __name__ == "__main__":
    asyncio.run(main())
