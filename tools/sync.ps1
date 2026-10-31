$ErrorActionPreference = 'Stop'
$SyncScript = Join-Path $PSScriptRoot 'sync.py'

$Python3 = Get-Command python3 -ErrorAction SilentlyContinue
if ($null -ne $Python3) {
    & $Python3.Source $SyncScript @args
    exit $LASTEXITCODE
}

$PythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $PythonLauncher) {
    & $PythonLauncher.Source -3 $SyncScript @args
    exit $LASTEXITCODE
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if ($null -ne $Python) {
    & $Python.Source $SyncScript @args
    exit $LASTEXITCODE
}

Write-Error 'Python 3 is required to run the synchronizer.'
exit 127
