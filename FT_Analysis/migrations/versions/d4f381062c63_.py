"""empty message

Revision ID: d4f381062c63
Revises: 
Create Date: 2020-04-07 16:08:52.835126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4f381062c63'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('league',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('href', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_league_href'), 'league', ['href'], unique=False)
    op.create_index(op.f('ix_league_name'), 'league', ['name'], unique=False)
    op.create_table('player',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('position', sa.String(), nullable=True),
    sa.Column('age', sa.String(), nullable=True),
    sa.Column('nationality', sa.String(), nullable=True),
    sa.Column('img_href', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('club',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('leagueId', sa.String(), nullable=True),
    sa.Column('country_img_href', sa.String(), nullable=True),
    sa.Column('club_img_href', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['leagueId'], ['league.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_club_club_img_href'), 'club', ['club_img_href'], unique=False)
    op.create_index(op.f('ix_club_country_img_href'), 'club', ['country_img_href'], unique=False)
    op.create_index(op.f('ix_club_name'), 'club', ['name'], unique=False)
    op.create_table('transfer',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('playerId', sa.String(), nullable=True),
    sa.Column('fromId', sa.String(), nullable=True),
    sa.Column('toId', sa.String(), nullable=True),
    sa.Column('fromLeagueId', sa.String(), nullable=True),
    sa.Column('toLeagueId', sa.String(), nullable=True),
    sa.Column('fromCountry', sa.String(), nullable=True),
    sa.Column('toCountry', sa.String(), nullable=True),
    sa.Column('value', sa.String(), nullable=True),
    sa.Column('timestamp', sa.String(), nullable=True),
    sa.Column('season', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['fromId'], ['club.id'], ),
    sa.ForeignKeyConstraint(['fromLeagueId'], ['league.id'], ),
    sa.ForeignKeyConstraint(['playerId'], ['player.id'], ),
    sa.ForeignKeyConstraint(['toId'], ['club.id'], ),
    sa.ForeignKeyConstraint(['toLeagueId'], ['league.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transfer')
    op.drop_index(op.f('ix_club_name'), table_name='club')
    op.drop_index(op.f('ix_club_country_img_href'), table_name='club')
    op.drop_index(op.f('ix_club_club_img_href'), table_name='club')
    op.drop_table('club')
    op.drop_table('player')
    op.drop_index(op.f('ix_league_name'), table_name='league')
    op.drop_index(op.f('ix_league_href'), table_name='league')
    op.drop_table('league')
    # ### end Alembic commands ###