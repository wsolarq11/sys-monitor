# Quality System Setup Guide

## Overview
This guide explains how to set up the real quality assurance mechanism.

## Current Status
- Basic directory structure: ✅ Created
- quality-check.sh: ⚠️ Partially created (needs completion)

## Manual Setup Steps

### Task 1: Complete quality-check.sh
The file `.lingma/scripts/quality-check.sh` needs to be completed with full implementation.

### Task 2-5: See detailed documentation
Refer to the user request for complete specifications.

## Automated Setup (Recommended)
Due to Windows CMD limitations, please use one of these methods:

1. **Use Git Bash or WSL**: Run the setup in a Unix-like environment
2. **Use PowerShell**: PowerShell has better multi-line string support
3. **Copy from template**: Manually copy the script content

## Files to Create
1. `.lingma/scripts/quality-check.sh` - Quality check script
2. `.lingma/rules/quality-standards.md` - Quality standards rule
3. Update `.lingma/scripts/spec-worker.py` - Integrate quality checks
4. Update `.lingma/logs/decision-log.json` - Record quality check results

## Next Steps
Please refer to the detailed implementation guide for complete code.
