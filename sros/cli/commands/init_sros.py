import typer

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    """
    Initialize a new SROS environment.
    """
    print("Initializing SROS v1...")
    # Logic to create default config, data dirs, etc.
    print("Done.")
