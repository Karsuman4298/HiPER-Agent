import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from graph.workflow import HYPERGraph
from config.settings import settings

app = typer.Typer(name=settings.APP_NAME)
console = Console()
graph = HYPERGraph()

@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Start an interactive chat session if no command is passed."""
    if ctx.invoked_subcommand is None:
        console.print(Panel("[bold cyan]Welcome to HiPER-Agent Interactive Mode![/bold cyan]\nType your prompt and press Enter. Press [bold red]Ctrl+C[/bold red] to exit.", title="HiPER-Agent", border_style="bold blue"))
        try:
            while True:
                prompt = console.input("\n[bold green]You >[/bold green] ")
                if prompt.strip():
                    run(prompt)
        except KeyboardInterrupt:
            console.print("\n[bold red]Exiting HiPER-Agent. Goodbye![/bold red]")


@app.command()
def add_contact(name: str, target: str):
    """Add a name-to-contact mapping (phone/email)."""
    import json
    import os
    contacts_file = "contacts.json"
    contacts = {}
    if os.path.exists(contacts_file):
        with open(contacts_file, "r") as f:
            contacts = json.load(f)
    
    contacts[name] = target
    with open(contacts_file, "w") as f:
        json.dump(contacts, f, indent=4)
    console.print(f"[bold green]Success:[/bold green] Contact {name} added as {target}")

@app.command()
def list_contacts():
    """List all saved contacts."""
    import json
    import os
    contacts_file = "contacts.json"
    if not os.path.exists(contacts_file):
        console.print("[yellow]No contacts found.[/yellow]")
        return
    
    with open(contacts_file, "r") as f:
        contacts = json.load(f)
    
    from rich.table import Table
    table = Table(title="HYPER-Agent Contacts")
    table.add_column("Name", style="cyan")
    table.add_column("Target", style="magenta")
    
    for name, target in contacts.items():
        table.add_row(name, target)
    
    console.print(table)

@app.command()
def run(prompt: str):
    """Unified entry point for any multi-agent task (Research, Code, Analyze, etc.)"""
    console.print(Panel(f"User Prompt: [bold white]{prompt}[/bold white]", title="HYPER-Agent Advanced Orchestrator", border_style="bold blue"))
    
    try:
        # The graph nodes now print their status and stream their outputs directly to the console
        result = graph.run(prompt)
        console.print("\n[bold green]System Run Complete.[/bold green]")
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate_limit" in error_msg.lower():
            console.print("\n" + "!" * 80, style="bold red")
            console.print("[bold red][ERROR]: API Rate Limit Exceeded (429)[/bold red]")
            console.print("=" * 80, style="bold red")
            console.print("[yellow]Tip:[/yellow] Groq has reached its daily/minute token quota. Please either:")
            console.print("1. Wait 5-10 minutes for the reset.")
            console.print("2. Switch your [bold].env[/bold] to a smaller model (e.g., [bold]llama3-8b-8192[/bold]).")
            console.print("3. Switch to [bold]Ollama[/bold] for unlimited local runs.")
            console.print("!" * 80 + "\n", style="bold red")
        else:
            console.print(Panel(f"[bold red]Unexpected Error:[/bold red] {error_msg}", title="System Failure", border_style="bold red"))

@app.command()
def research(query: str):
    """Autonomous research on a topic."""
    run(f"Research and summarize: {query}")

@app.command()
def code(task: str):
    """Generate and execute code for a task."""
    run(task)

@app.command()
def analyze(dataset: str):
    """Analyze a dataset."""
    run(f"Analyze this dataset: {dataset}")

if __name__ == "__main__":
    app()
