import argparse

def greet(name, age):
    print(f"Hello {name}, you are {age} years old!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple CLI example.")
    parser.add_argument("name", type=str, help="Your name")
    parser.add_argument("age", type=int, help="Your age")
    
    args = parser.parse_args()
    greet(args.name, args.age)
