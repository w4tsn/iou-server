"""initial database schema

Revision ID: 755def1ec563
Revises:
Create Date: 2022-03-14 19:44:54.132622

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "755def1ec563"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "group",
        sa.Column("group_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("group_id"),
    )
    op.create_index(op.f("ix_group_group_id"), "group", ["group_id"], unique=False)
    op.create_table(
        "user",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_name"), "user", ["name"], unique=False)
    op.create_index(op.f("ix_user_user_id"), "user", ["user_id"], unique=False)
    op.create_table(
        "group_membership",
        sa.Column("group_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["group.group_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.user_id"],
        ),
    )
    op.create_table(
        "transaction",
        sa.Column("transaction_id", sa.String(), nullable=False),
        sa.Column("group_id", sa.String(), nullable=True),
        sa.Column(
            "split_type",
            sa.Enum(
                "BY_SHARE",
                "BY_PERCENTAGE",
                "BY_ADJUSTMENT",
                "EQUAL",
                "UNEQUAL",
                name="splittype",
            ),
            nullable=True,
        ),
        sa.Column(
            "date",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["group.group_id"],
        ),
        sa.PrimaryKeyConstraint("transaction_id"),
    )
    op.create_index(
        op.f("ix_transaction_transaction_id"),
        "transaction",
        ["transaction_id"],
        unique=False,
    )
    op.create_table(
        "deposit",
        sa.Column("deposit_id", sa.String(), nullable=False),
        sa.Column("transaction_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transaction.transaction_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.user_id"],
        ),
        sa.PrimaryKeyConstraint("deposit_id"),
    )
    op.create_index(
        op.f("ix_deposit_deposit_id"), "deposit", ["deposit_id"], unique=False
    )
    op.create_table(
        "withdrawal",
        sa.Column("withdrawal_id", sa.String(), nullable=False),
        sa.Column("transaction_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transaction.transaction_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.user_id"],
        ),
        sa.PrimaryKeyConstraint("withdrawal_id"),
    )
    op.create_index(
        op.f("ix_withdrawal_withdrawal_id"),
        "withdrawal",
        ["withdrawal_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_withdrawal_withdrawal_id"), table_name="withdrawal")
    op.drop_table("withdrawal")
    op.drop_index(op.f("ix_deposit_deposit_id"), table_name="deposit")
    op.drop_table("deposit")
    op.drop_index(op.f("ix_transaction_transaction_id"), table_name="transaction")
    op.drop_table("transaction")
    op.drop_table("group_membership")
    op.drop_index(op.f("ix_user_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_name"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
    op.drop_index(op.f("ix_group_group_id"), table_name="group")
    op.drop_table("group")
    # ### end Alembic commands ###
