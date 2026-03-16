param(
  [switch]$Down
)

if ($Down) {
  docker compose down
  exit 0
}

docker compose up --build
