from click import command, echo


@command()
def module_b_command() -> None:
    echo("Command in module_b")
