import csv
import os
import instaloader

loader = instaloader.Instaloader()

# user = os.getenv("INSTA_USER")
# password = os.getenv("INSTA_PASSWORD")
# print(f"Username is:{user}      Password is: {'*' * len(password)}")

# print("Attempting login....")
# loader.load_session_from_file(user.lower())
# print("Succesful Login!\n")

print("Loading User Names....")
with open("./form_responses.csv") as file:
    data = list(csv.DictReader(file))
print(f"Loaded {len(data)} Usernames\n")


print("------------------------------")
print("Unfollowed Private Accounts:")
with open("./my_follows.csv") as file:
    follows = list(csv.DictReader(file))
my_follows = [ row["Instagram Username"] for row in follows ]

private_accs = [ row["Instagram Username"] for row in data if row["Der angegeben Account ist Privat"] == "TRUE"]
unfollowed = []
for account in private_accs:
    if account not in my_follows:
        unfollowed.append(account)
for acc in unfollowed: print(acc)
print("------------------------------")

# profiles = set([ row["Instagram Username"] for row in data ])
# troll = []

# for profile in profiles:
#     if profile in unfollowed and profile != user:
#         continue
#     try:
#         profile = instaloader.Profile.from_username(loader.context, user)
        
#         if profile.followers >= 5000: 
#             troll.append(user) 
#             continue

#         followers = profile.get_followers()
#         for f in followers: print(f.username)
#     except instaloader.exceptions.ProfileNotExistsException:
#         troll.append(user)
