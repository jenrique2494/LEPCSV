import re
import csv
from io import StringIO

path = 'EP990.csv'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find lines starting with #separator:comma
lines = text.splitlines()
sep_indices = [i for i,l in enumerate(lines) if l.strip().startswith('#separator:comma')]
if len(sep_indices) < 2:
    # nothing to do, print original
    print(text)
    raise SystemExit(0)

# find start line index of second header
start_idx = sep_indices[1]
# Reconstruct part1 and part2 text
part1_lines = lines[:start_idx]
part2_lines = lines[start_idx:]

# In part2, find first data line (non-comment and not empty)
data_start = 0
for i,l in enumerate(part2_lines):
    if not l.strip().startswith('#') and l.strip() != '':
        data_start = i
        break
header_lines = part2_lines[:data_start]
data_lines = part2_lines[data_start:]

# Parse CSV data_lines using csv.reader
reader = csv.reader(data_lines, delimiter=',', quotechar='"')
seen = set()
unique_rows = []
for row in reader:
    if len(row) < 2:
        # keep as-is
        unique_rows.append(row)
        continue
    key = row[1].strip()
    if key in seen:
        continue
    seen.add(key)
    unique_rows.append(row)

# Write cleaned data to string
out = StringIO()
writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
for r in unique_rows:
    writer.writerow(r)
clean_data = out.getvalue().splitlines()

# Combine back
new_lines = part1_lines + header_lines + clean_data
new_text = '\n'.join(new_lines) + '\n'
print(new_text)
