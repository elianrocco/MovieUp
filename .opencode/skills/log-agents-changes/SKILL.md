---
name: log-agents-changes
description: Use when any agent modifies the AGENTS.md file. Must log every change to LogsMD.txt with line number, new code, and previous line.
---

# Log AGENTS.md Changes

When any modification is made to the AGENTS.md file, you MUST document the change in LogsMD.txt at the project root.

## Instructions

1. If LogsMD.txt does not exist, create it at the project root before writing
2. BEFORE logging any change, write a header in LogsMD.txt containing the modification number and the current date in DD/MM/YYYY format, centered with fixed spacing (10 leading spaces), using this format:

```
          /*/*/* M[numero de modificacion] FECHA */*/*/
```

   Where FECHA uses DD/MM/YYYY. Example: `          /*/*/* M1 23/09/2026 */*/*/`

3. Determine the modification number M[n] by scanning LogsMD.txt for existing headers matching the pattern `/*/*/* M(\d+)`, taking the highest number found and adding 1. If there are none, use M1
4. Write ONE header per modification batch, immediately before the entries of that batch
5. Detect every line modified in AGENTS.md
6. For each modified line, write an entry to LogsMD.txt in the format:

```
[line_number] [new_line_content] [previous_line_content]
```

7. Preserve the log format exactly: line number in brackets, new code in brackets, previous line in brackets, separated by spaces, ending with a semicolon

## Example

If AGENTS.md is modified for the first time (or the highest existing header is M1, so the next is M2), the header and the entry would be:

```
          /*/*/* M1 23/09/2026 */*/*/
[5] [- **Backend:** Python 3.11] [- **Backend:** Python];
```

## Rules

- ALWAYS run this logging after any edit to AGENTS.md
- ALWAYS write the header (with modification number and DD/MM/YYYY date) before the first entry of each modification batch
- Do NOT skip any modified lines
- Append new entries, do not overwrite existing logs
- Do NOT overwrite or rewrite existing headers when computing the modification number
- Use absolute path for LogsMD.txt in the project root
- Preserve the fixed centered spacing of the header: exactly 10 leading spaces
