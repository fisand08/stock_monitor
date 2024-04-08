"""posts table

Revision ID: 2aeb80987778
Revises: 1e858be0ce28
Create Date: 2024-04-08 12:53:17.831452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2aeb80987778'
down_revision = '1e858be0ce28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('portfolio',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('portfolio', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_portfolio_timestamp'), ['timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_portfolio_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('portfolio', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_portfolio_user_id'))
        batch_op.drop_index(batch_op.f('ix_portfolio_timestamp'))

    op.drop_table('portfolio')
    # ### end Alembic commands ###
