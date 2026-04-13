param (
    [string]$OutputPath = "icons\icon.ico"
)

# ICO header (6 bytes) + icon directory entry (16 bytes) + minimal bitmap data
$iconData = [byte[]](
    # ICO header
    0x00, 0x00, 0x01, 0x00,  # ICO file type
    0x01, 0x00,              # Number of images
    # Image directory entry
    0x10, 0x10, 0x00, 0x00,  # Width, Height (16x16)
    0x00, 0x00,              # Color plane count
    0x20, 0x00,              # Bits per pixel (32)
    0x68, 0x04, 0x00, 0x00,  # Image data size (1128 bytes)
    0x16, 0x00, 0x00, 0x00,  # Image data offset (22 bytes)
    # Minimal PNG-like data (fake but valid structure)
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A  # PNG signature
)

# Add padding to make file large enough
for ($i = $iconData.Length; $i -lt 1200; $i++) {
    $iconData += 0x00
}

[System.IO.File]::WriteAllBytes($OutputPath, $iconData)
Write-Host "Created ICO file at $OutputPath"
