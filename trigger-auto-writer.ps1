# 开机后自动触发品牌文章写作任务
# 等待 OpenClaw 网关就绪后触发 cron job

$jobId = "1d07ff57-5ec6-4f32-acee-8583ab500fb2"
$maxWait = 120  # 最多等2分钟
$waited = 0

Write-Host "等待 OpenClaw 网关就绪..."

while ($waited -lt $maxWait) {
    try {
        $result = openclaw cron run --job-id $jobId 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 品牌文章任务已触发!"
            exit 0
        }
    } catch {
        # 网关还没准备好
    }
    Start-Sleep -Seconds 5
    $waited += 5
}

Write-Host "❌ 超时：OpenClaw 网关未就绪，任务未触发"
exit 1
