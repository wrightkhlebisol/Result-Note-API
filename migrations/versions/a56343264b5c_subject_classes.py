"""subject classes

Revision ID: a56343264b5c
Revises: 091756585476
Create Date: 2024-02-17 06:16:53.257982

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a56343264b5c'
down_revision = '091756585476'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subject_classes',
    sa.Column('school_id', sa.Integer(), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], name=op.f('fk_subject_classes_class_id_classes')),
    sa.ForeignKeyConstraint(['school_id'], ['schools.id'], name=op.f('fk_subject_classes_school_id_schools')),
    sa.PrimaryKeyConstraint('school_id', 'class_id', name=op.f('pk_subject_classes'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subject_classes')
    # ### end Alembic commands ###
