# Create ICO file with PNG-compressed icon data
$iconPath = "icons\icon.ico"

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.IO

# Create bitmap
$bitmap = New-Object System.Drawing.Bitmap(32, 32)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::FromArgb(255, 0, 120, 215))

# Get HICON handle
$hIcon = $bitmap.GetHicon()

# Create Icon object from handle
$icon = [System.Drawing.Icon]::FromHandle($hIcon)

# Save to memory stream in ICO format
$memoryStream = New-Object System.IO.MemoryStream
$icon.Save($memoryStream)
$icoBytes = $memoryStream.ToArray()

# Write to file
[System.IO.File]::WriteAllBytes($iconPath, $icoBytes)

# Cleanup
$graphics.Dispose()
$bitmap.Dispose()
$icon.Dispose()
$memoryStream.Dispose()

Write-Host "ICO file created at $iconPath ($($icoBytes.Length) bytes)"
