#-------------------------------WITH CLI-----------------------------------------------------------
import requests
import os
from dotenv import load_dotenv
import redis
import json
load_dotenv()
API_URL = os.getenv("API_URL")

#redisss
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

CACHE_KEY = "venue_cache_calling"
CACHE_TTL = 300   

#---------fetching from api-----------
def fetch_venue():
    try:
        cached_data = redis_client.get(CACHE_KEY)

        if cached_data:
            print("dataa caching")
            return json.loads(cached_data)

        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        redis_client.setex(CACHE_KEY, CACHE_TTL, json.dumps(data))
        return data
    except requests.RequestException as e:
        print("Error fetching data:", e)
        return []
#pagination
def paginate_venues(venues, page, per_page=5):
    start = (page - 1) * per_page
    end = start + per_page
    return venues[start:end]

#-------sort based on km-------------------------
# def sort_venues_by_dist(venues):
#     return sorted(venues, key=lambda v: v["kilometres"])


# def favorite(venues):
# try:
# data= [item for item in venues if item.get("favourite") == 1]
# return data
# except Exception as e:
# print("Error occured:", e)
# return venues

# def filter_by_distance(venues, km):
# return [v for v in venues if v.get("kilometres", 0) <= km]
# import json

# def save_favourites(favs):
# with open("favs.json","w") as f:
# json.dump(favs, f, indent=4)
#sort by rating then distance
def sort_venues_by_rating_and_dist(venues):
    try:
        if len(venues) <= 1:
            return venues
        center = venues[len(venues) // 2]
        pivot_rating = center["rating"]
        pivot_dist = center["kilometres"]
        # print("-------",pivot_rating)
        # print("-------",pivot_dist)
        left = []
        middle = []
        right = []

        for v in venues:
            if v["rating"] > pivot_rating:
                left.append(v)

            elif v["rating"] == pivot_rating:
                if v["kilometres"] < pivot_dist:
                    left.append(v)
                elif v["kilometres"] > pivot_dist:
                    right.append(v)
                else:
                    middle.append(v)
            else:
                right.append(v)

        return (
            sort_venues_by_rating_and_dist(left)
            + middle
            + sort_venues_by_rating_and_dist(right)
        )

    except Exception as e:
        print("Error occurred:", e)
        return venues

def sort_venues_by_dist(venues):
    try:
        if len(venues) <= 1:
            return venues

        center = venues[len(venues) // 2]["kilometres"]

        left = [v for v in venues if v["kilometres"] < center]
        middle = [v for v in venues if v["kilometres"] == center]
        right = [v for v in venues if v["kilometres"] > center]

        return sort_venues_by_dist(left) + middle + sort_venues_by_dist(right)
    except Exception as e:
        print("Error occured:", e)
        return venues    

#-------group by sport---------------------
def group_venues_by_sport(venues):
    try:
        grouped = {}

        for venue in venues:
            for sport in venue["sports"]:
                if sport not in grouped:
                    grouped[sport] = []
                grouped[sport].append(venue)

        return grouped
    except Exception as e:
        print("Error occured:", e)
        return venues     

#-----------manual search------------------------
def search_venues(venues, query):
    try:
        query = query.lower()
        results = []

        for venue in venues:
            name = venue.get("name", "").lower()
            # address = venue.get("address", "").lower()
            sports = " ".join(venue.get("sports", [])).lower()

            if query in name or query in sports:
                results.append(venue)

        return results
    except Exception as e:
        print("Error occured:", e)
        return venues     



#-------common display-------------------    
def display(venues):
    if not venues:
        print("No venues to display")
        return "______"

    for venue in venues:
        print("=" * 70)
        print(f"Venue Name : {venue.get('name','')}")
        print(f"Distance   : {venue.get('kilometres','0.0')}")
        print(f"Sports     : {' , '.join(venue.get('sports', []))}")
        print(f"Rating     : {venue.get('rating','0.0')}")
        print(f"Address    : {venue.get('address','')}")
    print("=" * 70)




def main():
    venues = fetch_venue()
    # sort_venues=sort_venues_by_dist(venues)
    sort_venues=sort_venues_by_rating_and_dist(venues)
    grouped_venues = group_venues_by_sport(sort_venues)
    while True:
        print("-------- Sports Venues -------------")
        print("1. View all venues (sorted by rating/distance)")
        print("2. Group by sport")
        print("3. Search ")
        print("4. Price range filter ")
        print("5. Price filter ")
        print("6. Exit")

        choice = input("Choose an option: ").strip()
        if choice=="1":
            page=input("Enter Page number: ").strip()
            page_num=int(page)
            paginated = paginate_venues(sort_venues, page_num)
            display(paginated)
        elif choice=="2":
            # print(grouped_venues)
            print("Available sports:")
            for sport in grouped_venues.keys():
                print(f"- {sport}")
            search = input("Enter sport name: ").strip().lower()
            venues_by_sport = grouped_venues.get(search.capitalize())

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
            print("Available sports:")
            for sport in grouped_venues.keys():
                print(f"- {sport}")
            sport_name = input("Enter sport name: ").strip()
            start=int(input("Enter price start range: ").strip())
            stop=int(input("Enter price end range: ").strip())
            print(start,stop)
            
            venues = [
                v for v in sort_venues
                if v["price"].get(sport_name, 0) >= start and v["price"].get(sport_name, 0) <= stop
            ]
            display(venues) 
        elif choice=="5": 
            print("Available sports:")
            for sport in grouped_venues.keys():
                print(f"- {sport}")
            sport_name = input("Enter sport name: ").strip().lower()  
            start_range=int(input("Enter price of your convinience: ").strip()) 
            venues = [
                v for v in sort_venues
                if sport_name.capitalize() in v.get("price", {})
                and v["price"][sport_name.capitalize()] <= start_range
            ]
            display(venues)

        elif choice=="6":  
            print("EXIT")
            break    
        else:
            print("Invalid")          
   
if __name__ == "__main__":
    main()
