import db_operations as dbo

def display_donations():
    print("\n--- Food Donation Listings ---")
    docs = dbo.get_all_donations()
    if not docs:
        print("No donations recorded.")
        return
    for d in docs:
        print(f"[{d.get('donation_id')}] {d.get('item_name')} | Category: {d.get('category')} | Qty: {d.get('quantity')} | Donor: {d.get('donor_name')} | Status: {d.get('status')}")

def display_shelters():
    print("\n--- Registered Shelters & NGOs ---")
    docs = dbo.get_all_shelters()
    for s in docs:
        print(f"[{s.get('shelter_id')}] {s.get('name')} | Contact: {s.get('contact')} | City: {s.get('city')}")

def handle_add_shelter():
    print("\n--- Register Shelter ---")
    s_id = input("Enter Shelter ID (e.g., SHL003): ").strip()
    name = input("Enter Shelter Name: ").strip()
    contact = input("Enter Contact Number: ").strip()
    city = input("Enter City: ").strip()
    if not s_id or not name:
        print("[Error] Fields cannot be empty.")
        return
    success, msg = dbo.insert_shelter(s_id, name, contact, city)
    print(msg)

def handle_add_donation():
    print("\n--- Post Food Donation ---")
    d_id = input("Enter Donation ID (e.g., DON004): ").strip()
    item = input("Enter Item Name: ").strip()
    cat = input("Enter Category (Prepared Food / Bakery / Fresh Produce): ").strip()
    try:
        qty = int(input("Enter Quantity (servings/kg): ").strip())
        if qty <= 0:
            print("[Error] Quantity must be greater than 0.")
            return
    except ValueError:
        print("[Error] Quantity must be an integer.")
        return
    donor = input("Enter Donor Name: ").strip()

    success, msg = dbo.insert_donation(d_id, item, cat, qty, donor)
    print(msg)

def handle_claim():
    print("\n--- Claim Food Batch ---")
    display_donations()
    d_id = input("\nEnter Donation ID to claim: ").strip()
    display_shelters()
    s_id = input("\nEnter Shelter ID claiming: ").strip()
    success, msg = dbo.claim_donation(d_id, s_id)
    print(msg)

def handle_update():
    print("\n--- Update Status ---")
    d_id = input("Enter Donation ID: ").strip()
    status = input("Enter New Status (Available / Claimed / Delivered / Cancelled): ").strip()
    success, msg = dbo.update_status(d_id, status)
    print(msg)

def handle_feedback():
    print("\n--- Submit Feedback ---")
    d_id = input("Enter Donation ID: ").strip()
    try:
        rating = int(input("Enter Rating (1-5): ").strip())
        if rating < 1 or rating > 5:
            print("[Error] Rating must be between 1 and 5.")
            return
    except ValueError:
        print("[Error] Invalid rating.")
        return
    comments = input("Enter Comments: ").strip()
    success, msg = dbo.insert_feedback(d_id, rating, comments)
    print(msg)

def handle_aggregation():
    by_status, by_cat = dbo.run_aggregation()
    print("\n==============================================")
    print("      AGGREGATION REPORT: FOOD RESCUE STATS   ")
    print("==============================================")
    print("\n1. Food Quantity by Status (Servings Diverted):")
    for r in by_status:
        print(f"   Status: {r['_id']:<12} | Total Quantity: {r['total_servings']} | Batches: {r['count']}")

    print("\n2. Donation Distribution by Food Category:")
    for r in by_cat:
        print(f"   Category: {r['_id']:<15} | Listings: {r['count']} | Avg Servings: {round(r['avg_servings'], 1)}")

def main():
    dbo.setup_database()
    while True:
        print("\n" + "="*50)
        print("  ZERO HUNGER (SDG 2) - FOOD REDISTRIBUTION SYSTEM")
        print("="*50)
        print("1. View Available Food Donations")
        print("2. View Registered Shelters & NGOs")
        print("3. Register New Shelter/NGO")
        print("4. Post Surplus Food Listing (Create)")
        print("5. Claim Food Listing (Registration)")
        print("6. Update Delivery Status (Update)")
        print("7. Submit Food Delivery Feedback")
        print("8. Generate Aggregation Analytics Report")
        print("9. Exit Application")

        choice = input("\nEnter choice (1-9): ").strip()
        if choice == "1":
            display_donations()
        elif choice == "2":
            display_shelters()
        elif choice == "3":
            handle_add_shelter()
        elif choice == "4":
            handle_add_donation()
        elif choice == "5":
            handle_claim()
        elif choice == "6":
            handle_update()
        elif choice == "7":
            handle_feedback()
        elif choice == "8":
            handle_aggregation()
        elif choice == "9":
            print("\nExiting. Goodbye!")
            break
        else:
            print("[Warning] Invalid choice. Choose 1-9.")

if __name__ == "__main__":
    main()