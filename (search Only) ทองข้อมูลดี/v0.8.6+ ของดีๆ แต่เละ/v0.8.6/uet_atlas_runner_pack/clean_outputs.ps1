Write-Host "== Cleaning old outputs ==" -ForegroundColor Yellow
Remove-Item -Recurse -Force .\runs\atlas_* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\reports\atlas_* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\**\__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\.pytest_cache -ErrorAction SilentlyContinue
Write-Host "Done." -ForegroundColor Green
