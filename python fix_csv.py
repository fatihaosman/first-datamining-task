import csv

input_file = 'superrstore.csv'      # your original file
output_file = 'superstore_fixed.csv'  # cleaned file for Weka

with open(input_file, newline='', encoding='cp1252') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:


    reader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

    for row in reader:
        fixed_row = []
        for cell in row:
            # Wrap in quotes if the cell contains comma or apostrophe
            if ',' in cell or "'" in cell:
                fixed_row.append(f'"{cell}"')
            else:
                fixed_row.append(cell)
        writer.writerow(fixed_row)

print(f"Done! Cleaned file saved as {output_file}")
