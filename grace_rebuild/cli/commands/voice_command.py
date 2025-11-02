"""
Voice command - Audio recording and playback
"""

import asyncio
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from ..grace_client import GraceAPIClient


class VoiceCommand:
    """Voice recording and TTS"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
        self.temp_dir = Path.home() / ".grace" / "audio"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute(self, action: Optional[str] = None, *args):
        """Execute voice command"""
        if not self.client.is_authenticated():
            self.console.print("[red]Please login first[/red]")
            return
        
        if action == "record":
            await self.record_audio()
        elif action == "speak":
            text = " ".join(args) if args else None
            await self.text_to_speech(text)
        else:
            await self.interactive_menu()
    
    async def record_audio(self, duration: int = 5):
        """Record audio from microphone"""
        try:
            import pyaudio
            import wave
        except ImportError:
            self.console.print("[red]PyAudio not installed. Install with: pip install pyaudio[/red]")
            return
        
        self.console.print(f"\n[bold yellow]🎤 Recording for {duration} seconds...[/bold yellow]")
        self.console.print("[dim]Speak now...[/dim]\n")
        
        # Audio settings
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        audio = pyaudio.PyAudio()
        
        try:
            # Open stream
            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            frames = []
            
            # Record with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("Recording...", total=duration * RATE // CHUNK)
                
                for _ in range(0, int(RATE / CHUNK * duration)):
                    data = stream.read(CHUNK)
                    frames.append(data)
                    progress.advance(task)
            
            stream.stop_stream()
            stream.close()
            
            # Save to file
            output_file = self.temp_dir / f"recording_{asyncio.get_event_loop().time()}.wav"
            
            wf = wave.open(str(output_file), 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            self.console.print(f"[green]✓ Recording saved: {output_file.name}[/green]")
            
            # Upload and transcribe
            await self.upload_and_transcribe(output_file)
            
        except Exception as e:
            self.console.print(f"[red]Recording error: {e}[/red]")
        finally:
            audio.terminate()
    
    async def upload_and_transcribe(self, audio_file: Path):
        """Upload audio file and get transcription"""
        self.console.print("\n[cyan]Uploading and transcribing...[/cyan]")
        
        with self.console.status("Processing audio...", spinner="dots"):
            response = await self.client.upload_audio(audio_file)
        
        if response.success:
            transcription = response.data.get("transcription", "")
            confidence = response.data.get("confidence", 0)
            
            self.console.print("\n[bold green]Transcription:[/bold green]")
            self.console.print(Panel(
                transcription,
                border_style="green",
                subtitle=f"Confidence: {confidence:.1%}"
            ))
            
            # Optionally send to chat
            if transcription:
                send_chat = await asyncio.to_thread(
                    self.console.input,
                    "\nSend to chat? (y/N): "
                )
                
                if send_chat.lower() == 'y':
                    chat_response = await self.client.chat(transcription)
                    if chat_response.success:
                        self.console.print("\n[bold magenta]Grace:[/bold magenta]")
                        self.console.print(Panel(
                            chat_response.data.get("response", ""),
                            border_style="magenta"
                        ))
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def text_to_speech(self, text: Optional[str] = None):
        """Convert text to speech"""
        if not text:
            text = await asyncio.to_thread(
                self.console.input,
                "Text to speak: "
            )
        
        if not text:
            self.console.print("[yellow]Cancelled[/yellow]")
            return
        
        with self.console.status("Generating speech...", spinner="dots"):
            response = await self.client.text_to_speech(text)
        
        if response.success:
            audio_url = response.data.get("audio_url")
            audio_data = response.data.get("audio_data")
            
            self.console.print("[green]✓ Speech generated[/green]")
            
            if audio_data:
                # Save and play audio
                output_file = self.temp_dir / f"tts_{asyncio.get_event_loop().time()}.wav"
                
                import base64
                with open(output_file, 'wb') as f:
                    f.write(base64.b64decode(audio_data))
                
                self.console.print(f"[dim]Saved to: {output_file}[/dim]")
                
                # Try to play
                await self.play_audio(output_file)
            elif audio_url:
                self.console.print(f"[cyan]Audio URL:[/cyan] {audio_url}")
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def play_audio(self, audio_file: Path):
        """Play audio file"""
        try:
            from pydub import AudioSegment
            from pydub.playback import play
            
            self.console.print("[cyan]▶ Playing audio...[/cyan]")
            
            audio = AudioSegment.from_wav(str(audio_file))
            play(audio)
            
            self.console.print("[green]✓ Playback complete[/green]")
        except ImportError:
            self.console.print("[yellow]pydub not installed. Install with: pip install pydub[/yellow]")
            self.console.print(f"[dim]Audio saved to: {audio_file}[/dim]")
        except Exception as e:
            self.console.print(f"[red]Playback error: {e}[/red]")
    
    async def interactive_menu(self):
        """Interactive voice menu"""
        while True:
            self.console.clear()
            self.console.print("[bold magenta]🎤 Voice Interface[/bold magenta]\n")
            
            self.console.print("1. Record audio (5 seconds)")
            self.console.print("2. Record audio (10 seconds)")
            self.console.print("3. Record audio (custom duration)")
            self.console.print("4. Text to speech")
            self.console.print("0. Back to main menu")
            
            choice = await asyncio.to_thread(self.console.input, "\nChoice: ")
            
            if choice == "1":
                await self.record_audio(duration=5)
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "2":
                await self.record_audio(duration=10)
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "3":
                duration = await asyncio.to_thread(
                    self.console.input,
                    "Duration (seconds): "
                )
                if duration.isdigit():
                    await self.record_audio(duration=int(duration))
                    await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "4":
                await self.text_to_speech()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "0":
                break
