"""Add meme and words tables"""

from alembic import op
import sqlalchemy as sa

revision = '7da56a4eb387'
down_revision = None


def upgrade():
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


def downgrade():
    op.drop_table('words')
    op.drop_table('memes')
