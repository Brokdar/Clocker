import logging

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
    logging.basicConfig(filename='clocker.log',
                        level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s]: %(message)s',
                        encoding='utf-8')

    cli()
