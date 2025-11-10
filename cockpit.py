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
            "Memory",
            "Immutable Log",
            "TriggerMesh",
            "Crypto Keys",
            "Fusion",
            "ML/DL",
            "Self Healing",
            "Agentic Spine",
            "System Status",
        ]
        self.selected_tab = 0

        # UI Components
        self.activity_bar = Frame(title="Activity", body=self._get_activity_bar_content())
        self.chat_content = TextArea(text="", read_only=True)
        self.log_content = TextArea(text="", read_only=True)
        self.status_content = TextArea(text="", read_only=True)
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
        return TextArea(text=content, read_only=True)

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
            else:
                self.open_powershell_for_tab()

        return kb

    def update_ui(self):
        self.activity_bar.body = self._get_activity_bar_content()
        self.main_content.title = self.tabs[self.selected_tab]
        if self.selected_tab == 0:
            self.main_content.body = self.chat_content
        elif self.selected_tab == 2: # Immutable Log
            self.main_content.body = self.log_content
        elif self.selected_tab == 9: # System Status
            self.main_content.body = self.status_content
        else:
            self.main_content.body = Window()

    async def send_message(self, message):
        self.append_to_chat(f"You: {message}")
        await self.websocket.send(message)

    def append_to_chat(self, text):
        self.chat_content.text += f"\n{text}"

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
                self.update_status()
            )

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
