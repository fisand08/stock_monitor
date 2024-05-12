"""added transaction stock_abbrev to Transaction table

Revision ID: 18e0214fa258
Revises: 45564e7517a1
Create Date: 2024-05-11 13:08:25.487293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18e0214fa258'
down_revision = '45564e7517a1'
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