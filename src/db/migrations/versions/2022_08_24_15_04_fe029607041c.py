"""Add Ayat.day.

Revision ID: fe029607041c
Revises: e51b916361eb
Create Date: 2022-08-24 15:04:26.227370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe029607041c'
down_revision = 'e51b916361eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ayats', sa.Column('day', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ayats', 'day')
    # ### end Alembic commands ###
