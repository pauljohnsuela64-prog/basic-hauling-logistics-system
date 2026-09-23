import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


# ==============================
# DATABASE CONNECTION
# ==============================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="bbasic_hauling"
)


cursor = db.cursor()


# ==============================
# ADD TRUCK
# ==============================

def add_truck():

    print("\n==========================================")
    print("               ADD TRUCK")
    print("==========================================")
    print("Type B anytime to go back.")
    print("==========================================")

    while True:

        plate_number = input(
            "Enter Plate Number: "
        ).strip()

        if plate_number.upper() == "B":
            return

        if plate_number == "":
            print("Plate number cannot be empty.")
            continue

        try:

            cursor.execute("""
                INSERT INTO trucks (plate_number)
                VALUES (%s)
            """, (plate_number,))

            db.commit()

            print(f"\nTruck {plate_number} added successfully!")
            return

        except mysql.connector.IntegrityError:

            print("\nThat plate number already exists.")


# ==============================
# VIEW TRUCKS
# ==============================

def view_trucks():

    print("\n==========================================")
    print("               TRUCK LIST")
    print("==========================================")

    cursor.execute("""
        SELECT id, plate_number
        FROM trucks
        ORDER BY plate_number
    """)

    trucks = cursor.fetchall()

    if not trucks:

        print("\nNo trucks have been added yet.")
        return

    print("\nID     PLATE NUMBER")
    print("------------------------------------------")

    for truck in trucks:

        print(f"{truck[0]:<6} {truck[1]}")


# ==============================
# SELECT TRUCK
# ==============================

def select_truck():

    print("\n==========================================")
    print("             SELECT TRUCK")
    print("==========================================")

    cursor.execute("""
        SELECT id, plate_number
        FROM trucks
        ORDER BY plate_number
    """)

    trucks = cursor.fetchall()

    if not trucks:

        print("\nNo trucks have been added yet.")
        return

    print()

    for index, truck in enumerate(trucks, start=1):

        print(f"{index}. {truck[1]}")

    print(f"{len(trucks) + 1}. Back")

    print("==========================================")

    while True:

        choice = input(
            "Select truck (or B to go back): "
        ).strip()

        if choice.upper() == "B":
            return

        try:

            choice_number = int(choice)

        except ValueError:

            print("\nPlease enter a number.")
            continue

        if choice_number == len(trucks) + 1:

            return

        if choice_number < 1 or choice_number > len(trucks):

            print("\nInvalid truck selection.")
            continue

        truck_id = trucks[choice_number - 1][0]
        truck_plate = trucks[choice_number - 1][1]

        truck_menu(truck_id, truck_plate)

        return


# ==============================
# ADD TRUCK RECORD
# ==============================

def add_record(truck_id, plate_number):

    while True:

        print("\n==========================================")
        print(f"       ADD RECORD - {plate_number}")
        print("==========================================")
        print("Type B at any input to cancel this record.")
        print("==========================================")

        # ATW NUMBER

        while True:

            atw_number = input(
                "Enter ATW Number: "
            ).strip()

            if atw_number.upper() == "B":

                print("\nAdd Record cancelled.")
                return

            if atw_number == "":

                print("ATW Number cannot be empty.")
                continue

            # CHECK FOR DUPLICATE ATW

            cursor.execute("""
                SELECT
                    trucks.plate_number
                FROM truck_records
                INNER JOIN trucks
                    ON truck_records.truck_id = trucks.id
                WHERE truck_records.atw_number = %s
                LIMIT 1
            """, (atw_number,))

            duplicate = cursor.fetchone()

            if duplicate is not None:

                print("\n==========================================")
                print("           DUPLICATE ATW WARNING")
                print("==========================================")
                print(f"ATW Number: {atw_number}")
                print(
                    f"This ATW already exists for truck "
                    f"{duplicate[0]}."
                )
                print("Please enter a different ATW Number.")
                print("==========================================")

                continue

            break

        # DATE

        while True:

            date_input = input(
                "Enter Date (YYYY-MM-DD): "
            ).strip()

            if date_input.upper() == "B":

                print("\nAdd Record cancelled.")
                return

            try:

                date_value = datetime.strptime(
                    date_input,
                    "%Y-%m-%d"
                ).date()

                break

            except ValueError:

                print("Invalid date. Please use YYYY-MM-DD.")

        # DESTINATION

        destination = input(
            "Enter Destination: "
        ).strip()

        if destination.upper() == "B":

            print("\nAdd Record cancelled.")
            return

        if destination == "":

            print("Destination cannot be empty.")
            continue

        # LITERS

        while True:

            liters_input = input(
                "Enter Liters: "
            ).strip()

            if liters_input.upper() == "B":

                print("\nAdd Record cancelled.")
                return

            try:

                liters = float(
                    liters_input.replace(",", "")
                )

                if liters <= 0:

                    print("Liters must be greater than 0.")

                else:

                    break

            except ValueError:

                print("Please enter a valid number.")

        # PRICE PER LITER

        while True:

            price_input = input(
                "Enter Price per Liter: "
            ).strip()

            if price_input.upper() == "B":

                print("\nAdd Record cancelled.")
                return

            try:

                price_per_liter = float(
                    price_input.replace(",", "")
                )

                if price_per_liter <= 0:

                    print(
                        "Price per liter must be greater than 0."
                    )

                else:

                    break

            except ValueError:

                print("Please enter a valid number.")

        # AUTOMATIC PREVIOUS ODO

        cursor.execute("""
            SELECT current_odo
            FROM truck_records
            WHERE truck_id = %s
            AND current_odo IS NOT NULL
            ORDER BY date DESC, id DESC
            LIMIT 1
        """, (truck_id,))

        previous_record = cursor.fetchone()

        if previous_record is None:

            print("\nNo previous ODO found for this truck.")

            while True:

                previous_input = input(
                    "Enter Previous ODO (optional): "
                ).strip()

                if previous_input.upper() == "B":

                    print("\nAdd Record cancelled.")
                    return

                if previous_input == "":

                    previous_odo = None
                    break

                try:

                    previous_odo = float(
                        previous_input.replace(",", "")
                    )

                    if previous_odo < 0:

                        print("ODO cannot be negative.")

                    else:

                        break

                except ValueError:

                    print("Please enter a valid number.")

        else:

            previous_odo = float(previous_record[0])

            print(
                f"\nPrevious ODO automatically set to: "
                f"{previous_odo:,.2f}"
            )

        # CURRENT ODO

        while True:

            current_input = input(
                "Enter Current ODO: "
            ).strip()

            if current_input.upper() == "B":

                print("\nAdd Record cancelled.")
                return

            try:

                current_odo = float(
                    current_input.replace(",", "")
                )

                if current_odo < 0:

                    print("ODO cannot be negative.")
                    continue

                if (
                    previous_odo is not None
                    and current_odo < previous_odo
                ):

                    print(
                        "Current ODO cannot be lower "
                        "than Previous ODO."
                    )
                    continue

                break

            except ValueError:

                print("Please enter a valid number.")

        # CALCULATIONS

        total_price = liters * price_per_liter

        if previous_odo is not None:

            distance = current_odo - previous_odo

            if liters > 0:

                fuel_efficiency = distance / liters

            else:

                fuel_efficiency = 0

        else:

            distance = None
            fuel_efficiency = None

        # RECORD SUMMARY

        print("\n==========================================")
        print("              RECORD SUMMARY")
        print("==========================================")

        print(f"Plate Number:     {plate_number}")
        print(f"ATW Number:       {atw_number}")
        print(f"Date:             {date_value}")
        print(f"Destination:      {destination}")
        print(f"Liters:           {liters:,.2f}")
        print(f"Price per Liter:  ₱{price_per_liter:,.2f}")
        print(f"Total Price:      ₱{total_price:,.2f}")

        if previous_odo is None:

            print("Previous ODO:     N/A")

        else:

            print(f"Previous ODO:     {previous_odo:,.2f}")

        print(f"Current ODO:      {current_odo:,.2f}")

        if distance is None:

            print("Distance:         N/A")
            print("Fuel Efficiency:  N/A")

        else:

            print(f"Distance:         {distance:,.2f} km")
            print(
                f"Fuel Efficiency:  "
                f"{fuel_efficiency:,.2f} km/L"
            )

        confirm = input(
            "\nSave this record? (Y/N): "
        ).strip().upper()

        if confirm == "B":

            print("\nAdd Record cancelled.")
            return

        if confirm != "Y":

            print("\nRecord was not saved.")

            continue_input = input(
                "Try another record? (Y/N): "
            ).strip().upper()

            if continue_input == "B":

                return

            if continue_input != "Y":

                return

            continue

        # SAVE RECORD

        sql = """
            INSERT INTO truck_records (
                truck_id,
                atw_number,
                date,
                destination,
                liters,
                price_per_liter,
                total_price,
                previous_odo,
                current_odo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            truck_id,
            atw_number,
            date_value,
            destination,
            liters,
            price_per_liter,
            total_price,
            previous_odo,
            current_odo
        )

        cursor.execute(sql, values)

        db.commit()

        # SAVED RECORD CONFIRMATION

        print("\n==========================================")
        print("          RECORD SAVED SUCCESSFULLY")
        print("==========================================")

        print(f"Truck:            {plate_number}")
        print(f"ATW Number:       {atw_number}")
        print(f"Date:             {date_value}")
        print(f"Destination:      {destination}")
        print(f"Liters:           {liters:,.2f}")
        print(f"Price per Liter:  ₱{price_per_liter:,.2f}")
        print(f"Total Price:      ₱{total_price:,.2f}")

        if previous_odo is None:

            print("Previous ODO:     N/A")

        else:

            print(f"Previous ODO:     {previous_odo:,.2f}")

        print(f"Current ODO:      {current_odo:,.2f}")

        if distance is None:

            print("Distance:         N/A")
            print("Fuel Efficiency:  N/A")

        else:

            print(f"Distance:         {distance:,.2f} km")
            print(
                f"Fuel Efficiency:  "
                f"{fuel_efficiency:,.2f} km/L"
            )

        print("==========================================")

        continue_input = input(
            "\nAdd another record for "
            f"{plate_number}? (Y/N): "
        ).strip().upper()

        if continue_input == "B":

            return

        if continue_input != "Y":

            return


# ==============================
# VIEW TRUCK RECORDS
# ==============================

def view_records(truck_id, plate_number):

    print("\n==========================================")
    print(f"       RECORDS - {plate_number}")
    print("==========================================")

    cursor.execute("""
        SELECT
            id,
            atw_number,
            date,
            destination,
            liters,
            price_per_liter,
            total_price,
            previous_odo,
            current_odo
        FROM truck_records
        WHERE truck_id = %s
        ORDER BY date, id
    """, (truck_id,))

    records = cursor.fetchall()

    if not records:

        print("\nNo records found for this truck.")
        return

    for record in records:

        atw_number = record[1]
        date = record[2]
        destination = record[3]
        liters = record[4]
        price_per_liter = record[5]
        total_price = record[6]
        previous_odo = record[7]
        current_odo = record[8]

        print("\n------------------------------------------")

        print(f"ATW Number:       {atw_number}")
        print(f"Date:             {date}")
        print(f"Destination:      {destination}")
        print(f"Liters:           {liters:,.2f}")
        print(f"Price per Liter:  ₱{price_per_liter:,.2f}")
        print(f"Total Price:      ₱{total_price:,.2f}")

        if previous_odo is None:

            print("Previous ODO:     N/A")
            print(f"Current ODO:      {current_odo:,.2f}")
            print("Distance:         N/A")
            print("Fuel Efficiency:  N/A")

        else:

            distance = current_odo - previous_odo

            if liters > 0:

                fuel_efficiency = distance / liters

            else:

                fuel_efficiency = 0

            print(f"Previous ODO:     {previous_odo:,.2f}")
            print(f"Current ODO:      {current_odo:,.2f}")
            print(f"Distance:         {distance:,.2f} km")
            print(
                f"Fuel Efficiency:  "
                f"{fuel_efficiency:,.2f} km/L"
            )

    print("------------------------------------------")


# ==============================
# UPDATE RECORD
# ==============================

def update_record(truck_id, plate_number):

    print("\n==========================================")
    print(f"       UPDATE RECORD - {plate_number}")
    print("==========================================")
    print("1. Update Record")
    print("2. Back")
    print("==========================================")

    while True:

        choice = input("Select an option: ").strip()

        if choice == "1":
            break

        elif choice == "2" or choice.upper() == "B":
            return

        else:
            print("\nInvalid choice. Please try again.")

    # FIND RECORD

    while True:

        atw_number = input(
            "Enter ATW Number to update (or B to go back): "
        ).strip()

        if atw_number.upper() == "B":

            return

        if atw_number == "":

            print("ATW Number cannot be empty.")
            continue

        cursor.execute("""
            SELECT
                id,
                atw_number,
                date,
                destination,
                liters,
                price_per_liter,
                previous_odo,
                current_odo
            FROM truck_records
            WHERE truck_id = %s
            AND atw_number = %s
        """, (truck_id, atw_number))

        record = cursor.fetchone()

        if record is None:

            print("\nNo record found with that ATW Number.")
            return

        break

    record_id = record[0]

    old_atw = record[1]
    old_date = record[2]
    old_destination = record[3]
    old_liters = record[4]
    old_price = record[5]
    old_previous_odo = record[6]
    old_current_odo = record[7]

    if old_previous_odo is not None:

        old_total = old_liters * old_price
        old_distance = old_current_odo - old_previous_odo

        if old_liters > 0:

            old_efficiency = old_distance / old_liters

        else:

            old_efficiency = 0

    else:

        old_total = old_liters * old_price
        old_distance = None
        old_efficiency = None

    # SHOW CURRENT RECORD

    print("\n==========================================")
    print("           CURRENT RECORD")
    print("==========================================")

    print(f"Plate Number:     {plate_number}")
    print(f"ATW Number:       {old_atw}")
    print(f"Date:             {old_date}")
    print(f"Destination:      {old_destination}")
    print(f"Liters:           {old_liters:,.2f}")
    print(f"Price per Liter:  ₱{old_price:,.2f}")
    print(f"Total Price:      ₱{old_total:,.2f}")

    if old_previous_odo is None:

        print("Previous ODO:     N/A")

    else:

        print(f"Previous ODO:     {old_previous_odo:,.2f}")

    print(f"Current ODO:      {old_current_odo:,.2f}")

    if old_distance is None:

        print("Distance:         N/A")
        print("Fuel Efficiency:  N/A")

    else:

        print(f"Distance:         {old_distance:,.2f} km")
        print(
            f"Fuel Efficiency:  "
            f"{old_efficiency:,.2f} km/L"
        )

    print("\n==========================================")
    print("           ENTER NEW INFORMATION")
    print("==========================================")
    print("Type B at any input to cancel the update.")
    print("==========================================")

    # DATE

    while True:

        date_input = input(
            f"Enter New Date (YYYY-MM-DD) [{old_date}]: "
        ).strip()

        if date_input.upper() == "B":

            print("\nUpdate cancelled.")
            return

        if date_input == "":

            date_value = old_date
            break

        try:

            date_value = datetime.strptime(
                date_input,
                "%Y-%m-%d"
            ).date()

            break

        except ValueError:

            print("Invalid date. Please use YYYY-MM-DD.")

    # DESTINATION

    destination = input(
        f"Enter New Destination [{old_destination}]: "
    ).strip()

    if destination.upper() == "B":

        print("\nUpdate cancelled.")
        return

    if destination == "":

        destination = old_destination

    # LITERS

    while True:

        liters_input = input(
            f"Enter New Liters [{old_liters:,.2f}]: "
        ).strip()

        if liters_input.upper() == "B":

            print("\nUpdate cancelled.")
            return

        if liters_input == "":

            liters = float(old_liters)
            break

        try:

            liters = float(
                liters_input.replace(",", "")
            )

            if liters <= 0:

                print("Liters must be greater than 0.")

            else:

                break

        except ValueError:

            print("Please enter a valid number.")

    # PRICE PER LITER

    while True:

        price_input = input(
            f"Enter New Price per Liter "
            f"[₱{old_price:,.2f}]: "
        ).strip()

        if price_input.upper() == "B":

            print("\nUpdate cancelled.")
            return

        if price_input == "":

            price_per_liter = float(old_price)
            break

        try:

            price_per_liter = float(
                price_input.replace(",", "")
            )

            if price_per_liter <= 0:

                print(
                    "Price per liter must be greater than 0."
                )

            else:

                break

        except ValueError:

            print("Please enter a valid number.")

    # PREVIOUS ODO

    if old_previous_odo is None:

        while True:

            previous_input = input(
                "Enter New Previous ODO (optional): "
            ).strip()

            if previous_input.upper() == "B":

                print("\nUpdate cancelled.")
                return

            if previous_input == "":

                previous_odo = None
                break

            try:

                previous_odo = float(
                    previous_input.replace(",", "")
                )

                if previous_odo < 0:

                    print("ODO cannot be negative.")

                else:

                    break

            except ValueError:

                print("Please enter a valid number.")

    else:

        while True:

            previous_input = input(
                f"Enter New Previous ODO "
                f"[{old_previous_odo:,.2f}]: "
            ).strip()

            if previous_input.upper() == "B":

                print("\nUpdate cancelled.")
                return

            if previous_input == "":

                previous_odo = float(old_previous_odo)
                break

            try:

                previous_odo = float(
                    previous_input.replace(",", "")
                )

                if previous_odo < 0:

                    print("ODO cannot be negative.")

                else:

                    break

            except ValueError:

                print("Please enter a valid number.")

    # CURRENT ODO

    while True:

        current_input = input(
            f"Enter New Current ODO "
            f"[{old_current_odo:,.2f}]: "
        ).strip()

        if current_input.upper() == "B":

            print("\nUpdate cancelled.")
            return

        if current_input == "":

            current_odo = float(old_current_odo)
            break

        try:

            current_odo = float(
                current_input.replace(",", "")
            )

            if current_odo < 0:

                print("ODO cannot be negative.")

            elif (
                previous_odo is not None
                and current_odo < previous_odo
            ):

                print(
                    "Current ODO cannot be lower "
                    "than Previous ODO."
                )

            else:

                break

        except ValueError:

            print("Please enter a valid number.")

    # CALCULATIONS

    total_price = liters * price_per_liter

    if previous_odo is not None:

        distance = current_odo - previous_odo

        if liters > 0:

            fuel_efficiency = distance / liters

        else:

            fuel_efficiency = 0

    else:

        distance = None
        fuel_efficiency = None

    # UPDATED SUMMARY

    print("\n==========================================")
    print("           UPDATED RECORD")
    print("==========================================")

    print(f"Plate Number:     {plate_number}")
    print(f"ATW Number:       {old_atw}")
    print(f"Date:             {date_value}")
    print(f"Destination:      {destination}")
    print(f"Liters:           {liters:,.2f}")
    print(f"Price per Liter:  ₱{price_per_liter:,.2f}")
    print(f"Total Price:      ₱{total_price:,.2f}")

    if previous_odo is None:

        print("Previous ODO:     N/A")

    else:

        print(f"Previous ODO:     {previous_odo:,.2f}")

    print(f"Current ODO:      {current_odo:,.2f}")

    if distance is None:

        print("Distance:         N/A")
        print("Fuel Efficiency:  N/A")

    else:

        print(f"Distance:         {distance:,.2f} km")
        print(
            f"Fuel Efficiency:  "
            f"{fuel_efficiency:,.2f} km/L"
        )

    confirm = input(
        "\nSave these changes? (Y/N): "
    ).strip().upper()

    if confirm == "B":

        print("\nUpdate cancelled.")
        return

    if confirm != "Y":

        print("\nUpdate cancelled.")
        return

    # UPDATE DATABASE

    sql = """
        UPDATE truck_records
        SET
            date = %s,
            destination = %s,
            liters = %s,
            price_per_liter = %s,
            total_price = %s,
            previous_odo = %s,
            current_odo = %s
        WHERE id = %s
    """

    values = (
        date_value,
        destination,
        liters,
        price_per_liter,
        total_price,
        previous_odo,
        current_odo,
        record_id
    )

    cursor.execute(sql, values)

    db.commit()

    print("\nRecord updated successfully!")


# ==============================
# DELETE RECORD
# ==============================

def delete_record(truck_id, plate_number):

    print("\n==========================================")
    print(f"       DELETE RECORD - {plate_number}")
    print("==========================================")
    print("1. Delete Record")
    print("2. Back")
    print("==========================================")

    while True:

        choice = input("Select an option: ").strip()

        if choice == "1":
            break

        elif choice == "2" or choice.upper() == "B":
            return

        else:
            print("\nInvalid choice. Please try again.")

    # FIND RECORD

    atw_number = input(
        "Enter ATW Number to delete (or B to go back): "
    ).strip()

    if atw_number.upper() == "B":

        return

    if atw_number == "":

        print("ATW Number cannot be empty.")
        return

    cursor.execute("""
        SELECT
            id,
            atw_number,
            date,
            destination,
            liters,
            price_per_liter,
            total_price,
            previous_odo,
            current_odo
        FROM truck_records
        WHERE truck_id = %s
        AND atw_number = %s
    """, (truck_id, atw_number))

    record = cursor.fetchone()

    if record is None:

        print("\nNo record found with that ATW Number.")
        return

    record_id = record[0]
    atw = record[1]
    date = record[2]
    destination = record[3]
    liters = record[4]
    price_per_liter = record[5]
    total_price = record[6]
    previous_odo = record[7]
    current_odo = record[8]

    print("\n==========================================")
    print("           RECORD TO DELETE")
    print("==========================================")

    print(f"Plate Number:     {plate_number}")
    print(f"ATW Number:       {atw}")
    print(f"Date:             {date}")
    print(f"Destination:      {destination}")
    print(f"Liters:           {liters:,.2f}")
    print(f"Price per Liter:  ₱{price_per_liter:,.2f}")
    print(f"Total Price:      ₱{total_price:,.2f}")

    if previous_odo is None:

        print("Previous ODO:     N/A")

    else:

        print(f"Previous ODO:     {previous_odo:,.2f}")

    print(f"Current ODO:      {current_odo:,.2f}")

    if previous_odo is None:

        print("Distance:         N/A")
        print("Fuel Efficiency:  N/A")

    else:

        distance = current_odo - previous_odo

        if liters > 0:

            fuel_efficiency = distance / liters

        else:

            fuel_efficiency = 0

        print(f"Distance:         {distance:,.2f} km")
        print(
            f"Fuel Efficiency:  "
            f"{fuel_efficiency:,.2f} km/L"
        )

    print("\n==========================================")

    confirm = input(
        "Are you sure you want to DELETE this record? (Y/N): "
    ).strip().upper()

    if confirm == "B":

        print("\nDelete cancelled.")
        return

    if confirm != "Y":

        print("\nDelete cancelled.")
        return

    cursor.execute("""
        DELETE FROM truck_records
        WHERE id = %s
    """, (record_id,))

    db.commit()

    print("\nRecord deleted successfully!")


# ==============================
# SEARCH BY PLATE NUMBER
# ==============================

def search_by_plate():

    print("\n==========================================")
    print("        SEARCH BY PLATE NUMBER")
    print("==========================================")

    plate_number = input(
        "Enter Plate Number (or B to go back): "
    ).strip()

    if plate_number.upper() == "B":

        return

    if plate_number == "":

        print("Plate Number cannot be empty.")
        return

    cursor.execute("""
        SELECT
            trucks.plate_number,
            truck_records.atw_number,
            truck_records.date,
            truck_records.destination,
            truck_records.liters,
            truck_records.price_per_liter,
            truck_records.total_price,
            truck_records.previous_odo,
            truck_records.current_odo
        FROM trucks
        INNER JOIN truck_records
            ON trucks.id = truck_records.truck_id
        WHERE trucks.plate_number = %s
        ORDER BY truck_records.date, truck_records.id
    """, (plate_number,))

    records = cursor.fetchall()

    if not records:

        print("\nNo records found for this plate number.")
        return

    print("\n==========================================")
    print(f"      RECORDS FOR {plate_number}")
    print("==========================================")

    for record in records:

        plate = record[0]
        atw = record[1]
        date = record[2]
        destination = record[3]
        liters = record[4]
        price_per_liter = record[5]
        total_price = record[6]
        previous_odo = record[7]
        current_odo = record[8]

        print("\n------------------------------------------")

        print(f"Plate Number:     {plate}")
        print(f"ATW Number:       {atw}")
        print(f"Date:             {date}")
        print(f"Destination:      {destination}")
        print(f"Liters:           {liters:,.2f}")
        print(f"Price per Liter:  ₱{price_per_liter:,.2f}")
        print(f"Total Price:      ₱{total_price:,.2f}")

        if previous_odo is None:

            print("Previous ODO:     N/A")
            print(f"Current ODO:      {current_odo:,.2f}")
            print("Distance:         N/A")
            print("Fuel Efficiency:  N/A")

        else:

            distance = current_odo - previous_odo

            if liters > 0:

                fuel_efficiency = distance / liters

            else:

                fuel_efficiency = 0

            print(f"Previous ODO:     {previous_odo:,.2f}")
            print(f"Current ODO:      {current_odo:,.2f}")
            print(f"Distance:         {distance:,.2f} km")
            print(
                f"Fuel Efficiency:  "
                f"{fuel_efficiency:,.2f} km/L"
            )

    print("------------------------------------------")


# ==============================
# SEARCH BY ATW NUMBER
# ==============================

def search_by_atw():

    print("\n==========================================")
    print("          SEARCH BY ATW NUMBER")
    print("==========================================")

    atw_number = input(
        "Enter ATW Number (or B to go back): "
    ).strip()

    if atw_number.upper() == "B":

        return

    if atw_number == "":

        print("ATW Number cannot be empty.")
        return

    cursor.execute("""
        SELECT
            trucks.plate_number,
            truck_records.atw_number,
            truck_records.date,
            truck_records.destination,
            truck_records.liters,
            truck_records.price_per_liter,
            truck_records.total_price,
            truck_records.previous_odo,
            truck_records.current_odo
        FROM truck_records
        INNER JOIN trucks
            ON truck_records.truck_id = trucks.id
        WHERE truck_records.atw_number = %s
    """, (atw_number,))

    record = cursor.fetchone()

    if record is None:

        print("\nNo record found with that ATW Number.")
        return

    plate = record[0]
    atw = record[1]
    date = record[2]
    destination = record[3]
    liters = record[4]
    price_per_liter = record[5]
    total_price = record[6]
    previous_odo = record[7]
    current_odo = record[8]

    print("\n==========================================")
    print("              RECORD FOUND")
    print("==========================================")

    print(f"Plate Number:     {plate}")
    print(f"ATW Number:       {atw}")
    print(f"Date:             {date}")
    print(f"Destination:      {destination}")
    print(f"Liters:           {liters:,.2f}")
    print(f"Price per Liter:  ₱{price_per_liter:,.2f}")
    print(f"Total Price:      ₱{total_price:,.2f}")

    if previous_odo is None:

        print("Previous ODO:     N/A")
        print(f"Current ODO:      {current_odo:,.2f}")
        print("Distance:         N/A")
        print("Fuel Efficiency:  N/A")

    else:

        distance = current_odo - previous_odo

        if liters > 0:

            fuel_efficiency = distance / liters

        else:

            fuel_efficiency = 0

        print(f"Previous ODO:     {previous_odo:,.2f}")
        print(f"Current ODO:      {current_odo:,.2f}")
        print(f"Distance:         {distance:,.2f} km")
        print(
            f"Fuel Efficiency:  "
            f"{fuel_efficiency:,.2f} km/L"
        )


# ==============================
# SEARCH MENU
# ==============================

def search_records():

    while True:

        print("\n==========================================")
        print("             SEARCH RECORDS")
        print("==========================================")
        print("1. Search by Plate Number")
        print("2. Search by ATW Number")
        print("3. Back")
        print("==========================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            search_by_plate()

        elif choice == "2":

            search_by_atw()

        elif choice == "3" or choice.upper() == "B":

            break

        else:

            print("\nInvalid choice. Please try again.")


# ==============================
# TRUCK MENU
# ==============================

def truck_menu(truck_id, plate_number):

    while True:

        print("\n==========================================")
        print(f"             TRUCK: {plate_number}")
        print("==========================================")
        print("1. Add Record")
        print("2. View Records")
        print("3. Update Record")
        print("4. Delete Record")
        print("5. Back")
        print("==========================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            add_record(truck_id, plate_number)

        elif choice == "2":

            view_records(truck_id, plate_number)

        elif choice == "3":

            update_record(truck_id, plate_number)

        elif choice == "4":

            delete_record(truck_id, plate_number)

        elif choice == "5" or choice.upper() == "B":

            break

        else:

            print("\nInvalid choice. Please try again.")


# ==============================
# MANAGE TRUCKS MENU
# ==============================

def manage_trucks():

    while True:

        print("\n==========================================")
        print("             MANAGE TRUCKS")
        print("==========================================")
        print("1. Add Truck")
        print("2. View Trucks")
        print("3. Back")
        print("==========================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            add_truck()

        elif choice == "2":

            view_trucks()

        elif choice == "3" or choice.upper() == "B":

            break

        else:

            print("\nInvalid choice. Please try again.")


# ==============================
# TRUCK RECORDS MENU
# ==============================

def truck_records_menu():

    while True:

        print("\n==========================================")
        print("             TRUCK RECORDS")
        print("==========================================")
        print("1. Select Truck")
        print("2. Back")
        print("==========================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            select_truck()

        elif choice == "2" or choice.upper() == "B":

            break

        else:

            print("\nInvalid choice. Please try again.")


# ==============================
# MAIN MENU
# ==============================

def main():

    while True:

        print("\n==========================================")
        print("       BASIC HAULING & LOGISTICS")
        print("==========================================")
        print("1. Manage Trucks")
        print("2. Truck Records")
        print("3. Search Records")
        print("4. Exit")
        print("==========================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            manage_trucks()

        elif choice == "2":

            truck_records_menu()

        elif choice == "3":

            search_records()

        elif choice == "4" or choice.upper() == "B":

            print("\nExiting system...")
            break

        else:

            print("\nInvalid choice. Please try again.")


# ==============================
# RUN PROGRAM
# ==============================

main()

cursor.close()
db.close()