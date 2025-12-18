import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")


#---------fetching from api-----------
def fetch_venue():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Error fetching data:", e)
        return []


#-------sort based on km-------------------------
# def sort_venues_by_dist(venues):
#     return sorted(venues, key=lambda v: v["kilometres"])
def sort_venues_by_dist(venues):
    if len(venues) <= 1:
        return venues

    center = venues[len(venues) // 2]["kilometres"]

    left = [v for v in venues if v["kilometres"] < center]
    middle = [v for v in venues if v["kilometres"] == center]
    right = [v for v in venues if v["kilometres"] > center]

    return sort_venues_by_dist(left) + middle + sort_venues_by_dist(right)

#-------group by sport---------------------
def group_venues_by_sport(venues):
    grouped = {}

    for venue in venues:
        for sport in venue["sports"]:
            if sport not in grouped:
                grouped[sport] = []
            grouped[sport].append(venue)

    return grouped

#-----------manual search------------------------
def search_venues(venues, query):
    query = query.lower()
    results = []

    for venue in venues:
        name = venue.get("name", "").lower()
        # address = venue.get("address", "").lower()
        sports = " ".join(venue.get("sports", [])).lower()

        if query in name or query in sports:
            results.append(venue)

    return results



#-------common display-------------------    
def display(venues):
    if not venues:
        print("No venues to display")
        return "______"

    for venue in venues:
        print("=" * 70)
        # print(f"Venue Name : {venue.get('name')}")
        print(f"Venue Name : {venue.get('name','')}")
        print(f"Distance   : {venue.get('kilometres','0.0')}")
        print(f"Sports     : {' , '.join(venue.get('sports', []))}")
        print(f"Rating     : {venue.get('rating','0.0')}")
        print(f"Address    : {venue.get('address','')}")
    print("=" * 70)




def main():
    venues = fetch_venue()
    sort_venues=sort_venues_by_dist(venues)
    grouped_venues = group_venues_by_sport(venues)
    # print(f"Total venues: {len(venues)}")
    # sorted_venues = sort_venues_by_dist(venues)
    # print("sorted_venues----",sorted_venues)
    # group=group_venues_by_sport(venues)
    # print("group---",group)
    while True:
        print("-------- Sports Venues -------------")
        print("1. View all venues (sorted by distance)")
        print("2. Group by sport")
        print("3. Search ")
        print("4. Exit")

        choice = input("Choose an option: ").strip()
        if choice=="1":
            display(sort_venues)
        elif choice=="2":
            # print(grouped_venues)
            print("Available sports:")
            for sport in grouped_venues.keys():
                print(f"- {sport}")
            search = input("Enter sport name: ").strip()
            venues_by_sport = grouped_venues.get(search)

            if not venues_by_sport:
                print("No venues found...")
            else:
                display(venues_by_sport) 
        elif choice=="3":
            search = input("Search: ").strip()
            data=search_venues(venues,search)
            if data:
                display(data) 
            else:
                print("not found")
        elif choice=="4":  
            print("EXIT")
            break    
        else:
            print("Invalid")          







    
if __name__ == "__main__":
    main()
