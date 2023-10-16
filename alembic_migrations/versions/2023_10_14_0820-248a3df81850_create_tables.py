"""create tables

Revision ID: 248a3df81850
Revises: 
Create Date: 2023-10-14 08:20:03.224513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '248a3df81850'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


STATUS_ENUM_POSTGRES = postgresql.ENUM('started', 'ended', 'in_process', 'awaiting', 'canceled', name='status')
STATUS_ENUM = sa.Enum('started', 'ended', 'in_process', 'awaiting', 'canceled', name='status')
STATUS_ENUM.with_variant(STATUS_ENUM_POSTGRES, 'postgresql')


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('outlet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('worker',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('phone_number', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('phone_number', sa.String(length=255), nullable=False),
    sa.Column('outlet_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['outlet_id'], ['outlet.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('worker_outlet',
    sa.Column('outlet', sa.Integer(), nullable=False),
    sa.Column('worker', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['outlet'], ['outlet.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['worker'], ['worker.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('outlet', 'worker')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('ended_date', sa.DateTime(), server_default=sa.text("(TIMEZONE('utc', now()) + INTERVAL '1 week')"), nullable=False),
    sa.Column('outlet_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('started', 'ended', 'in_process', 'awaiting', 'canceled', name='status'), nullable=False),
    sa.Column('worker_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['outlet_id'], ['outlet.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['worker_id'], ['worker.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('visit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('worker_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('outlet_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['outlet_id'], ['outlet.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['worker_id'], ['worker.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('visit')
    op.drop_table('order')
    op.drop_table('worker_outlet')
    op.drop_table('customer')
    op.drop_table('worker')
    op.drop_table('outlet')
    STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###