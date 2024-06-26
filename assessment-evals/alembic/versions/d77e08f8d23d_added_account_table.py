"""Added account table

Revision ID: d77e08f8d23d
Revises: 
Create Date: 2024-05-02 18:40:13.103431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'd77e08f8d23d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('answersheet',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=False),
    sa.Column('time_limit', sa.Interval(), nullable=False),
    sa.Column('time_start', sa.DateTime(), nullable=True),
    sa.Column('time_finish', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('to_attempt', 'in_progress', 'completed', name='quizattemptstatus'), nullable=True),
    sa.Column('total_points', sa.Integer(), nullable=False),
    sa.Column('attempt_score', sa.Float(), nullable=True),
    sa.Column('quiz_title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('quiz_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answersheet_id'), 'answersheet', ['id'], unique=False)
    op.create_index(op.f('ix_answersheet_quiz_id'), 'answersheet', ['quiz_id'], unique=False)
    op.create_index(op.f('ix_answersheet_student_id'), 'answersheet', ['student_id'], unique=False)
    op.create_table('answerslot',
    sa.Column('quiz_answer_sheet_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('question_type', sa.Enum('single_select_mcq', 'multiple_select_mcq', name='questiontypeenum'), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('points_awarded', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['quiz_answer_sheet_id'], ['answersheet.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answerslot_id'), 'answerslot', ['id'], unique=False)
    op.create_index(op.f('ix_answerslot_question_id'), 'answerslot', ['question_id'], unique=False)
    op.create_index(op.f('ix_answerslot_quiz_answer_sheet_id'), 'answerslot', ['quiz_answer_sheet_id'], unique=False)
    op.create_table('answerslotoption',
    sa.Column('quiz_answer_slot_id', sa.Integer(), nullable=False),
    sa.Column('option_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['quiz_answer_slot_id'], ['answerslot.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answerslotoption_id'), 'answerslotoption', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_answerslotoption_id'), table_name='answerslotoption')
    op.drop_table('answerslotoption')
    op.drop_index(op.f('ix_answerslot_quiz_answer_sheet_id'), table_name='answerslot')
    op.drop_index(op.f('ix_answerslot_question_id'), table_name='answerslot')
    op.drop_index(op.f('ix_answerslot_id'), table_name='answerslot')
    op.drop_table('answerslot')
    op.drop_index(op.f('ix_answersheet_student_id'), table_name='answersheet')
    op.drop_index(op.f('ix_answersheet_quiz_id'), table_name='answersheet')
    op.drop_index(op.f('ix_answersheet_id'), table_name='answersheet')
    op.drop_table('answersheet')
    # ### end Alembic commands ###
