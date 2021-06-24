"""Unedited images plus Stars

Revision ID: 08d414780bc2
Revises: 7e56e7541209
Create Date: 2021-06-22 14:14:56.225111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08d414780bc2'
down_revision = '7e56e7541209'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pictures', sa.Column('star_rating', sa.Integer(), nullable=True))
    op.add_column('shoot', sa.Column('unedited_images', sa.Boolean(), nullable=True))
    op.add_column('shoot', sa.Column('max_unedited', sa.Integer(), nullable=True))

def downgrade():
    pass  # NOOP
