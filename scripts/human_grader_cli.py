import json
import os

def run_grading():
    print("Welcome to the TripWire Human Grading CLI!")
    print("You will grade AmazonHelp responses on a scale of 1 to 5.")
    print("1 = Terrible, 5 = Perfect")
    print("Type 0 if you want to SKIP a tweet (e.g., if it's in a language you don't read).\n")
    
    with open("data/human_annotations.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for i, item in enumerate(data):
        if item.get("human_groundedness") is not None and item.get("human_groundedness") > 0:
            continue
            
        print("-" * 50)
        print(f"[{i+1}/{len(data)}] Customer Tweet: {item['customer_text']}")
        print(f"        Draft Reply : {item['draft_reply_to_judge']}")
        print("-" * 50)
        
        while True:
            try:
                g = int(input("Groundedness (1-5, or 0 to skip)? "))
                if 0 <= g <= 5: break
            except ValueError: pass
            print("Please enter a number between 0 and 5.")
            
        if g == 0:
            item["human_groundedness"] = 0
            item["human_actionability"] = 0
            item["human_tone"] = 0
        else:
            while True:
                try:
                    a = int(input("Actionability (1-5)? "))
                    if 1 <= a <= 5: break
                except ValueError: pass
                
            while True:
                try:
                    t = int(input("Tone (1-5)? "))
                    if 1 <= t <= 5: break
                except ValueError: pass
                
            item["human_groundedness"] = g
            item["human_actionability"] = a
            item["human_tone"] = t
            
        with open("data/human_annotations.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    print("\nThank you! Grading is complete.")
    
if __name__ == "__main__":
    run_grading()
