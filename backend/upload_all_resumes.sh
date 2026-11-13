
#!/bin/bash

RESUME_DIR="/c/Users/DELL/OneDrive/Desktop/Crezy Dev/GrowthForImpact-Assignment_project/Software Development Assignment Resumes/Software Development Assignment Resumes"

API_URL="http://127.0.0.1:8000/api/resumes/upload/"

SUCCESS=0
DUPLICATES=0
FAILED=0
TOTAL=0

LOG_FILE="batch_upload_results.txt"

echo "Starting resume uploads..."
: > "$LOG_FILE"

while IFS= read -r -d '' file; do
    TOTAL=$((TOTAL + 1))
    filename=$(basename "$file")
    candidate_id="${filename%.*}"

    echo "[$TOTAL] $filename"

    response=$(curl -sS -w "\nHTTP_STATUS:%{http_code}" \
        -X POST "$API_URL" \
        -F "candidate_identifier=$candidate_id" \
        -F "file=@$file")

    http_code=$(echo "$response" | sed -n 's/.*HTTP_STATUS://p')
    body=$(echo "$response" | sed '/HTTP_STATUS:/d')

    echo "$filename | HTTP $http_code" >> "$LOG_FILE"

    case "$http_code" in
        201)
            SUCCESS=$((SUCCESS + 1))
            echo "  UPLOADED"
            ;;
        409)
            DUPLICATES=$((DUPLICATES + 1))
            echo "  DUPLICATE"
            ;;
        *)
            FAILED=$((FAILED + 1))
            echo "  FAILED: $body"
            ;;
    esac

done < <(find "$RESUME_DIR" -type f \( -iname "*.pdf" -o -iname "*.docx" \) -print0)

echo ""
echo "========== SUMMARY =========="
echo "Files detected: $TOTAL"
echo "New uploads: $SUCCESS"
echo "Duplicates: $DUPLICATES"
echo "Failed: $FAILED"
echo "Details: $LOG_FILE"
