$wc = New-Object System.Net.WebClient
$wc.Headers.Add('User-Agent', 'Mozilla/5.0')
try {
    $html = $wc.DownloadString('https://www.ikf.com.cn/')
    $len = [Math]::Min(5000, $html.Length)
    Write-Output $html.Substring(0, $len)
} catch {
    Write-Error $_.Exception.Message
}
