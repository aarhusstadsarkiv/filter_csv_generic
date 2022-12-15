import json
from pathlib import Path
import csv
import argparse
from . import settings


def hasID(idstring: str, id: str) -> bool:
    _id = idstring.split(";")[0]
    return _id == id


def main(args=None):
    # output: dict[str, dict[str, str]] = {}
    output: list[tuple[int, int, int]] = []

    parser = argparse.ArgumentParser(
        description=(
            "Filters the csv formatted backup database.\n"
            "Apply any number of --filter: Allowed field searches are:\n"
            "collection, curators, desc_notes, date_from, creators, reg_id \n"
            "Allowed operators are: "
            "equalTo, notEqualTo, greaterThan, lessThan, contains.\n\n"
            'ex.1 field is "id-field"\n'
            "--filter collection equalTo 1\n\n"
            "ex.2 if the field is a dictionary, and target search is in a key's value:\n"
            '--filter admin_data contains "Bestillingsinformation:negativsamlingen 1970"\n\n'
            "ex.3 if the field is a dictionary, and filter after target has a certain key:\n"
            "--filter admin_data hasKey Bestillingsinformation\n\n"
            "ex.4 the field is a dictionary and the key is known and filter on the value:\n"
            "--filter desc_data contains Typer:Farve"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "csv_path",
        metavar="input_dir",
        type=Path,
        help="Path to the backup database csv file.",
    )
    parser.add_argument(
        "output_path",
        metavar="output_dir",
        type=Path,
        help="Path to the output/result directory for csv file(s).",
    )
    parser.add_argument(
        "--filter",
        type=str,
        nargs=3,
        action="append",
        help=("Adds a filter to limit the results"),
    )

    args = parser.parse_args(args)

    input_dir = Path(args.csv_path)
    output_dir = Path(args.output_path)

    print("Starting filtering process...")
    # print(input_dir)
    # print(output_dir)

    filters: list[list[str]] = args.filter

    # csv_path = Path(
    #     "C:\\Users\\az68636\\github\\filter-csv-generic\\tests\\test_data\\2022-11-29_oas_backup.csv"
    # )

    csv_path = input_dir

    with open(csv_path, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)

        for row in csvReader:
            _dict: dict = json.loads(row["oasDictText"])

            id = row["id"]

            operators_results: list[bool] = []

            for i in range(len(filters)):

                fieldname: str = args.filter[i][0]
                operator_key = args.filter[i][1]
                operator = settings.FIELDS[fieldname][operator_key]
                value = args.filter[i][2]

                if not _dict.get(fieldname):
                    op_results = False
                else:
                    op_results = operator(_dict[fieldname], value)

                operators_results.append(op_results)

            total_op_result = all(operators_results)

            if not total_op_result:
                continue  # if false

            output.append([id])  # if true

    max_file_size = 5000
    count = 0
    for i in range(0, len(output), max_file_size):

        # output_path = "C:\\Users\\az68636\\github\\filter-csv-generic\\tests\\test_data\\"
        csv_out_path = Path(output_dir, Path("filter_results_" + str(count) + ".csv"))

        with open(csv_out_path, "w", newline="") as f:
            write = csv.writer(f)
            write.writerow(["id"])
            write.writerows(output[i : i + max_file_size])

        count += 1

    print("Done: Found " + str(len(output)) + " results matching the applied filter(s)")


if __name__ == "__main__":
    main()
