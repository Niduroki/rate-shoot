"""Initial

Revision ID: 7e56e7541209
Revises: 
Create Date: 2021-06-22 14:05:56.024116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e56e7541209'
down_revision = None
branch_labels = None
depends_on = None


def downgrade():
    op.drop_table('passwords')
    op.drop_table('shoot')
    op.drop_table('pictures')


def upgrade():
    try:
        op.create_table('passwords',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('password', sa.VARCHAR(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        )
        
        op.create_table('shoot',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('link', sa.VARCHAR(), nullable=True),
        sa.Column('description', sa.VARCHAR(), nullable=True),
        sa.Column('creation', sa.DATETIME(), nullable=True),  # TODO datetime valid identifier?
        sa.Column('max_images', sa.INTEGER(), nullable=False),
        sa.Column('done', sa.BOOLEAN(), nullable=True),
        sa.Column('unedited_images', sa.BOOLEAN(), nullable=True),
        sa.Column('max_unedited', sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('done IN (0, 1)'),
        sa.CheckConstraint('unedited_images IN (0, 1)'),
        )
        
        op.create_table('pictures',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('shoot_id', sa.INTEGER(), nullable=True),
        sa.Column('filename', sa.VARCHAR(), nullable=True),
        sa.Column('star_rating', sa.INTEGER(), nullable=True),
        sa.Column('status', sa.VARCHAR(), nullable=True),
        sa.Column('comment', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['shoot_id'], ['shoot.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('filename'),
        )
    except sa.exc.OperationalError:
        pass  # Tables probably exist already - skip
