import pandas as pd  # pandas is the standard Python library for working with tabular data.
                     # 'as pd' gives it a short alias so we type pd.something instead of pandas.something.


# ---------------------------------------------------------------
# WHAT IS A DATAFRAME?
# A DataFrame is pandas' version of a spreadsheet table.
# It has rows (one per invoice) and named columns (invoice_id, vendor, amount, ...).
# Unlike a plain Python list, a DataFrame lets you filter, group, sort, and calculate
# across thousands of rows with a single line of code.
# ---------------------------------------------------------------


def load_invoices(filepath):
    """Read a CSV file and return it as a DataFrame."""

    # pd.read_csv() opens the file, parses every row, and returns a DataFrame.
    # The column names come from the first row of the CSV automatically.
    df = pd.read_csv(filepath)

    # parse_dates would also work here, but keeping it simple for now.
    # df.shape is a tuple (rows, columns) — useful for a quick sanity check.
    print(f"Loaded {df.shape[0]} invoices, {df.shape[1]} columns.")

    return df  # Hand the DataFrame back to whoever called this function.


def group_by_vendor(df):
    """Group invoices by vendor and compute total spend, invoice count, and average amount.

    WHAT IS GROUPBY?
    Imagine sorting all invoices into separate piles — one pile per vendor.
    groupby() does exactly that in memory, then lets you run a calculation on each pile.
    The result is one summary row per vendor instead of one row per invoice.
    """

    # df.groupby("vendor") splits the DataFrame into groups, one group per unique vendor name.
    # ["amount"] selects only the amount column inside each group.
    # .agg() runs multiple calculations at once — each key becomes a new column name.
    summary = (
        df.groupby("vendor")["amount"]
        .agg(
            total_spend="sum",    # Add up all invoice amounts for this vendor.
            invoice_count="count",  # Count how many invoices belong to this vendor.
            avg_invoice="mean",   # Divide total_spend by invoice_count.
        )
        .reset_index()  # groupby turns "vendor" into the index (row label).
                        # reset_index() promotes it back to a regular column.
    )

    # Round avg_invoice to 2 decimal places so it looks clean in the report.
    summary["avg_invoice"] = summary["avg_invoice"].round(2)

    return summary


def sort_by_spend(df):
    """Sort the summary DataFrame by total_spend, highest first."""

    # sort_values() reorders rows based on a column.
    # ascending=False means largest value appears at the top (like ORDER BY total_spend DESC in SQL).
    # ignore_index=True resets row numbers to 0, 1, 2, ... after sorting.
    sorted_df = df.sort_values("total_spend", ascending=False, ignore_index=True)

    return sorted_df


def flag_key_vendors(df):
    """Add a 'vendor_tier' column — 'Key Vendor' if total spend exceeds 2,00,000, else 'Standard'."""

    # np.where is one option, but a plain Python approach is clearer for learning:
    # df.apply() runs a function once per row and collects the return values into a new column.
    # 'row' here is one row of the DataFrame, accessed like a dictionary with row["column_name"].
    def assign_tier(row):
        # IF the vendor's total spend is above 200000, label them Key Vendor.
        if row["total_spend"] > 200000:
            return "Key Vendor"
        else:
            return "Standard"

    # df.apply(assign_tier, axis=1) calls assign_tier for every row (axis=1 means row-by-row).
    # The result is a new Series (a single column) which we assign to a new column called vendor_tier.
    df["vendor_tier"] = df.apply(assign_tier, axis=1)

    return df


def save_report(df, output_path):
    """Write the final DataFrame to an Excel file."""

    # to_excel() serialises the DataFrame into .xlsx format.
    # index=False prevents pandas from writing the row numbers (0,1,2...) as an extra column.
    # sheet_name sets the tab label inside the Excel workbook.
    df.to_excel(output_path, index=False, sheet_name="Vendor Spend")

    print(f"Report saved to {output_path}")


# ---------------------------------------------------------------
# MAIN BLOCK
# Code inside 'if __name__ == "__main__"' only runs when you execute this file directly.
# It won't run if another script imports this file — a good habit for reusable code.
# ---------------------------------------------------------------

if __name__ == "__main__":

    # Step 1 — Load
    invoices = load_invoices("invoices.csv")

    # Step 2 — Group
    summary = group_by_vendor(invoices)

    # Step 3 — Sort
    summary = sort_by_spend(summary)

    # Step 4 — Flag
    summary = flag_key_vendors(summary)

    # Step 5 — Preview in terminal before saving
    print("\n=== Vendor Spend Report ===\n")
    # pd.set_option controls how pandas prints tables in the terminal.
    # display.max_columns=None means: never hide columns by replacing them with '...'.
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 120)      # Wider output so columns don't wrap.
    pd.set_option("display.float_format", "{:,.2f}".format)  # Format numbers with commas.
    print(summary.to_string(index=False))    # to_string() prints the full table without truncation.

    # Step 6 — Save
    save_report(summary, "vendor_report.xlsx")
