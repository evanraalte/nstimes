def red(text: str | int) -> str:
    return f"[bold red]{text}[/bold red]"


def cyan(text: str | int) -> str:
    return f"[bold cyan]{text}[/bold cyan]"


def green(text: str | int) -> str:
    return f"[bold green]{text}[/bold green]"


def strike(text: str | int) -> str:
    return f"[strike]{text}[/strike]"


def cancelled(text: str | int) -> str:
    return red(strike(text))
