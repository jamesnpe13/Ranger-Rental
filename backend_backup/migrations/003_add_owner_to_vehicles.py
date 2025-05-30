"""Add owner_id to vehicles table

Revision ID: 003
Revises: 002
Create Date: 2025-05-19 09:48:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # Add owner_id column with a default value of 1 (or your admin user's ID)
    op.add_column('vehicles', 
        sa.Column('owner_id', sa.Integer(), nullable=False, server_default='1')
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_vehicles_owner_id',
        'vehicles', 'users',
        ['owner_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    # Drop the foreign key constraint first
    op.drop_constraint('fk_vehicles_owner_id', 'vehicles', type_='foreignkey')
    
    # Then drop the column
    op.drop_column('vehicles', 'owner_id')
