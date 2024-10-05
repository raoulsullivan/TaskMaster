"""Add Task Frequencies

Revision ID: 4766206eff54
Revises: 9fa77f2dac91
Create Date: 2024-09-30 19:26:29.959394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4766206eff54'
down_revision: Union[str, None] = '9fa77f2dac91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('frequencies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('DAILY', 'WEEKLY', name='taskfrequencyenum'), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id')
    )
    op.create_table('daily_frequencies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['frequencies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('weekly_frequencies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('day_of_week', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['frequencies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute("""
        INSERT INTO 'frequencies' (type, task_id)
        SELECT 'DAILY', id FROM tasks
    """)
    op.execute("""
        INSERT INTO 'daily_frequencies' (id)
        SELECT id FROM frequencies
    """)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('weekly_frequencies')
    op.drop_table('daily_frequencies')
    op.drop_table('frequencies')
    # ### end Alembic commands ###
