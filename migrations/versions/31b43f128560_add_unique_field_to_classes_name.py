"""Add unique field to classes name

Revision ID: 31b43f128560
Revises: 4096b3894dad
Create Date: 2024-02-13 22:05:17.308760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31b43f128560'
down_revision = '4096b3894dad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('classes', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_classes_name'), ['name'])

    with op.batch_alter_table('subjects', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_subjects_name'), ['name'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subjects', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_subjects_name'), type_='unique')

    with op.batch_alter_table('classes', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_classes_name'), type_='unique')

    # ### end Alembic commands ###
