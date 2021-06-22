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
    op.drop_table('Links')
    op.drop_table('sites')
    op.drop_table('config')
    op.drop_table('users')


def upgrade():
    try:
        op.create_table('users',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('username', sa.VARCHAR(), nullable=True),
        sa.Column('password', sa.VARCHAR(), nullable=True),
        sa.Column('admin', sa.BOOLEAN(), nullable=True),
        sa.CheckConstraint('admin IN (0, 1)'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
        )
        op.create_table('config',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('key', sa.VARCHAR(), nullable=True),
        sa.Column('value', sa.VARCHAR(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
        )
        op.create_table('sites',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('owner_id', sa.INTEGER(), nullable=True),
        sa.Column('name', sa.VARCHAR(), nullable=True),
        sa.Column('seo_description', sa.VARCHAR(), nullable=True),
        sa.Column('seo_author', sa.VARCHAR(), nullable=True),
        sa.Column('image', sa.VARCHAR(), nullable=True),
        sa.Column('bio', sa.VARCHAR(), nullable=True),
        sa.Column('footer', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('image'),
        sa.UniqueConstraint('name')
        )
        op.create_table('Links',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('site_id', sa.INTEGER(), nullable=True),
        sa.Column('icon', sa.VARCHAR(), nullable=True),
        sa.Column('link', sa.VARCHAR(), nullable=True),
        sa.Column('text', sa.VARCHAR(), nullable=True),
        sa.Column('order', sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    except sa.exc.OperationalError:
        pass  # Tables probably exist already - skip
