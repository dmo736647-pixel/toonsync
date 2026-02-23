"""add payment methods table

Revision ID: 003
Revises: 002
Create Date: 2026-02-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建支付方式表"""
    op.create_table(
        'payment_methods',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('payment_type', sa.String(50), nullable=False),
        sa.Column('encrypted_card_number', sa.Text, nullable=True),
        sa.Column('encrypted_cvv', sa.Text, nullable=True),
        sa.Column('encrypted_account_number', sa.Text, nullable=True),
        sa.Column('encrypted_routing_number', sa.Text, nullable=True),
        sa.Column('card_brand', sa.String(50), nullable=True),
        sa.Column('last_four_digits', sa.String(4), nullable=True),
        sa.Column('expiry_month', sa.String(2), nullable=True),
        sa.Column('expiry_year', sa.String(4), nullable=True),
        sa.Column('billing_name', sa.String(255), nullable=True),
        sa.Column('billing_address', sa.Text, nullable=True),
        sa.Column('is_default', sa.String(10), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    
    # 创建索引
    op.create_index('ix_payment_methods_user_id', 'payment_methods', ['user_id'])


def downgrade() -> None:
    """删除支付方式表"""
    op.drop_index('ix_payment_methods_user_id', table_name='payment_methods')
    op.drop_table('payment_methods')
