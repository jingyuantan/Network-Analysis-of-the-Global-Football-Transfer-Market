"""empty message

Revision ID: d2ad3491894c
Revises: 7f1bf6fa5caa
Create Date: 2020-01-24 11:43:40.935573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2ad3491894c'
down_revision = '7f1bf6fa5caa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('league', sa.Column('country', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('league', 'country')
    # ### end Alembic commands ###