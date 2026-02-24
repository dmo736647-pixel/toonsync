"""Add PayPal fields to subscription

Revision ID: add_paypal_fields
Revises: 003
Create Date: 2026-02-22

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_paypal_fields'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('subscriptions', sa.Column('status', sa.String(20), nullable=False, server_default='active'))
    op.add_column('subscriptions', sa.Column('paypal_order_id', sa.String(255), nullable=True))
    op.add_column('subscriptions', sa.Column('paypal_transaction_id', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('subscriptions', 'paypal_transaction_id')
    op.drop_column('subscriptions', 'paypal_order_id')
    op.drop_column('subscriptions', 'status')
