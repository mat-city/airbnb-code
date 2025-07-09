import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.distance import geodesic
import pandas as pd
import numpy as np
import joblib
# Load the model
with open("best_airbnb_model_more_featuresV4.pkl", "rb") as f:
    model = joblib.load(f)

def filter_attributes(attributes: dict): 
    #filter out values/attributes which are not used by the model to calculate the price
    model_keys = ["n_bathrooms", "n_guest", "n_bedrooms", "n_beds", "is_near_all_sights", "room_density", "location_rating",
                  "amenity_luxury_items", "amenity_tv", "amenity_coffee", "rating", "distance_city_center", "distance_to_acropolis", "distance_to_stadium"]
    return {key: attributes[key] for key in model_keys if key in attributes}

def set_default_values(attributes: dict):
    if "n_bathrooms" in attributes.keys():
        attributes["n_bathrooms"] = 2
    if "n_guest" in attributes.keys():
        attributes["n_guest"] = 2
    if "n_bedrooms" in attributes.keys():
        attributes["n_bedrooms"] = 2
    if "n_beds" in attributes.keys():
        attributes["n_beds"] = 2
    if "is_near_all_sights" in attributes.keys():
        attributes["is_near_all_sights"] = 1
    if "room_density" in attributes.keys():
        attributes["room_density"] = 2/3 #TODO take default values of n_guest and n_bedrooms only if they are both not defined
    if "location_rating" in attributes.keys():
        attributes["location_rating"] = 4
    if "amenity_luxury_items" in attributes.keys():
        attributes["amenity_luxury_items"] = 1
    if "amenity_tv" in attributes.keys():
        attributes["amenity_tv"] = 1
    if "amenity_coffee" in attributes.keys():
        attributes["amenity_coffee"] = 1
    if "rating" in attributes.keys():
        attributes["rating"] = 4
    if "distance_city_center" in attributes.keys():
        attributes["distance_city_center"] = 1
    if "distance_to_acropolis" in attributes.keys():
        attributes["distance_to_acropolis"] = 1
    if "distance_to_stadium" in attributes.keys():
        attributes["distance_to_stadium"] = 1
    return attributes

def initialize_model_input(session_state: dict, default_attributes: dict):
    input = {
    "n_bathrooms": session_state.n_bathrooms if session_state.n_bathrooms else default_attributes["n_bathrooms"],
    "n_guest": session_state.n_guest if session_state.n_guest else default_attributes["n_guest"],
    "n_bedrooms": session_state.n_bedrooms if session_state.n_bedrooms else default_attributes["n_bedrooms"],
    "n_beds": session_state.n_beds if session_state.n_beds else default_attributes["n_beds"],
    "is_near_all_sights": session_state.is_near_all_sights if session_state.is_near_all_sights is not None else default_attributes["is_near_all_sights"],
    "amenity_luxury_items": session_state.amenity_luxury_items if session_state.amenity_luxury_items is not None else default_attributes["amenity_luxury_items"], 
    "room_density": session_state.room_density if session_state.room_density else default_attributes["room_density"], 
    "location_rating": session_state.location_rating if session_state.location_rating else default_attributes["location_rating"], 
    "amenity_tv": session_state.amenity_tv if session_state.amenity_tv is not None else default_attributes["amenity_tv"], 
    "amenity_coffee": session_state.amenity_coffee if session_state.amenity_coffee is not None else default_attributes["amenity_coffee"], 
    "rating": session_state.rating if session_state.rating else default_attributes["rating"], 
    "distance_city_center": session_state.distance_city_center if session_state.distance_city_center else default_attributes["distance_city_center"], 
    "distance_to_acropolis": session_state.distance_to_acropolis if session_state.distance_to_acropolis else default_attributes["distance_to_acropolis"], 
    "distance_to_stadium": session_state.distance_to_stadium if session_state.distance_to_stadium else default_attributes["distance_to_stadium"]
    }
    return input

# Streamlit setup
st.page_title = "Price Prediction Service for Airbnb Listings"
st.set_page_config(layout="wide", page_title=st.page_title)
st.markdown(
    """
<style>
.small-font {
    font-size:10px !important;
}
/* Custom CSS for reducing input field size */
.streamlit-input {
    height: 10px;
    font-size: 6px;
}
/* Adjust padding inside the form */
.stForm > div {
    padding: 2px !important;
}
</style>
""",
    unsafe_allow_html=True,
)
st.title(st.page_title)

#user role selection: Host/Guest
# Initialize role in session state
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# Only show role selection if no role chosen yet
if st.session_state.user_role is None:
    st.title("Who are you?")
    role = st.radio("Select Your Role", ["Host", "Guest"])
    if st.button("Confirm Role"):
        st.session_state.user_role = role
        st.rerun()

else: 
    if st.button("Change Role"):
        for key in st.session_state.keys():
            st.session_state[key] = None
        st.rerun()
        
    if st.session_state.user_role=="Guest": 
        st.write("Use this webapp to plan your next holiday!")
    else:
        st.write("Use this webapp to get prices for your new listing!")
        
    if "start_date" not in st.session_state:
        st.session_state.start_date = None
    if "end_date" not in st.session_state:
        st.session_state.end_date = None
    if "distance_city_center" not in st.session_state:
        st.session_state.distance_city_center = None
    if "distance_to_acropolis" not in st.session_state:
        st.session_state.distance_to_acropolis = None
    if "distance_to_stadium" not in st.session_state:
        st.session_state.distance_to_stadium = None

    left_column, right_column = st.columns(2)
    with left_column:
        st.session_state.n_guest = st.number_input("Guests", value=None, min_value=1, max_value=15)
        st.session_state.n_bedrooms = st.number_input("Bedrooms", value=None, min_value=1, max_value=15)
        st.session_state.n_beds = st.number_input("Beds", value=None, min_value=1, max_value=15)
        st.session_state.n_bathrooms = st.number_input("Bathrooms", value=None, min_value=1, max_value=5)
        st.session_state.property_type = st.selectbox("Property Type", options=["Entire rental unit", "Entire condo", "Private room in rental unit", "Tiny home", "Entire villa", "Other"])
        if st.session_state.user_role=="Guest": 
            st.session_state.start_date = st.date_input("Check in Date", value=None, format="DD/MM/YYYY")
            st.session_state.end_date = st.date_input("Check out Date", value=None, format="DD/MM/YYYY")
        else:
            st.session_state.start_date = "some shit"
            st.session_state.end_date = "some other shit"
            
    with right_column:
        st.session_state.city = st.selectbox("Location", options=["Athen", "Barcelona"])
        with st.popover("Select Location"):
            # Default center: Athens
            athens_coords = [37.9838, 23.7275]

            # Create Folium Map with OpenStreetMap tiles (English labels)
            m = folium.Map(location=athens_coords, zoom_start=12, tiles='OpenStreetMap')
            # Add predefined markers
            points_of_interest = {
                "Acropolis": [37.9715, 23.7257],
                "City Center": [37.9755, 23.7348],
                "Panathenaic Stadium": [37.9680, 23.7416]
            }

            for name, coords in points_of_interest.items():
                folium.Marker(
                    location=coords,
                    popup=name,
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
            # Enable clicking to get lat/lon
            m.add_child(folium.LatLngPopup())

            # Render map in Streamlit
            st.markdown("### Click on the map to select your preferred location")
            map_data = st_folium(m, width=700, height=500)
            # Display clicked coordinates
            if map_data and map_data.get("last_clicked"):
                st.session_state.selected_location = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
                st.session_state.distance_city_center = geodesic(st.session_state.selected_location, points_of_interest["City Center"]).km
                st.session_state.distance_to_acropolis = geodesic(st.session_state.selected_location, points_of_interest["Acropolis"]).km
                st.session_state.distance_to_stadium = geodesic(st.session_state.selected_location, points_of_interest["Panathenaic Stadium"]).km
        if st.session_state.get("selected_location"):
            st.markdown(f"Selected Location: {st.session_state.selected_location}")     
            st.markdown(f"Distance to city center: {round(st.session_state.distance_city_center,2)} km")   
            st.markdown(f"Distance to city center: {round(st.session_state.distance_to_acropolis,2)} km")   
            st.markdown(f"Distance to city center: {round(st.session_state.distance_to_stadium,2)} km")   

        st.session_state.amenities = st.multiselect("Amenities", options=["Luxury Items", "TV", "Coffee", "Streaming Services", "WiFi", "Sound System", "Refrigerator", "Housekeeping", "Cooking Place", "Hygiene Products"])
        st.session_state.rating = st.number_input("Star Rating ⭐⭐⭐⭐⭐", value=None, min_value=0.1, max_value=5.0, step=0.1)
        st.session_state.location_rating = st.number_input("Star Rating ⭐⭐⭐⭐⭐ of the Location", value=None, min_value=0.1, max_value=5.0, step=0.1)

    def calculate_price(session_state: dict): 
        #calculate more features
        #TODO change the engineering of room_density, why would you do n_bedrooms + 1?
        try: session_state.room_density = session_state.n_guest / (session_state.n_bedrooms + 1)
        except: session_state.room_density = None 
        try:
            if (
            (session_state.distance_to_acropolis < 2) and
            (session_state.distance_city_center < 2) and
            (session_state.distance_to_stadium < 2)):
                session_state.is_near_all_sights = 1 
            else:
                session_state.is_near_all_sights = 0
            print(f"is_near_all_sights: {session_state.is_near_all_sights}")
        except: 
            session_state.is_near_all_sights = None
        
        #amenities
        if session_state.amenities!=[]:
            st.session_state.amenity_luxury_items = 1 if "Luxury Items" in st.session_state.amenities else 0
            st.session_state.amenity_tv = 1 if "TV" in st.session_state.amenities else 0
            st.session_state.amenity_coffee = 1 if "Coffee" in st.session_state.amenities else 0
        else:
            (session_state.amenity_luxury_items, session_state.amenity_tv, session_state.amenity_coffee) = (None, None, None)
        #total days
        try: n_days = (session_state.end_date - session_state.start_date).days
        except: n_days = None
        
        if sum(1 for value in session_state.values() if value is None) > 0:
            print(f"session state: {session_state}")
            # st.write(f"Prices for the missing attributes will be calculated, given the following attributes: {[key for key in session_state.keys() if session_state[key]!=None and session_state[key]!=[]]}")
            missing_attributes = {key: session_state[key] for key in session_state.keys() if session_state[key]==None or session_state[key]==[]}
            filtered_missing_attributes = filter_attributes(missing_attributes)
            #set default value for missing attributes
            default_attributes = set_default_values(filtered_missing_attributes)
            print(f"missing_attributes: {missing_attributes}")
            print(f"default_attributes: {default_attributes}")
            
            # st.write(f"The missing attributes being used and their default values are: {default_attributes}")
            with st.spinner(f"Calculating"):
                #calculate price prediction for missing values
                with st.expander(f"**Prices regarding missing values**", expanded=False):
                    all_prices = []
                    model_input = initialize_model_input(session_state, default_attributes)
                    print(f"model_input: {model_input}")
                    for key in filtered_missing_attributes.keys():
                        st.write(f"*Prices for different values of {key}*")
                        data = {}
                        if key in ["n_bathrooms", "n_guest", "n_bedrooms", "n_beds"]:
                            old_value = model_input[key]
                            for i in range(1,5):
                                model_input[key] = i
                                converted_model_input = [[value for value in model_input.values()]]
                                price = np.expm1(model.predict(converted_model_input)[0])
                                # st.write(f"Input: {converted_model_input}")
                                # st.write(f"Output: {price}")
                                # st.write("------------------")
                                data[i] = price
                                all_prices.append(price)
                            model_input[key] = old_value
                        
                        elif key in ["room_density"]:
                            for i in [1, 2, 3, 4]:
                                model_input[key] = i
                                converted_model_input = [[value for value in model_input.values()]]
                                price = np.expm1(model.predict(converted_model_input)[0])
                                data[i] = price
                                # st.write(f"Input: {converted_model_input}")
                                # st.write(f"Output: {price}")
                                # st.write("------------------")
                                all_prices.append(price)
                                
                        elif key in ["location_rating", "rating"]:
                            for i in range(2,6):
                                model_input[key] = i
                                converted_model_input = [[value for value in model_input.values()]]
                                price = np.expm1(model.predict(converted_model_input)[0])
                                data[i] = price
                                # st.write(f"Input: {converted_model_input}")
                                # st.write(f"Output: {price}")
                                # st.write("------------------")
                                all_prices.append(price)
                        
                        elif key in ["distance_city_center", "distance_to_acropolis", "distance_to_stadium"]:
                            for i in [0.5, 1, 1.5, 2]:
                                model_input[key] = i
                                converted_model_input = [[value for value in model_input.values()]]
                                price = np.expm1(model.predict(converted_model_input)[0])
                                data[i] = price
                                # st.write(f"Input: {converted_model_input}")
                                # st.write(f"Output: {price}")
                                # st.write("------------------")
                                all_prices.append(price)
                        elif key in ["is_near_all_sights", "amenity_luxury_items", "amenity_tv", "amenity_coffee"]:
                            for i in [0,1]:
                                model_input[key] = i
                                converted_model_input = [[value for value in model_input.values()]]
                                price = np.expm1(model.predict(converted_model_input)[0])
                                data[i] = price
                                # st.write(f"Input: {converted_model_input}")
                                # st.write(f"Output: {price}")
                                # st.write("------------------")
                                all_prices.append(price)
                                
                        dataframe = pd.DataFrame(data=data.values(),index=data.keys())
                        st.bar_chart(dataframe, x_label=key, y_label="Average Price per night")
                        #st.bar_chart(chart_data, x_label="Amount of Guests", y_label="Average Price per night")
                if st.session_state.user_role=="Guest": 
                    st.success(f"You can expected a price from **{round(min(all_prices),2)}**💲 to **{round(max(all_prices),2)}**💲 per Night{f' or **{round(n_days*min(all_prices),2)}**💲 to **{round(n_days*max(all_prices),2)}**💲 in total' if n_days else ''}.", icon="🔥")
                else:
                    st.success(f"The recommended price for your new listing ranges from **{round(min(all_prices),2)}**💲 to **{round(max(all_prices),2)}**💲 per Night{f' or **{round(n_days*min(all_prices),2)}**💲 to **{round(n_days*max(all_prices),2)}**💲 in total' if n_days else ''}.", icon="🔥")
                return True
        else: 
            # Example prediction: 1: bathrooms, 2: accommodates, 3: bedrooms, 4: beds, 5: review_scores_location, 
            # 6: amenity_luxury_items, 7: review_scores_rating, 8: distance_to_center, 9: distance_to_acropolis, 10: distance_to_stadium
            model_input = initialize_model_input(session_state, [])
            converted_model_input = [[value for value in model_input.values()]]
            y_pred = np.expm1(model.predict(converted_model_input)[0])
            if st.session_state.user_role=="Guest": 
                st.success(f"You can expected a price of **{round(y_pred,2)}**💲 per Night{f' or **{round(n_days*y_pred,2)}**💲 in total' if n_days else ''}.", icon="🔥")
            else:
                st.success(f"The recommended price for your new listing is **{round(y_pred,2)}**💲 per Night{f' or **{round(n_days*y_pred,2)}**💲 in total' if n_days else ''}.", icon="🔥")
            return False

        
    if st.button("Calculate my Price", use_container_width=True):
        missing_fields = calculate_price(st.session_state)
        
