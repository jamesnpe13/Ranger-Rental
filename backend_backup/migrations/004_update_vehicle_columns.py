"""Update Vehicle model columns

Revision ID: 004
Revises: 003
Create Date: 2025-05-19 09:52:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # This is a no-op since we're just making the model match the existing schema
    pass

def downgrade():
    # No need to do anything on downgrade either
    pass
