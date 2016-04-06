"""Make meme template keys unique."""

from alembic import op
import sqlalchemy as sa


revision = 'a7a9acdc0670'
down_revision = '7da56a4eb387'


def upgrade():
    op.create_unique_constraint(None, 'memes', ['key'])


def downgrade():
    op.drop_constraint(None, 'memes', type_='unique')
