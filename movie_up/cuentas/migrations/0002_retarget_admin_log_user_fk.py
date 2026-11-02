from django.db import migrations


def retarget_admin_log_user_fk(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != 'mysql':
        return

    quote = schema_editor.quote_name
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM django_admin_log')
        if cursor.fetchone()[0]:
            raise RuntimeError(
                'Cannot retarget django_admin_log.user_id while log entries exist.'
            )

        cursor.execute(
            """
            SELECT constraint_name
            FROM information_schema.key_column_usage
            WHERE constraint_schema = DATABASE()
              AND table_name = 'django_admin_log'
              AND column_name = 'user_id'
              AND referenced_table_name = 'cuenta'
            """
        )
        if cursor.fetchone():
            return

        cursor.execute(
            """
            SELECT constraint_name
            FROM information_schema.key_column_usage
            WHERE constraint_schema = DATABASE()
              AND table_name = 'django_admin_log'
              AND column_name = 'user_id'
              AND referenced_table_name = 'auth_user'
            """
        )
        old_fk = cursor.fetchone()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
              AND table_name = 'cuenta'
            """
        )
        if not cursor.fetchone()[0]:
            raise RuntimeError('The cuenta table must exist before retargeting admin logs.')

        operations = []
        if old_fk:
            operations.append(f'DROP FOREIGN KEY {quote(old_fk[0])}')
        operations.extend(
            [
                f'MODIFY COLUMN {quote("user_id")} BIGINT NOT NULL',
                (
                    f'ADD CONSTRAINT {quote("cuentas_django_admin_log_user_fk")} '
                    f'FOREIGN KEY ({quote("user_id")}) '
                    f'REFERENCES {quote("cuenta")} ({quote("id")})'
                ),
            ]
        )
        schema_editor.execute(
            f'ALTER TABLE {quote("django_admin_log")} ' + ', '.join(operations)
        )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('cuentas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(retarget_admin_log_user_fk),
    ]
