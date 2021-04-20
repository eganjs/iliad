from click import command, echo


@command()
def module_a_command() -> None:
    echo("Command in module_a")
