import click
from itertools import count

from paltry import PaltryVM
from paltry.datatypes import PtObject
from paltry.codegen import codegen
from paltry.parser import PaltryParser, PaltrySemantics


@click.command()
@click.option('--show-ir/--no-show-ir', default=False)
def main(show_ir):
    vm = PaltryVM()
    parser = PaltryParser(
        parseinfo=True,
        semantics=PaltrySemantics()
    )

    for num in count():
        inp = input('> ')
        ast = parser.parse(inp, 'toplevel')

        value = vm.eval_code(ast, show_ir=show_ir)
        if value is None:
            print('Error!')
        else:
            print(value)


if __name__ == '__main__':
    main()
