$wc = New-Object System.Net.WebClient
$wc.Headers.Add('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
try {
    $html = $wc.DownloadString('https://www.smzdm.com/fenlei/ikf/')
    $len = [Math]::Min(5000, $html.Length)
    Write-Output $html.Substring(0, $len)
} catch {
    Write-Error $_.Exception.Message
}
