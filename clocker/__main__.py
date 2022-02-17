"""Clocker main"""

import logging

import click

from clocker.cli import (error, holidays, notify, remove, report, show, start, stop, track)


@click.group()
@click.option('-d', '--debug', default=False, is_flag=True, help='Sets logging level to debug')
def cli(debug: bool):
    """Command Line Interface. Group of available commands.

    Args:
        debug (bool): set logging level to debug
    """

    if debug:
        logging.basicConfig(filename='clocker.log',
                            level=logging.DEBUG,
                            format='%(asctime)s [%(levelname)s]: %(message)s',
                            encoding='utf-8')
    else:
        logging.basicConfig(filename='clocker.log',
                            level=logging.INFO,
                            format='%(asctime)s [%(levelname)s]: %(message)s',
                            encoding='utf-8')


cli.add_command(start)
cli.add_command(stop)
cli.add_command(track)
cli.add_command(remove)
cli.add_command(show)
cli.add_command(report)
cli.add_command(notify)
cli.add_command(holidays)

if __name__ == '__main__':
    try:
        cli()  #pylint: disable = no-value-for-parameter
    except Exception as err:  # pylint: disable = broad-except
        error(err)
