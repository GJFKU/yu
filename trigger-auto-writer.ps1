# 开机自动打开 Edge（带远程调试端口）并触发 OpenClaw 品牌文章写作任务

# 1. 检查 Edge 是否已带调试端口运行
$portCheck = netstat -ano | Select-String ":9222"
if (-not $portCheck) {
    Write-Host "启动 Edge（远程调试端口 9222）..."
    Start-Process "msedge" -ArgumentList "--remote-debugging-port=9222 --no-first-run --new-window about:blank"
    Start-Sleep -Seconds 5
}

# 2. 等待 OpenClaw 网关就绪后触发 cron job
$jobId = "1d07ff57-5ec6-4f32-acee-8583ab500fb2"
$maxWait = 120
$waited = 0

Write-Host "等待 OpenClaw 网关就绪..."

while ($waited -lt $maxWait) {
    try {
        $result = openclaw cron run --job-id $jobId 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Edge 已就绪 + 品牌文章任务已触发!"
            exit 0
        }
    } catch {
        # 网关还没准备好
    }
    Start-Sleep -Seconds 5
    $waited += 5
}

Write-Host "❌ 超时"
