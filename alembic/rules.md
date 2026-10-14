# SpaceDock Database Migration Rules

This file provides comprehensive guidelines for working with database migrations in SpaceDock.

## Migration Workflow

### Creating a Migration

1. **Identify the change**: Determine what needs to be modified in the database schema
2. **Create the migration**: Run the alembic command to generate a new migration file
3. **Edit the migration**: Implement the schema changes
4. **Test the migration**: Apply and verify the migration in a development environment
5. **Commit the migration**: Add the migration file to version control
6. **Deploy the migration**: Apply the migration to production

### Command Reference

```bash
# Create a new migration
alembic revision -m "message"

# Apply migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1

# List available migrations
alembic history

# Stamp the database (mark as up-to-date without running migrations)
alembic stamp head
```

## Migration Best Practices

### Schema Changes

1. **Add columns**: Use `op.add_column()` for new columns
2. **Modify columns**: Use `op.alter_column()` for column changes
3. **Drop columns**: Use `op.drop_column()` for removing columns
4. **Add tables**: Use `op.create_table()` for new tables
5. **Drop tables**: Use `op.drop_table()` for removing tables
6. **Add indexes**: Use `op.create_index()` for new indexes
7. **Drop indexes**: Use `op.drop_index()` for removing indexes

### Data Migrations

For complex data transformations:

```python
def upgrade():
    # Add new column
    op.add_column('mod', sa.Column('new_field', sa.String(), nullable=True))
    
    # Update data
    connection = op.get_bind()
    connection.execute(
        "UPDATE mod SET new_field = 'default' WHERE new_field IS NULL"
    )
    
    # Make column non-nullable
    op.alter_column('mod', 'new_field', nullable=False)
```

### Batch Operations

For large data migrations, use batch operations to avoid locking the database:

```python
def upgrade():
    batch_size = 1000
    connection = op.get_bind()
    
    # Get total count
    total = connection.execute("SELECT COUNT(*) FROM mod").scalar()
    
    # Process in batches
    for offset in range(0, total, batch_size):
        mods = connection.execute(
            "SELECT id FROM mod LIMIT :batch_size OFFSET :offset",
            {'batch_size': batch_size, 'offset': offset}
        ).fetchall()
        
        # Process each mod
        for mod in mods:
            # Your data transformation logic here
            pass
```

## Testing Migrations

### Local Testing

1. **Create a test database**: `createdb spacedock_test`
2. **Apply migrations**: `alembic -c alembic.ini upgrade head`
3. **Run tests**: `python -m pytest tests/integration/`
4. **Verify data**: Check that the migration produces expected results

### Migration Testing Strategies

1. **Backup your database**: Always backup before testing migrations
2. **Test on a copy**: Use a database copy that matches production
3. **Verify data integrity**: Check that data is preserved correctly
4. **Test performance**: Ensure migrations complete in acceptable time
5. **Test rollback**: Verify that downgrade works correctly

## Rollback Strategies

### Simple Rollback

```bash
# Downgrade by one revision
alembic downgrade -1

# Downgrade to a specific revision
alembic downgrade <revision_id>
```

### Handling Failed Migrations

1. **Identify the issue**: Check logs and error messages
2. **Downgrade**: Rollback to the previous state
3. **Fix the migration**: Correct the migration file
4. **Reapply**: Create a new migration if needed
5. **Test thoroughly**: Verify the fix works

## Migration Patterns

### Adding a New Table

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('new_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('new_table')
```

### Adding a Foreign Key

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('mod_version', sa.Column('mod_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_mod_version_mod', 'mod_version', 'mod', ['mod_id'], ['id'])
    
    # Update existing data
    connection = op.get_bind()
    connection.execute(
        "UPDATE mod_version SET mod_id = mod.id FROM mod WHERE mod_version.name = mod.name"
    )
    
    op.alter_column('mod_version', 'mod_id', nullable=False)

def downgrade():
    op.drop_constraint('fk_mod_version_mod', 'mod_version', type_='foreignkey')
    op.drop_column('mod_version', 'mod_id')
```

### Renaming a Column

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column('mod', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('mod', 'new_name', new_column_name='old_name')
```

## Performance Considerations

1. **Batch operations**: Process data in batches to avoid locking
2. **Indexes**: Temporarily disable indexes during large data operations
3. **Transactions**: Use transactions to ensure atomicity
4. **Connection pooling**: Reuse database connections
5. **Monitoring**: Monitor database performance during migrations

## Common Issues and Solutions

### Migration Already Applied

**Error**: `alembic.util.exc.AlembicCommandError: Target database is not up to date.`

**Solution**: Stamp the database to mark migrations as applied without running them:
```bash
alembic stamp head
```

### Missing Tables

**Error**: `sqlalchemy.exc.OperationalError: no such table: table_name`

**Solution**: Check the migration order and ensure dependencies are correct.

### Data Type Mismatches

**Error**: `sqlalchemy.exc.ProgrammingError: invalid input syntax for integer`

**Solution**: Ensure data types match between the migration and existing data.

### Constraint Violations

**Error**: `sqlalchemy.exc.IntegrityError: null value in column violates not-null constraint`

**Solution**: Provide default values or update existing data before making columns non-nullable.

## Best Practices Summary

1. **Small, focused migrations**: Each migration should make one logical change
2. **Clear migration messages**: Use descriptive messages for `alembic revision -m`
3. **Test thoroughly**: Always test migrations before deploying to production
4. **Document changes**: Add comments to explain complex migrations
5. **Backup databases**: Always backup before applying migrations to production
6. **Monitor performance**: Watch database performance during migrations
7. **Plan rollback**: Always have a rollback strategy

For questions about database migrations, refer to this file or consult the team.