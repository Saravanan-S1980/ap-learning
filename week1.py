import csv  # Import the built-in csv module so Python knows how to read CSV files

# Open the file "invoices.csv" for reading.
# 'r' means read-only. 'newline=""' prevents Python from adding extra blank lines on Windows.
with open("invoices.csv", "r", newline="") as file:

    # csv.DictReader reads each row as a dictionary, so you can access columns by name.
    # e.g., row["vendor"] instead of row[1]
    reader = csv.DictReader(file)

    # Read all rows into a list called 'invoices'.
    # Each item in the list is one row (a dictionary).
    invoices = list(reader)

# len() counts how many items are in the list — one item = one invoice row.
total_invoices = len(invoices)

# Start a running total at zero. We'll add each invoice's amount to this.
total_amount = 0.0

# Loop through every row in the invoices list.
for row in invoices:
    # row["amount"] gives us the amount value as a string, e.g. "1250.00"
    # float() converts that string into a decimal number so we can do math.
    total_amount += float(row["amount"])  # += means: add to total_amount and save the result

# Build a set of vendor names. A set automatically removes duplicates —
# if the same vendor appears 3 times, the set will only hold it once.
unique_vendors = set()

# Loop through every row again to collect vendor names.
for row in invoices:
    unique_vendors.add(row["vendor"])  # .add() puts the value into the set

# Sort the set alphabetically so the output is easy to read.
# sorted() returns a plain list in A-Z order.
sorted_vendors = sorted(unique_vendors)

# --- Print the results ---

print("=== Invoice Summary ===")  # Print a header label

# f-strings (f"...") let you embed variable values directly inside a string using {}.
print(f"Total invoices : {total_invoices}")

# :,.2f is a format code: comma-separated thousands, 2 decimal places.
print(f"Total amount   : INR {total_amount:,.2f}")

print(f"Unique vendors : {len(sorted_vendors)}")  # Count of distinct vendors

print("\nVendor list:")  # \n adds a blank line before the list

# Loop through each vendor name and print it with a bullet point.
for vendor in sorted_vendors:
    print(f"  - {vendor}")

# --- Group total amount by GL code ---

# A dictionary maps keys to values. We'll use gl_code as the key and running total as the value.
# Example after processing: {"6100": 2555.50, "5200": 14550.75, ...}
by_gl_code = {}

for row in invoices:
    gl = row["gl_code"]          # Get the GL code string for this row, e.g. "6100"
    amount = float(row["amount"])  # Convert amount from string to number

    # Check if we've seen this GL code before.
    # If not, create a new entry starting at 0 before adding to it.
    if gl not in by_gl_code:
        by_gl_code[gl] = 0.0

    by_gl_code[gl] += amount  # Add this invoice's amount to the running total for that GL code

print("\n=== Total Amount by GL Code ===")

# sorted() on a dictionary sorts by its keys (the GL codes), giving a consistent order.
for gl_code in sorted(by_gl_code):
    total = by_gl_code[gl_code]  # Look up the total for this GL code
    print(f"  GL {gl_code} : INR {total:,.2f}")


# ---------------------------------------------------------------
# SECTION 1 — Flag high-value invoices (amount above INR 75,000)
# ---------------------------------------------------------------

# This is an empty list that will collect every invoice that exceeds the threshold.
high_value = []

# A FOR LOOP repeats the same block of code once for every item in a collection.
# Plain English: "Go through each invoice, one at a time, and run the code below on it."
for row in invoices:

    # An IF STATEMENT runs its indented block ONLY when the condition is True.
    # Plain English: "If this invoice's amount is greater than 75000, do something about it."
    if float(row["amount"]) > 75000:

        # .append() adds the item to the end of the high_value list.
        high_value.append(row)

print("\n=== High-Value Invoices (above INR 75,000) ===")

# For loop again — this time we're printing each flagged invoice.
# Plain English: "For every invoice we collected in high_value, print its details."
for row in high_value:
    print(f"  {row['invoice_id']} | {row['vendor']:<25} | INR {float(row['amount']):>12,.2f} | {row['status']}")

# --- Write high-value invoices to a new CSV file ---

# The column names for the output file — must match the keys in each row dictionary.
output_columns = ["invoice_id", "vendor", "amount", "currency", "gl_code", "invoice_date", "status"]

# Open a new file for writing ('w'). If the file already exists, it will be overwritten.
# newline="" prevents Python from inserting extra blank lines between rows on Windows.
with open("high_value_invoices.csv", "w", newline="") as out_file:

    # csv.DictWriter is the write counterpart to DictReader.
    # fieldnames tells it which columns to write and in what order.
    writer = csv.DictWriter(out_file, fieldnames=output_columns)

    # writeheader() writes the column name row at the top of the file (invoice_id,vendor,...).
    writer.writeheader()

    # writerows() loops through the list and writes one CSV row per dictionary.
    # Plain English: "For every flagged invoice, write it as a line in the new file."
    writer.writerows(high_value)

# len() tells us how many rows were written — useful as a quick confirmation.
print(f"\n  => Written {len(high_value)} rows to high_value_invoices.csv")


# ---------------------------------------------------------------
# SECTION 2 — Unapproved vendor check
# ---------------------------------------------------------------

# This is the whitelist of vendors your company has pre-approved.
# Using a list here because the order matters for human reading; a set would also work.
approved_vendors = ["Siemens India", "Tata Consultancy", "Infosys BPO"]

# An empty list to hold invoices from vendors NOT on the approved list.
unapproved = []

# FOR LOOP: visit every invoice one by one.
# Plain English: "Look at each invoice and check who sent it."
for row in invoices:

    # IF STATEMENT with 'not in': the condition is True when the vendor is ABSENT from the list.
    # Plain English: "If this vendor's name is not found in our approved list, flag the invoice."
    if row["vendor"] not in approved_vendors:
        unapproved.append(row)

print("\n=== Invoices from Unapproved Vendors ===")

# sorted() reorders the list before we loop through it.
# key=lambda row: float(row["amount"]) tells sorted() what value to sort by —
# here it extracts the amount from each row as a number.
# reverse=True means highest amount comes first (descending order).
for row in sorted(unapproved, key=lambda row: float(row["amount"]), reverse=True):
    print(f"  {row['invoice_id']} | {row['vendor']:<25} | INR {float(row['amount']):>12,.2f}")


# ---------------------------------------------------------------
# SECTION 3 — Count invoices by status
# ---------------------------------------------------------------

# A dictionary to hold the count for each status value.
# We'll add keys dynamically as we discover new statuses.
status_counts = {}

# FOR LOOP: go through every invoice to read its status field.
# Plain English: "For each invoice, find its status and add 1 to that status's counter."
for row in invoices:
    status = row["status"]  # e.g. "pending", "approved", "on-hold"

    # IF the status key doesn't exist in our dictionary yet, create it starting at 0.
    if status not in status_counts:
        status_counts[status] = 0

    status_counts[status] += 1  # Increment the counter by 1 for this status

print("\n=== Invoice Count by Status ===")

# FOR LOOP: print each status and its count.
# sorted() keeps the output in a predictable alphabetical order.
for status in sorted(status_counts):
    count = status_counts[status]
    print(f"  {status:<10} : {count} invoice(s)")

# ---------------------------------------------------------------
# SECTION 4 — On-hold invoices
# ---------------------------------------------------------------

# A list comprehension is a compact way to build a list using a filter.
# Plain English: "Give me every row where the status column equals 'on-hold'."
# This is equivalent to writing a for loop + if + append, all in one line.
on_hold = [row for row in invoices if row["status"] == "on-hold"]

print("\n=== On-Hold Invoices ===")

for row in on_hold:
    print(f"  {row['invoice_id']} | {row['vendor']:<25} | INR {float(row['amount']):>12,.2f} | {row['invoice_date']}")
