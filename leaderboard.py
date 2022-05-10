from db import users

def get_top_x_role(top: int, role: str):
    """
    > This function takes in a number and a role, and returns a dictionary with the top x users for that role

    :param top: the number of users you want to get
    :type top: int
    :param role: the role you want to get the top players for
    :type role: str
    :return: A dictionary with the top x users for a given role.
    """
    all_users = list(users.find())
    out = sorted(all_users, key=lambda i: i['ratings'][role]["mu"], reverse=True)[:top]
    return {f"top {top} {role}": out}


def get_top_x_overall(top: int):
    """
    It gets the top 10 users overall

    :param top: int - the number of users to return
    :type top: int
    :return: A dictionary with the key "top 10 overall" and the value is a list of the top 10 users.
    """
    out = []
    roles = ["tank", "damage", "support"]
    all_users = list(users.find())
    for role in roles:
        out.extend(sorted(all_users, key=lambda i: i['ratings'][role]["mu"], reverse=True)[:top])
    return {f"top {top} overall": out[:10]}
