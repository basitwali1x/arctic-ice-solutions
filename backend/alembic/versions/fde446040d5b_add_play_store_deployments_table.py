"""add_play_store_deployments_table

Revision ID: fde446040d5b
Revises: 1c2fef3a4a06
Create Date: 2025-11-02 05:48:56.543351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fde446040d5b'
down_revision: Union[str, Sequence[str], None] = '1c2fef3a4a06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('play_store_deployments',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('app_name', sa.String(length=100), nullable=False),
    sa.Column('app_bundle_path', sa.String(length=500), nullable=True),
    sa.Column('release_track', sa.String(length=40), nullable=False),
    sa.Column('version_code', sa.Integer(), nullable=False),
    sa.Column('version_name', sa.String(length=40), nullable=False),
    sa.Column('status', sa.String(length=40), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('deployment_logs', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_play_store_deployments_app_name'), 'play_store_deployments', ['app_name'], unique=False)
    op.create_index(op.f('ix_play_store_deployments_created_at'), 'play_store_deployments', ['created_at'], unique=False)
    op.create_index(op.f('ix_play_store_deployments_status'), 'play_store_deployments', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_play_store_deployments_status'), table_name='play_store_deployments')
    op.drop_index(op.f('ix_play_store_deployments_created_at'), table_name='play_store_deployments')
    op.drop_index(op.f('ix_play_store_deployments_app_name'), table_name='play_store_deployments')
    op.drop_table('play_store_deployments')
