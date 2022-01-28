import logging

import click

from clocker.cli import remove, show, start, stop, track


@click.group()
@click.option('-d', '--debug', default=False, is_flag=True, help='Sets logging level to debug')
def cli(debug: bool):
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

if __name__ == '__main__':
    #pylint: disable = no-value-for-parameter
    cli()
