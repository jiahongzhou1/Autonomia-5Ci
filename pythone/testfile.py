import os

def clear_file(filepath):
  try:
    # Open the file in write mode ('w').
    # This truncates the file if it exists or creates it if it doesn't.
    # Using 'with' ensures the file is closed automatically.
    with open(filepath, 'w', encoding='utf-8') as f:
      pass # We don't need to write anything, just opening in 'w' clears it

    print(f"File '{filepath}' has been cleared.")
  except Exception as e:
    print(f"Error clearing file '{filepath}': {e}")

if __name__ == "__main__":
    clear_file("C:\\Users\\lol30\\Documents\\VSC\\Autonomia-5Ci\\pythone\\Saves\\asd.json")