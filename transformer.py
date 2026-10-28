#Validates and transforms records

def transform_user(user):
    """
    Validate and transform one external user record.
    Returns a clean dictionary or raises ValueError.
    """

    if not isinstance(user, dict):
        raise ValueError("User record must be a dictionary")

    external_id = user.get("id")
    name = user.get("name")
    email = user.get("email")

    # Validate required fields
    if type(external_id) is not int or external_id <= 0:
        raise ValueError("Invalid or missing user ID")

    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"Missing name for user {external_id}")

    if not isinstance(email, str) or "@" not in email:
        raise ValueError(f"Invalid email for user {external_id}")

    email = email.strip().lower()

    if not email or email.startswith("@") or email.endswith("@"):
        raise ValueError(f"Invalid email for user {external_id}")

    # Extract optional nested address data
    address = user.get("address") or {}

    if not isinstance(address, dict):
        address = {}

    city = address.get("city", "")
    phone = user.get("phone", "")

    return {
        "external_id": external_id,
        "full_name": name.strip(),
        "email": email,
        "city": city.strip() if isinstance(city, str) else "",
        "phone": phone.strip() if isinstance(phone, str) else ""
    }



def transform_users(users):
    """
    Transform a batch of user records.
    Returns valid records and rejected records separately.
    """

    valid_users = []
    rejected_users = []

    for index, user in enumerate(users):
        try:
            transformed = transform_user(user)
            valid_users.append(transformed)

        except ValueError as error:
            rejected_users.append({
                "record_index": index,
                "reason": str(error)
            })

    return valid_users, rejected_users
