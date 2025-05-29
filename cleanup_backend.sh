#!/bin/bash

# Navigate to the backend directory
cd "$(dirname "$0")/backend" || exit 1

# List of files to keep
KEEP=(
  "app.py"
  "config.py"
  "requirements.txt"
  "wsgi.py"
  "__init__.py"
  "models/"
  "routes/"
  "auth/"
  "migrations/"
  "instance/"
  "vehicles/"
  "utils/"
)

# Create a temporary directory to move files to be deleted
TEMP_DIR="../to_delete_$(date +%s)"
mkdir -p "$TEMP_DIR"

# Move non-essential files to the temp directory
find . -type f -not -path "./venv/*" -not -path "./instance/*" -not -path "./migrations/*" | while read -r file; do
  keep_file=0
  for keep in "${KEEP[@]}"; do
    if [[ "$file" == "./$keep" || "$file" == "./$keep"* ]]; then
      keep_file=1
      break
    fi
  done
  
  if [ $keep_file -eq 0 ]; then
    echo "Moving to delete: $file"
    mkdir -p "$TEMP_DIR/$(dirname "$file")"
    mv "$file" "$TEMP_DIR/$file" 2>/dev/null || true
  fi
done

# Remove empty directories (except the ones we want to keep)
find . -type d -not -path "." -not -path "./venv" -not -path "./instance" -not -path "./migrations" -empty -delete 2>/dev/null || true

echo "\nCleanup complete. Files to be deleted are in: $TEMP_DIR"
echo "Please review the contents of $TEMP_DIR and then run:"
echo "  rm -rf $TEMP_DIR"

echo "\nTo restore any deleted files, you can find them in the backup directory."
