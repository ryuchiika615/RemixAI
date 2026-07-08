$logFile = "C:\Users\ryuch\RemixAI\server.log"
$python = "C:\Users\ryuch\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$script = @"
import sys, os
sys.path.insert(0, 'C:\\Users\\ryuch\\RemixAI')
os.chdir('C:\\Users\\ryuch\\RemixAI')
from remixai.webui import main
main()
"@

$job = Start-Job -ScriptBlock {
    param($py, $code, $log)
    & $py -c $code *>&1 | Out-File -FilePath $log -Encoding utf8
} -ArgumentList $python, $script, $logFile

Write-Output "Job ID: $($job.Id)"
Write-Output "Waiting for server..."
Start-Sleep -Seconds 8

$log = Get-Content $logFile -ErrorAction SilentlyContinue
if ($log) {
    Write-Output "=== Server Log ==="
    $log
}
