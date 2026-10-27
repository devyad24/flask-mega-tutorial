"""add post likes

Revision ID: 6144aeb0c45c
Revises: e7bb20598bfb
Create Date: 2026-10-27 06:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6144aeb0c45c'
down_revision = 'e7bb20598bfb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('post_likes',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'post_id')
    )
    with op.batch_alter_table('post_likes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_post_likes_post_id'), ['post_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_post_likes_user_id'), ['user_id'], unique=False)


def downgrade():
    with op.batch_alter_table('post_likes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_post_likes_user_id'))
        batch_op.drop_index(batch_op.f('ix_post_likes_post_id'))

    op.drop_table('post_likes')
