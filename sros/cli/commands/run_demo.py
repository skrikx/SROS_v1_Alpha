import typer
from ...kernel import kernel_bootstrap

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main():
    """
    Run the SROS demo.
    """
    print("Starting SROS Demo...")
    kernel = kernel_bootstrap.boot()
    
    # Keep alive for a bit
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
