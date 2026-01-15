# Script para eliminar tests duplicados
# Ejecutar desde: D:\Estadia_IACT\proyecto\IACT\api\callcentersite\tests\unit

$archivos = @(
    "test_core_etl_service.py",
    "test_core_models.py",
    "test_core_serializers.py",
    "test_ivr_models.py",
    "test_ivr_adapters.py"
)

Write-Host "ELIMINANDO TESTS DUPLICADOS" -ForegroundColor Yellow
Write-Host ""

foreach ($archivo in $archivos) {
    if (Test-Path $archivo) {
        Write-Host "Eliminando: $archivo" -ForegroundColor Red
        Remove-Item $archivo -Force
    } else {
        Write-Host "No encontrado: $archivo" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "VERIFICANDO ESTRUCTURA FINAL:" -ForegroundColor Green
Write-Host ""
Get-ChildItem -Recurse -Filter "test_*.py" | ForEach-Object {
    Write-Host "  $($_.FullName.Replace($PWD.Path, '.'))"
}

Write-Host ""
Write-Host "COMPLETADO. Ejecuta pytest para verificar 49 tests." -ForegroundColor Green
