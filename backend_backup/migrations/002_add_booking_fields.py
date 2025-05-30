"""Add total_price and payment_intent_id to bookings

Revision ID: 002
Revises: 001
Create Date: 2025-05-19 09:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Add total_price column
    op.add_column('bookings', 
        sa.Column('total_price', sa.Float(), nullable=True)
    )
    
    # Add payment_intent_id column
    op.add_column('bookings',
        sa.Column('payment_intent_id', sa.String(length=100), nullable=True)
    )
    
    # Set default value for existing records
    op.execute("UPDATE bookings SET total_price = 0.0 WHERE total_price IS NULL")
    
    # Make total_price non-nullable
    op.alter_column('bookings', 'total_price', nullable=False)
    
    # Update status default to 'pending'
    op.execute("UPDATE bookings SET status = 'pending' WHERE status IS NULL")
    op.alter_column('bookings', 'status', 
                   server_default='pending', 
                   existing_type=sa.String(20),
                   nullable=False)

def downgrade():
    # Remove the columns we added
    op.drop_column('bookings', 'payment_intent_id')
    op.drop_column('bookings', 'total_price')
    
    # Revert status default
    op.alter_column('bookings', 'status',
                   server_default='confirmed',
                   existing_type=sa.String(20),
                   nullable=False)
