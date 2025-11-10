import csv
import io

input_file = r'C:\Users\HP 1030 G4\Desktop\superstore sales\superrstore.csv'
output_file = r'C:\Users\HP 1030 G4\Desktop\superstore sales\superstore_fixed.csv'
bad_rows_file = r'C:\Users\HP 1030 G4\Desktop\superstore sales\bad_rows.txt'

expected_cols = 21

def parse_buffer(buf):
    """
    Parse a buffer string (one CSV logical record) into a row list using csv.reader.
    Returns the row list or raises csv.Error.
    """
    # csv.reader expects an iterable of lines, so wrap in list
    reader = csv.reader([buf], quotechar='"', doublequote=True)
    return next(reader)

with open(input_file, 'r', encoding='cp1252', errors='replace', newline='') as infile, \
     open(output_file, 'w', encoding='utf-8', newline='') as outfile, \
     open(bad_rows_file, 'w', encoding='utf-8') as badf:

    writer = csv.writer(outfile, quoting=csv.QUOTE_ALL, doublequote=True)

    buffer = ''
    line_no = 0
    logical_record_no = 0

    for physical_line in infile:
        line_no += 1
        # Keep the physical lines (including their newline) in buffer
        if buffer:
            buffer += physical_line
        else:
            buffer = physical_line

        # Count double-quote characters. If count is even -> likely complete record.
        # (This is a common heuristic — it handles fields with embedded newlines.)
        if buffer.count('"') % 2 != 0:
            # Not balanced yet; read next physical line to complete the logical record
            continue

        # Now attempt to parse the accumulated logical record
        logical_record_no += 1
        try:
            row = parse_buffer(buffer)
        except csv.Error as e:
            badf.write(f"PARSE_ERROR logical_record={logical_record_no} started_at_line={line_no - buffer.count('\\n')}\n")
            badf.write(f"error: {e}\nbuffer:\n{buffer}\n{'-'*80}\n")
            # Reset buffer and continue (skip writing this malformed record)
            buffer = ''
            continue

        # Clean cells: remove internal newlines, strip spaces
        row = [cell.replace('\n', ' ').replace('\r', ' ').strip() for cell in row]

        # If row has too few columns, pad with empty strings
        if len(row) < expected_cols:
            row += [''] * (expected_cols - len(row))

        # If row has too many columns, log it to bad file for manual inspection
        if len(row) != expected_cols:
            badf.write(f"MISMATCH logical_record={logical_record_no} parsed_cols={len(row)} expected={expected_cols}\n")
            badf.write(f"parsed_row: {row}\n{'-'*80}\n")
            # You may still write a padded/truncated row if you prefer, but here we skip writing malformed rows:
            # Option A (safe): skip writing malformed rows (comment out next two lines to skip)
            # Option B (practical): truncate to expected_cols or merge last fields; I will write padded/truncated:
            row = row[:expected_cols]  # truncate extras if any (less ideal)
            # row += [''] * (expected_cols - len(row))  # already handled above for fewer columns

        # Write the cleaned row
        writer.writerow(row)

        # Reset buffer for next logical record
        buffer = ''

    # If file ended but buffer still has content, try one last parse
    if buffer.strip():
        logical_record_no += 1
        try:
            row = parse_buffer(buffer)
            row = [cell.replace('\n', ' ').replace('\r',' ').strip() for cell in row]
            if len(row) < expected_cols:
                row += [''] * (expected_cols - len(row))
            if len(row) != expected_cols:
                badf.write(f"MISMATCH_AT_EOF logical_record={logical_record_no} parsed_cols={len(row)} expected={expected_cols}\n")
                badf.write(f"parsed_row: {row}\n{'-'*80}\n")
            writer.writerow(row[:expected_cols])
        except csv.Error as e:
            badf.write(f"PARSE_ERROR_AT_EOF logical_record={logical_record_no} error: {e}\nbuffer:\n{buffer}\n")

print("Done. Clean file:", output_file)
print("Bad rows (if any) logged to:", bad_rows_file)
