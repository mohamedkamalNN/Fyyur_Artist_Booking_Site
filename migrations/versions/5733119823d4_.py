"""empty message

Revision ID: 5733119823d4
Revises: 59ef84902e2f
Create Date: 2021-02-22 17:03:18.105701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5733119823d4'
down_revision = '59ef84902e2f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'seeking_shows',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'seeking_shows',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###