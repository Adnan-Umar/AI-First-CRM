"""initial schema

Revision ID: 20260711_01
Revises:
Create Date: 2026-07-11 11:08:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260711_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("organization_type", sa.String(length=80), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_organizations_city"), "organizations", ["city"], unique=False)
    op.create_index(op.f("ix_organizations_name"), "organizations", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("territory", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    op.create_table(
        "healthcare_professionals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("specialty", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("preferred_channel", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_healthcare_professionals_email"), "healthcare_professionals", ["email"], unique=False
    )
    op.create_index(
        op.f("ix_healthcare_professionals_first_name"),
        "healthcare_professionals",
        ["first_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_healthcare_professionals_last_name"),
        "healthcare_professionals",
        ["last_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_healthcare_professionals_organization_id"),
        "healthcare_professionals",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_healthcare_professionals_specialty"),
        "healthcare_professionals",
        ["specialty"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_healthcare_professionals_specialty"), table_name="healthcare_professionals")
    op.drop_index(
        op.f("ix_healthcare_professionals_organization_id"), table_name="healthcare_professionals"
    )
    op.drop_index(op.f("ix_healthcare_professionals_last_name"), table_name="healthcare_professionals")
    op.drop_index(op.f("ix_healthcare_professionals_first_name"), table_name="healthcare_professionals")
    op.drop_index(op.f("ix_healthcare_professionals_email"), table_name="healthcare_professionals")
    op.drop_table("healthcare_professionals")

    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_organizations_name"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_city"), table_name="organizations")
    op.drop_table("organizations")

