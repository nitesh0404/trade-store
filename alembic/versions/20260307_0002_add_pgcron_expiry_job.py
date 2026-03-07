from alembic import op


revision = "20260307_0002"
down_revision = "20260307_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS pg_cron")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION mark_expired_trades() RETURNS void AS $$
        BEGIN
            UPDATE trades
            SET expired = TRUE
            WHERE expired = FALSE
              AND maturity_date < CURRENT_DATE;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM cron.job WHERE jobname = 'trade_store_mark_expired_daily'
            ) THEN
                PERFORM cron.schedule(
                    'trade_store_mark_expired_daily',
                    '5 0 * * *',
                    $$SELECT mark_expired_trades();$$
                );
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(
        """
        DO $$
        DECLARE
            job_id integer;
        BEGIN
            SELECT jobid INTO job_id
            FROM cron.job
            WHERE jobname = 'trade_store_mark_expired_daily'
            LIMIT 1;

            IF job_id IS NOT NULL THEN
                PERFORM cron.unschedule(job_id);
            END IF;
        END
        $$;
        """
    )
    op.execute("DROP FUNCTION IF EXISTS mark_expired_trades()")
