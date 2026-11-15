#!/bin/bash
set -e

# Creates the first admin user in a fresh SpaceDock deployment.
# By default, only runs when there are no users in the database.
#
# Usage: ./scripts/create-admin-user.sh [OPTIONS] [username] [email] [password]
#
# Options:
#   -f, --force          Allow creation even if users already exist
#   -h, --help           Show this help message
#
# Defaults: admin / admin@example.com / development

show_help() {
    cat << EOF
Creates the first admin user in a fresh SpaceDock deployment.
By default, only runs when there are no users in the database.

Usage: $(basename "$0") [OPTIONS] [username] [email] [password]

Options:
  -f, --force          Allow creation even if users already exist
  -h, --help           Show this help message

Defaults: admin / admin@example.com / development

Examples:
  $(basename "$0")
  $(basename "$0") admin admin@example.com secret
  $(basename "$0") --force second-admin second@example.com pass
EOF
}

FORCE=false
while [[ "$1" =~ ^- ]]; do
    case "$1" in
        -f|--force) FORCE=true; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

USERNAME="${1:-admin}"
EMAIL="${2:-admin@example.com}"
PASSWORD="${3:-development}"

echo "Creating admin user: ${USERNAME}"

if [ "$FORCE" = false ]; then
    USER_COUNT=$(docker compose exec db psql -U postgres -d spacedock -t -c "SELECT COUNT(*) FROM \"user\";" 2>/dev/null | tr -d ' ')
    if [ -n "$USER_COUNT" ] && [ "$USER_COUNT" -gt 0 ]; then
        echo "Database already has users ($USER_COUNT). Use --force to override."
        exit 1
    fi
fi

docker compose exec backend python3 -c "
from SpaceDock.objects import User
from SpaceDock.database import db

u = User.query.filter(User.username.ilike('${USERNAME}')).first()
if u:
    print('User ${USERNAME} already exists')
else:
    admin = User(username='${USERNAME}', email='${EMAIL}', admin=True, public=True)
    admin.set_password('${PASSWORD}')
    db.add(admin)
    db.commit()
    print('Admin user created: ${USERNAME} (${EMAIL})')
    print('Username: ${USERNAME}')
    print('Email: ${EMAIL}')
    print('Admin: True')
    print('Public: True')
"

echo "Done"
