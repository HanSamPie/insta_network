import os
import instaloader

loader = instaloader.Instaloader()

user = os.getenv("INSTA_USER")
password = os.getenv("INSTA_PASSWORD")

print(f"Username is:{user}      Password is: {'*' * len(password)}")

print("Attempting login")
loader.load_session_from_file(user.lower())
print("Succesful Login!")

profile = instaloader.Profile.from_username(loader.context, user)
print("Follwers: ",profile.followers)
followers = profile.get_followers()
print("Followers2:",profile.followers)

for follower in followers: print(follower.username)