"""Add choose one

Revision ID: bad8060b717e
Revises: 08d414780bc2
Create Date: 2021-07-05 15:26:34.163437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bad8060b717e'
down_revision = '08d414780bc2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('shoot', sa.Column('choose_one', sa.Boolean(), nullable=True))


def downgrade():
    pass  # NOOP
