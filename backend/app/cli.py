import os

import click
from flask.cli import with_appcontext

from app.services.bootstrap import bootstrap_admin_from_env


@click.command("seed-admin")
@with_appcontext
def seed_admin_command():
    try:
        result = bootstrap_admin_from_env(os.environ)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    user = result["user"]
    action = "created" if result["created"] else "updated"
    password_note = " password_updated=true" if result["password_updated"] else ""
    click.echo(f"admin {action}: {user.username}{password_note}")


def register_cli(app):
    app.cli.add_command(seed_admin_command)
