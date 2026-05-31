"""Create initial database schema."""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """Create initial tables."""
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(255)),
        sa.Column('last_name', sa.String(255)),
        sa.Column('avatar_url', sa.String(512)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('telegram_user_id', sa.String(255), unique=True),
        sa.Column('whatsapp_phone', sa.String(50), unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True)),
    )
    
    # Create indexes
    op.create_index('idx_email', 'users', ['email'])
    op.create_index('idx_telegram_user_id', 'users', ['telegram_user_id'])
    op.create_index('idx_whatsapp_phone', 'users', ['whatsapp_phone'])


def downgrade() -> None:
    """Drop initial tables."""
    op.drop_table('users')
