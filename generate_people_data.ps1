$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$sourceRoot = 'D:\2026 연구정보부\2026 AI 디지털 활용 선도학교\인공지능과 함께 하는 역사야 놀자(동아리 활동)\교육부 국사편찬위원회_한국사데이터베이스 정보_친일파관련문헌 원문_20230518'
$outputPath = Join-Path $PSScriptRoot 'people_data.js'

$files = @(
  @{ Id = 'pj_001.xml'; Path = (Join-Path $sourceRoot 'pj_001.xml') },
  @{ Id = 'pj_002.xml'; Path = (Join-Path $sourceRoot 'pj_002.xml') },
  @{ Id = 'pj_003.xml'; Path = (Join-Path $sourceRoot 'pj_003.xml') },
  @{ Id = 'pj_004.xml'; Path = (Join-Path $sourceRoot 'pj_004.xml') }
)

function Normalize-Text {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) { return '' }
  return (($Text -replace '\s+', ' ').Trim())
}

function Normalize-Key {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) { return '' }
  return (($Text -replace '[\s''"“”‘’·,./()\[\]-]+', '').Trim())
}

function Add-Unique {
  param(
    [System.Collections.ArrayList]$List,
    [string]$Value,
    [int]$Limit = 9999
  )

  if ([string]::IsNullOrWhiteSpace($Value)) { return }
  if ($List.Count -ge $Limit) { return }
  if (-not $List.Contains($Value)) {
    [void]$List.Add($Value)
  }
}

function Infer-Category {
  param([string]$Context)

  if ($Context -match '경찰|경부|경시|헌병|보안과|고등경찰|특고') { return '경찰' }
  if ($Context -match '총독부|도지사|군수|참의|관료|행정|국장|학무') { return '행정' }
  if ($Context -match '백화점|회사|사장|실업|경제|상공|재계') { return '경제' }
  if ($Context -match '문인|문학|시인|역사가|기자|신문|잡지|편집') { return '문학·언론' }
  if ($Context -match '목사|교회|천도교|종교|불교') { return '종교·사회' }
  if ($Context -match '학병|학생|교수|학교|학도') { return '교육' }
  if ($Context -match '왕족|귀족|자작|백작|후작|종친') { return '귀족·정치' }
  if ($Context -match '암살|공판|특위|사건') { return '사건 관련' }
  return '기타'
}

function Infer-Role {
  param([string]$Category, [string]$Context)

  switch ($Category) {
    '경찰' { return '경찰·치안 인물' }
    '행정' { return '행정·관변 인물' }
    '경제' { return '경제·실업 인물' }
    '문학·언론' { return '문학·언론 인물' }
    '종교·사회' { return '종교·사회 인물' }
    '교육' { return '교육 관련 인물' }
    '귀족·정치' { return '귀족·정치 인물' }
    '사건 관련' { return '사건 연루 인물' }
    default {
      if ($Context -match '의사|독립') { return '독립운동 관련 인물' }
      return '원문 등장 인물'
    }
  }
}

$people = @{}
$fileSummaries = @()

foreach ($file in $files) {
  $xml = [xml](Get-Content $file.Path -Raw -Encoding UTF8)
  $allNamesInFile = [System.Collections.Generic.HashSet[string]]::new()

  foreach ($level2 in $xml.SelectNodes('//level2')) {
    $title = Normalize-Text ([string]$level2.front.biblioData.title.mainTitle)
    if (-not $title) { $title = $file.Id }

    foreach ($paragraph in $level2.SelectNodes('.//paragraph')) {
      $paragraphText = Normalize-Text ([string]$paragraph.InnerText)
      if (-not $paragraphText) { continue }

      foreach ($indexNode in $paragraph.SelectNodes('.//index[@type="이름"]')) {
        $name = Normalize-Text ([string]$indexNode.InnerText)
        if (-not $name) { continue }

        [void]$allNamesInFile.Add($name)

        if (-not $people.ContainsKey($name)) {
          $people[$name] = [ordered]@{
            id = $null
            name = $name
            hanja = ''
            alias = ''
            category = ''
            role = ''
            period = ''
            summary = ''
            actions = [System.Collections.ArrayList]::new()
            charges = ''
            sources = [System.Collections.ArrayList]::new()
            files = [System.Collections.ArrayList]::new()
            titles = [System.Collections.ArrayList]::new()
            occurrences = 0
            key = (Normalize-Key $name)
          }
        }

        $entry = $people[$name]
        $entry.occurrences++
        Add-Unique -List $entry.files -Value $file.Id
        Add-Unique -List $entry.titles -Value $title -Limit 8
        Add-Unique -List $entry.actions -Value $paragraphText -Limit 4
        Add-Unique -List $entry.sources -Value ("{0} - {1}" -f $file.Id, $title) -Limit 10
      }
    }
  }

  $fileSummaries += [ordered]@{
    file = $file.Id
    uniqueNames = $allNamesInFile.Count
  }
}

$autoPeople = New-Object System.Collections.Generic.List[object]
$counter = 1

foreach ($entry in ($people.Values | Sort-Object @{ Expression = 'occurrences'; Descending = $true }, @{ Expression = 'name'; Descending = $false })) {
  $context = (($entry.titles + $entry.actions) -join ' ')
  $category = Infer-Category $context
  $role = Infer-Role $category $context
  $entry.id = ('person-{0:d4}' -f $counter)
  $counter++
  $entry.category = $category
  $entry.role = $role
  $entry.period = ($entry.files -join ', ')
  $entry.alias = if ($entry.titles.Count -gt 0) { ($entry.titles | Select-Object -First 2) -join ' / ' } else { '원문 등장 인물' }
  $entry.charges = if ($entry.actions.Count -gt 0) { '원문 문맥상 친일·동원·공판 관련 서술 확인 필요' } else { '원문 추가 확인 필요' }

  $leadTitle = if ($entry.titles.Count -gt 0) { $entry.titles[0] } else { '원문' }
  $entry.summary = "{0}개 XML에서 {1}회 표기되며, 대표적으로 {2} 등에서 확인됩니다." -f $entry.files.Count, $entry.occurrences, $leadTitle

  $autoPeople.Add([ordered]@{
    id = $entry.id
    name = $entry.name
    hanja = $entry.hanja
    alias = $entry.alias
    category = $entry.category
    role = $entry.role
    period = $entry.period
    summary = $entry.summary
    actions = @($entry.actions)
    charges = $entry.charges
    sources = @($entry.sources)
    key = $entry.key
    occurrences = $entry.occurrences
  }) | Out-Null
}

$payload = [ordered]@{
  generatedAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  totalPeople = $autoPeople.Count
  files = $fileSummaries
  people = $autoPeople
}

$json = $payload | ConvertTo-Json -Depth 8 -Compress
$js = "window.AUTO_PEOPLE_PAYLOAD = $json;"
[System.IO.File]::WriteAllText($outputPath, $js, [System.Text.UTF8Encoding]::new($false))

Write-Output ("Generated {0} people -> {1}" -f $autoPeople.Count, $outputPath)
