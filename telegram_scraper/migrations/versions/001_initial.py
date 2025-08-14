"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create telegram_channels table
    op.create_table('telegram_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_scraped', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telegram_channels_id'), 'telegram_channels', ['id'], unique=False)
    op.create_index(op.f('ix_telegram_channels_name'), 'telegram_channels', ['name'], unique=False)
    op.create_index(op.f('ix_telegram_channels_username'), 'telegram_channels', ['username'], unique=True)
    op.create_index(op.f('ix_telegram_channels_category'), 'telegram_channels', ['category'], unique=False)
    op.create_index(op.f('ix_telegram_channels_language'), 'telegram_channels', ['language'], unique=False)

    # Create telegram_posts table
    op.create_table('telegram_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=True),
        sa.Column('image_url', sa.String(length=1000), nullable=True),
        sa.Column('image_path', sa.String(length=500), nullable=True),
        sa.Column('gcs_image_url', sa.String(length=1000), nullable=True),
        sa.Column('published_date', sa.DateTime(), nullable=True),
        sa.Column('scraped_date', sa.DateTime(), nullable=True),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('is_duplicate', sa.Boolean(), nullable=True),
        sa.Column('duplicate_of', sa.Integer(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('title_hash', sa.String(length=64), nullable=True),
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('forwards', sa.Integer(), nullable=True),
        sa.Column('replies', sa.Integer(), nullable=True),
        sa.Column('has_media', sa.Boolean(), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=True),
        sa.Column('moderation_status', sa.Enum('pending', 'ready', 'wrong', name='moderationstatus'), nullable=True),
        sa.Column('moderated_by', sa.String(length=100), nullable=True),
        sa.Column('moderated_at', sa.DateTime(), nullable=True),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telegram_posts_id'), 'telegram_posts', ['id'], unique=False)
    op.create_index(op.f('ix_telegram_posts_telegram_id'), 'telegram_posts', ['telegram_id'], unique=True)
    op.create_index(op.f('ix_telegram_posts_title'), 'telegram_posts', ['title'], unique=False)
    op.create_index(op.f('ix_telegram_posts_published_date'), 'telegram_posts', ['published_date'], unique=False)
    op.create_index(op.f('ix_telegram_posts_scraped_date'), 'telegram_posts', ['scraped_date'], unique=False)
    op.create_index(op.f('ix_telegram_posts_category'), 'telegram_posts', ['category'], unique=False)
    op.create_index(op.f('ix_telegram_posts_language'), 'telegram_posts', ['language'], unique=False)
    op.create_index(op.f('ix_telegram_posts_content_hash'), 'telegram_posts', ['content_hash'], unique=False)
    op.create_index(op.f('ix_telegram_posts_title_hash'), 'telegram_posts', ['title_hash'], unique=False)
    op.create_index(op.f('ix_telegram_posts_moderation_status'), 'telegram_posts', ['moderation_status'], unique=False)

    # Create scraping_logs table
    op.create_table('scraping_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('posts_found', sa.Integer(), nullable=True),
        sa.Column('posts_new', sa.Integer(), nullable=True),
        sa.Column('posts_duplicate', sa.Integer(), nullable=True),
        sa.Column('images_downloaded', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraping_logs_id'), 'scraping_logs', ['id'], unique=False)
    op.create_index(op.f('ix_scraping_logs_created_at'), 'scraping_logs', ['created_at'], unique=False)

    # Add foreign key constraints
    op.create_foreign_key(None, 'telegram_posts', 'telegram_channels', ['channel_id'], ['id'])
    op.create_foreign_key(None, 'telegram_posts', 'telegram_posts', ['duplicate_of'], ['id'])
    op.create_foreign_key(None, 'scraping_logs', 'telegram_channels', ['channel_id'], ['id'])

    # Create additional indexes
    op.create_index('idx_posts_published_date', 'telegram_posts', ['published_date'])
    op.create_index('idx_posts_category', 'telegram_posts', ['category'])
    op.create_index('idx_posts_language', 'telegram_posts', ['language'])
    op.create_index('idx_posts_content_hash', 'telegram_posts', ['content_hash'])
    op.create_index('idx_posts_title_hash', 'telegram_posts', ['title_hash'])
    op.create_index('idx_posts_telegram_id', 'telegram_posts', ['telegram_id'])
    op.create_index('idx_posts_moderation_status', 'telegram_posts', ['moderation_status'])
    op.create_index('idx_scraping_logs_channel_date', 'scraping_logs', ['channel_id', 'created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_scraping_logs_channel_date', table_name='scraping_logs')
    op.drop_index('idx_posts_moderation_status', table_name='telegram_posts')
    op.drop_index('idx_posts_telegram_id', table_name='telegram_posts')
    op.drop_index('idx_posts_title_hash', table_name='telegram_posts')
    op.drop_index('idx_posts_content_hash', table_name='telegram_posts')
    op.drop_index('idx_posts_language', table_name='telegram_posts')
    op.drop_index('idx_posts_category', table_name='telegram_posts')
    op.drop_index('idx_posts_published_date', table_name='telegram_posts')

    # Drop tables
    op.drop_table('scraping_logs')
    op.drop_table('telegram_posts')
    op.drop_table('telegram_channels')
