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
print("Unfollowed Private Accounts:")
my_profile = instaloader.Profile.from_username(loader.context, user)
my_follows = [ profile.username for profile in my_profile.get_followees()]
private_accs = [ row["Instagram Username"] for row in data if row["Der angegeben Account ist Privat"] == "TRUE"]
unfollowed = set(my_follows) - set(private_accs)
for acc in unfollowed: print(acc)
print("------------------------------")

profiles = set([ row["Instagram Username"] for row in data ])
troll = []

for user in profiles:
    try:
        profile = instaloader.Profile.from_username(loader.context, user)
        
        if profile.followers >= 5000: 
            troll.append(user) 
            continue

        followers = profile.get_followers()
        for f in followers: print(f.username)
    except instaloader.exceptions.ProfileNotExistsException:
        troll.append(user)

