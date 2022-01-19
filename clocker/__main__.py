import click

from clocker.cli import show, start, stop, track


@click.group()
def cli():
    pass

cli.add_command(start)
cli.add_command(stop)
cli.add_command(track)
cli.add_command(show)

if __name__ == '__main__':
    cli()
