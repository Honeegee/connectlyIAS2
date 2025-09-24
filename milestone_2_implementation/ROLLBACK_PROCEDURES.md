# Rollback Procedures - Milestone 2 Implementation

## Quick Rollback Commands

### 1. Git Rollback to Baseline
```bash
# Rollback to pre-implementation baseline
git reset --hard f87c124

# Force push to remote (if needed)
git push origin master --force
```

### 2. Database Rollback
```bash
# Stop containers
docker-compose down

# Remove database volume
docker volume rm school-connectly_postgres_data

# Restart with clean database
docker-compose up -d db
python manage.py migrate
```

### 3. Full Environment Reset
```bash
# Stop all services
docker-compose down -v

# Remove all volumes (WARNING: This deletes all data)
docker volume prune -f

# Rebuild from baseline
git reset --hard f87c124
docker-compose up --build
```

### 4. Partial Rollback (File-Level)
```bash
# Restore specific file from baseline
git checkout f87c124 -- <file_path>

# Example: Restore settings.py
git checkout f87c124 -- connectly/settings.py
```

## Baseline Information
- **Commit Hash**: `f87c124`
- **Commit Message**: "Pre-Implementation Baseline - Milestone 2 Security Controls"
- **Remote Repository**: https://github.com/Honeegee/connectlyIAS2.git
- **Branch**: master

## Recovery Steps for Common Issues

### Issue: Implementation breaks authentication
```bash
git checkout f87c124 -- authentication/
python manage.py migrate
docker-compose restart web
```

### Issue: Database migration fails
```bash
# Rollback specific migration
python manage.py migrate <app_name> <previous_migration_number>

# Or full database reset (see Database Rollback above)
```

### Issue: Docker containers won't start
```bash
docker-compose down
docker system prune -f
git reset --hard f87c124
docker-compose up --build
```

## Verification After Rollback
1. Check git status: `git log --oneline -1`
2. Verify services: `docker-compose ps`
3. Test API: `curl http://localhost:8000/health/`
4. Run tests: `python manage.py test`