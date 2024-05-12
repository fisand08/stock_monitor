"""added transaction table

Revision ID: 02b5e2725438
Revises: 18e0214fa258
Create Date: 2024-05-11 13:11:52.334735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02b5e2725438'
down_revision = '18e0214fa258'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stock_abbreviation', sa.String(), nullable=False))
        batch_op.create_foreign_key(None, 'stock', ['stock_abbreviation'], ['abbreviation'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('stock_abbreviation')

    # ### end Alembic commands ###