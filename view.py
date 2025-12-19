
#--------------------------------WITH SIMPLE UI-----------------------------------------------------------
from flask import Flask, render_template, request
from app import fetch_venue,sort_venues_by_dist,group_venues_by_sport,search_venues


app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    try:
        venues = fetch_venue()
        venues = sort_venues_by_dist(venues)

        grouped = group_venues_by_sport(venues)

        query = request.args.get("q", "").strip()
        sport = request.args.get("sport", "").strip()
        action = request.args.get("action")
        print(request.args)
        if action == "search" and query:
            venues = search_venues(venues, query)

        elif action == "filter" and sport:
            venues = grouped.get(sport, [])

        print("----",query,sport)
        return render_template(
            "index.html",
            venues=venues,
            grouped=grouped,
            query=query,
            selected_sport=sport
        )
    except Exception as e:
        print("Error occured:", e)
        return render_template(
            "index.html",
            venues=[],
            grouped={},
            query="",
            selected_sport=""
        )    


if __name__ == "__main__":
    app.run(debug=True)