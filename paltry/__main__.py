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

        ast, = ast
        name = 'anonymous_{}'.format(num)
        with vm.module(name, show_ir=show_ir) as (module, builder):
            retval = codegen(ast, module, builder)
            builder.ret(retval)

        value = vm.run_init(name)
        print(value)


if __name__ == '__main__':
    main()
