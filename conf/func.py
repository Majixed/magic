import json

def get_admins():
    with open("admins.json", "r") as json_read:
        admin_data = json.load(json_read)
    admin_list = admin_data["botAdmin"]
    return admin_list
