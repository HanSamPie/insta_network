import csv
import os
import instaloader

loader = instaloader.Instaloader()

user = os.getenv("INSTA_USER")
# password = os.getenv("INSTA_PASSWORD")
# print(f"Username is:{user}      Password is: {'*' * len(password)}")

print("Attempting login....")
loader.load_session_from_file(user.lower())
print("Succesful Login!\n")

print("Loading User Names....")
with open("./form_responses.csv") as file:
    data = list(csv.DictReader(file))
print(f"Loaded {len(data)} Usernames\n")

print("------------------------------")
# TODO Filter for accounts I dont follow
print("Private Accounts:")
private_accs = [ row["Instagram Username"] for row in data if row["Der angegeben Account ist Privat"] == "TRUE"]
for acc in private_accs: print(acc)
print("------------------------------")

#profiles = set(re.split(r"\s+", text.strip()))
profiles = [ row["Instagram Username"] for row in data ]

for user in profiles:
    profile = instaloader.Profile.from_username(loader.context, user)
    print("Follwers: ",profile.followers)

    followers = profile.get_followers()
    for f in followers: print(f.username)

