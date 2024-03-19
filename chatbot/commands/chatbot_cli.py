import click
from dcc.commands import evaluate, train


@click.group(help="CLI for project")
def main():
    pass


main.add_command(train.train)
main.add_command(evaluate.evaluate)

if __name__ == "__main__":
    main()