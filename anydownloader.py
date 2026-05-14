import sys
import os
import shutil
import re
from pathlib import Path
from typing import Dict, Any, List

# Required: pip install yt-dlp rich
try:
    import yt_dlp
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.table import Table
except ImportError:
    print("CRITICAL: Missing dependencies. Run: pip install yt-dlp rich")
    sys.exit(1)

console = Console()

class ARCNexusArchitect:
    """Hardened media ingestion engine with automatic input correction."""

    def __init__(self, output_dir: str):
        self.output_dir = self._sanitize_path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.has_ffmpeg = shutil.which("ffmpeg") is not None
        self.session_stats = {"success": [], "failed": []}

    def _sanitize_path(self, path_str: str) -> Path:
        """Fixes common path errors and prevents URL-as-Folder crashes."""
        # Detect if user accidentally put a URL in the path prompt
        if "://" in path_str or "www." in path_str:
            fallback = Path.home() / "Downloads" / "ARC_Archive"
            console.print(f"[bold orange3]WARNING:[/bold orange3] URL detected in folder path. Redirecting to: {fallback}")
            return fallback
        
        # Strip illegal Windows characters from the final folder name
        clean_path = re.sub(r'[<>:"|?*]', '', path_str)
        return Path(clean_path).resolve()

    def _build_options(self, mode: str, res: int, subs: bool) -> dict:
        ydl_opts = {
            'outtmpl': str(self.output_dir / '%(title).100s.%(ext)s'), # Limit title length to 100 chars
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }

        if self.has_ffmpeg:
            ydl_opts['postprocessors'] = [{'key': 'FFmpegMetadata'}]
            if subs:
                ydl_opts['writesubtitles'] = True
                ydl_opts['subtitleslangs'] = ['en', 'all']
                ydl_opts['postprocessors'].append({'key': 'FFmpegEmbedSubtitle'})

        if mode == "Audio Only":
            ydl_opts['format'] = 'bestaudio/best'
            if self.has_ffmpeg:
                ydl_opts['postprocessors'].insert(0, {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                })
        else:
            if self.has_ffmpeg:
                ydl_opts['format'] = f"bestvideo[height<={res}]+bestaudio/best"
                ydl_opts['merge_output_format'] = 'mp4'
            else:
                ydl_opts['format'] = f"best[height<={min(res, 720)}][ext=mp4]/best"

        return ydl_opts

    def execute_ingestion(self, urls: List[str], mode: str, res: int, subs: bool):
        console.print(f"\n[bold cyan]TARGET ARCHIVE:[/bold cyan] {self.output_dir}")
        console.print(f"[bold cyan]FUSION CORE (FFmpeg):[/bold cyan] {'[green]ONLINE[/green]' if self.has_ffmpeg else '[red]OFFLINE[/red]'}")
        console.print("-" * 50)

        ydl_opts = self._build_options(mode, res, subs)

        for index, url in enumerate(urls, 1):
            console.print(f"\n[bold yellow]Target [{index}/{len(urls)}]:[/bold yellow] {url}")
            
            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=40, pulse_style="bright_cyan"),
                "[progress.percentage]{task.percentage:>3.0f}%",
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                
                task_id = progress.add_task("Handshaking...", total=100)

                def progress_hook(d: Dict[str, Any]):
                    if d['status'] == 'downloading':
                        p = d.get('downloaded_bytes', 0)
                        t = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
                        progress.update(task_id, description="[cyan]Streaming...", completed=p, total=t)
                    elif d['status'] == 'finished':
                        progress.update(task_id, description="[green]Finalizing...", completed=1, total=1)

                ydl_opts['progress_hooks'] = [progress_hook]

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        if info:
                            title = info.get('title', 'Unknown Media')
                            self.session_stats["success"].append(title)
                        else:
                            raise Exception("Bypass occurred - No info returned.")
                except Exception as e:
                    self.session_stats["failed"].append(url)
                    console.print(f"  [red]✖ ERROR:[/red] Ingestion Failure.")

        self._print_session_report()

    def _print_session_report(self):
        table = Table(title="\n[bold cyan]A.R.C. SESSION TELEMETRY[/bold cyan]")
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right")
        table.add_row("Total Processed", str(len(self.session_stats['success']) + len(self.session_stats['failed'])))
        table.add_row("Successful", f"[green]{len(self.session_stats['success'])}[/green]")
        table.add_row("Failed", f"[red]{len(self.session_stats['failed'])}[/red]")
        console.print(table)

def get_input_urls() -> List[str]:
    while True:
        source_input = Prompt.ask("[bold yellow]Enter Target URL OR path to a .txt file[/bold yellow]").strip()
        
        # Check if the "URL" is actually a local folder accidentally
        if os.path.isdir(source_input):
            console.print("[bold orange3]NOTICE:[/bold orange3] You entered a folder. Checking for 'links.txt' inside...")
            potential_file = Path(source_input) / "links.txt"
            if potential_file.exists():
                source_input = str(potential_file)
            else:
                console.print("[bold red]ERROR:[/bold red] That is a folder, not a URL or a .txt file.")
                continue

        if source_input.lower().endswith('.txt'):
            target_file = Path(source_input)
            if target_file.is_file():
                with open(target_file, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip() and not line.startswith('#')]
            else:
                console.print("[bold red]ERROR:[/bold red] File not found.")
                continue
        
        if "://" not in source_input and "." not in source_input:
            console.print("[bold red]ERROR:[/bold red] Invalid URL format.")
            continue

        return [source_input]

def main():
    console.print(Panel.fit(
        " [bold cyan]A.R.C. NEXUS ENGINE[/bold cyan] ",
        subtitle="v4.1.0 - Auto-Sanitization Protocol"
    ))

    # Path Detection with Safety Loop
    default_path = str(Path.home() / "Downloads" / "ARC_Archive")
    target_dir = Prompt.ask("[bold yellow]Enter Destination Folder[/bold yellow]", default=default_path)
    
    urls = get_input_urls()
    
    media_type = Prompt.ask("[bold yellow]Select Type[/bold yellow]", choices=["Full Video", "Audio Only"], default="Full Video")
    res_choice = 1080
    subs_choice = False

    if media_type == "Full Video":
        res_choice = IntPrompt.ask("[bold yellow]Max Resolution[/bold yellow]", choices=["480", "720", "1080", "2160"], default=1080)
        subs_choice = Confirm.ask("[bold yellow]Embed Subtitles?[/bold yellow]", default=True)

    architect = ARCNexusArchitect(output_dir=target_dir)
    architect.execute_ingestion(urls, media_type, res_choice, subs_choice)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]System override initiated. Goodbye.[/bold red]")
        sys.exit(0)

        