from alembic import op
import sqlalchemy as sa


revision = "20260307_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trades",
        sa.Column("trade_id", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("counterparty_id", sa.String(), nullable=False),
        sa.Column("book_id", sa.String(), nullable=False),
        sa.Column("maturity_date", sa.Date(), nullable=False),
        sa.Column("created_date", sa.Date(), nullable=False),
        sa.Column("expired", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("trade_id", "version"),
    )


def downgrade() -> None:
    op.drop_table("trades")
