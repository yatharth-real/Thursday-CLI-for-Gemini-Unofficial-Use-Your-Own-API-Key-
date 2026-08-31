import argparse
import os
import sys
from dotenv import load_dotenv

import google.generativeai as genai
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live

# Initialize rich console
console = Console()

# Define tools for Gemini
def read_file(filepath: str) -> str:
    """Reads the content of a file or lists the contents of a directory.

    Args:
        filepath: The path to the file or directory.

    Returns:
        The content of the file, the listing of the directory, or an error message.
    """
    try:
        if os.path.isdir(filepath):
            files = os.listdir(filepath)
            return f"Directory listing for {filepath}:\n" + "\n".join(files)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {filepath}: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Writes content to a file.

    Args:
        filepath: The path to the file.
        content: The text content to write.

    Returns:
        A success or error message.
    """
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing to file {filepath}: {str(e)}"


def setup_gemini(api_key):
    genai.configure(api_key=api_key)
    # Provide tools to the model
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        tools=[read_file, write_file]
    )
    return model

def main():
    parser = argparse.ArgumentParser(
        description="Thursday: A vibrant, highly visual TUI and CLI built for Google Gemini models."
    )
    parser.add_argument(
        "--version", action="version", version="Thursday CLI 0.1.0"
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        console.print("[bold red]Error:[/bold red] GEMINI_API_KEY environment variable is not set or is still the placeholder.", style="red")
        console.print("Please set it in your .env file or environment.")
        sys.exit(1)

    model = setup_gemini(api_key)

    # Start chat session, setting enable_automatic_function_calling=True
    chat = model.start_chat(history=[], enable_automatic_function_calling=True)

    console.print(Panel.fit("[bold cyan]Welcome to Thursday CLI![/bold cyan]\nPowered by Google Gemini.", border_style="cyan"))
    console.print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
            if user_input.lower() in ['exit', 'quit']:
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            if not user_input.strip():
                continue

            # Note: when tools are called, streaming might yield chunks differently.
            # enable_automatic_function_calling=True with stream=True works but might interleave.
            response = chat.send_message(user_input, stream=True)

            console.print("\n[bold magenta]Thursday:[/bold magenta]")
            full_response = ""

            # Use Rich Live for real-time markdown streaming
            with Live(Markdown(full_response), console=console, refresh_per_second=10) as live:
                for chunk in response:
                    full_response += chunk.text
                    live.update(Markdown(full_response))

            console.print("-" * 40)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Exiting...[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")

if __name__ == "__main__":
    main()
