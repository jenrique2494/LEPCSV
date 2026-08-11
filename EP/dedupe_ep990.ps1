$path = 'EP990.csv'
$text = Get-Content -Raw -Encoding UTF8 $path
$lines = $text -split "`n"
$sep_indices = @()
for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i].TrimStart().StartsWith('#separator:comma')) { $sep_indices += $i }
}
if ($sep_indices.Count -lt 2) {
    Write-Output $text
    exit 0
}
$start_idx = $sep_indices[1]
$part1 = $lines[0..($start_idx-1)]
$part2 = $lines[$start_idx..($lines.Count-1)]
# find first non-comment non-empty line in part2
$data_start = 0
for ($i=0; $i -lt $part2.Count; $i++) {
    if (-not ($part2[$i].TrimStart().StartsWith('#')) -and ($part2[$i].Trim() -ne '')) { $data_start = $i; break }
}
$header_lines = $part2[0..($data_start-1)]
$data_lines = $part2[$data_start..($part2.Count-1)]

$seen = @{}
$out_data = @()
$regex = '^[^,]*,(?:"([^"]*)"|([^,]*))'
foreach ($line in $data_lines) {
    if ($line.Trim() -eq '') { continue }
    $m = [regex]::Match($line, $regex)
    if ($m.Success) {
        $key = $m.Groups[1].Value
        if (-not $key) { $key = $m.Groups[2].Value }
        $key = $key.Trim()
        if (-not $seen.ContainsKey($key)) {
            $seen[$key] = $true
            $out_data += $line
        }
    } else {
        $out_data += $line
    }
}

$new_lines = @()
$new_lines += $part1
$new_lines += $header_lines
$new_lines += $out_data
$new_text = ($new_lines -join "`n") + "`n"
Write-Output $new_text
