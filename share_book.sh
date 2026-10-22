#! /bin/bash
set -euo pipefail
URL=$1
BUCKET=$2
EXPIRATION=$3

FILENAME=$(basename "$URL")
curl -fL "${URL}" -o "books/${FILENAME}"


chmod +x share_book.sh
./share_book.sh https://www.gutenberg.org/ebooks/1184.txt.utf-8 secret-ufm3jx 604800