"""Delete the memes table."""

from alembic import op
import sqlalchemy as sa


revision = 'bcb76d229183'
down_revision = '7da56a4eb387'


def upgrade():
    # NOTE: This will delete all existing data, but I don't really
    # care about keeping it. The old schema is bringing down the site.
    op.drop_table('words')
    op.create_table('words',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('meme_id', sa.String(), nullable=False),
        sa.Column('occurances', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.drop_table('memes')


def downgrade():
    # NOTE: This simply deletes all existing data and recreates the
    # schema from 7da56a4eb387
    op.drop_table('words')
    op.create_table('memes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('words',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('meme_id', sa.Integer(), nullable=False),
        sa.Column('occurances', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['meme_id'], ['memes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
