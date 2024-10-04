"""Initial migration for schedule, bko, and lokasi tables

Revision ID: 20240606
Revises: None  # or the previous revision ID
Create Date: 2024-06-08 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '20240606'
down_revision = None  # Replace None with '<previous_revision_id>' if not the initial migration
branch_labels = None
depends_on = None

def upgrade():
    # Ensure 'lokasi' table exists
    op.create_table('lokasi',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nama_lokasi', sa.String(length=80), nullable=False)
    )

    # Ensure 'schedule' table exists
    op.create_table('schedule',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nama', sa.String(length=80), nullable=False),
        sa.Column('jabatan', sa.String(length=80), nullable=False),
        sa.Column('lokasi_id', sa.Integer(), sa.ForeignKey('lokasi.id'), nullable=False),
        sa.Column('tanggal', sa.Date(), nullable=False),
        sa.Column('shift', sa.String(length=20), nullable=False)
    )

    # Ensure 'bko' table exists
    op.create_table('bko',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tanggal', sa.Date(), nullable=False),
        sa.Column('lokasi_id', sa.Integer(), sa.ForeignKey('lokasi.id'), nullable=False),
        sa.Column('shift', sa.String(length=20), nullable=False),
        sa.Column('jumlah_personil', sa.Integer(), nullable=False),
        sa.Column('harga_satuan', sa.Numeric(10, 2), nullable=False),
        sa.Column('satuan', sa.String(length=20), nullable=False),
        sa.Column('event', sa.String(length=100), nullable=False),
        sa.Column('personil', sa.String(length=100), nullable=False)
    )

def downgrade():
    op.drop_table('bko')
    op.drop_table('schedule')
    op.drop_table('lokasi')
