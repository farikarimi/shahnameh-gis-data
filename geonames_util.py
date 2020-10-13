import csv
import geocoder
from geojson import Feature, FeatureCollection, Point, dump

# In this Python script a GeoJSON file is constructed containing geographical
# and other information on the places from the Shahnameh text.
# Some of the English names, the coordinates and the Wikipedia links for the places
# are fetched from the GeoNames database using the Geocoder Python package.
# The GeoJSON is created using the geojson Python package.


def csv_as_list(path):
    """Reads the CSV file at the given path and returns the content as a list of rows."""
    with open(path, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        # Remove header
        next(reader, None)
        lst = list(reader)
    return lst


def get_all_fa_places(fa_path):
    """Gets the English names from the GeoNames database for the Persian place names from Wikipedia
    that don't yet have an English counterpart in place_names_en_da.csv."""
    # List of Persian place names from Wikipedia
    fa_csv_list = csv_as_list(fa_path)
    # For each Persian name
    for fa_name in [r[0] for r in fa_csv_list]:
        # Try to get a list of the (English) names found for the search term from the GeoNames database
        en_names_list = list(geocoder.geonames(fa_name, key='USERNAME', maxRows=10))
        # If the list is not empty
        if en_names_list:
            # print the Persian name and the English names for review.
            print(f'{fa_name}\n{en_names_list}')


def occurs_in_text(string):
    """Checks if the given string occurs in the Shahnameh text."""
    with open('data/frdvsi.txt', 'r') as shahnameh_file:
        shahnameh_txt = shahnameh_file.read()
    if string in shahnameh_txt:
        return True
    return False


def get_geo_places(path):
    """Creates and returns a list containing a dictionary for each place name from the CSV file at the given path."""
    # Create an empty list for the dictionaries
    places_dict_list = []
    # For each row in the CSV file
    for row in csv_as_list(path):
        # get the place from the GeoNames database that has the exact
        # same name as the English name in the CSV file (row[0])
        place = geocoder.geonames(row[0], name_equals=row[0], key='USERNAME')
        # If the Shahnameh text and the GeoNames database both contain the place name
        if occurs_in_text(row[1]) and place:
            # Fetch all available information on the place from the GeoNames database
            place = geocoder.geonames(place.geonames_id, method='details', key='USERNAME')
            # add a dictionary with
            places_dict_list.append({'name': row[0],    # the English name of the place,
                                     'name2': row[1],   # the Persian name of the place
                                     'lat': float(place.lat),   # the latitude of the place,
                                     'lng': float(place.lng),   # the longitude of the place to the list,
                                     'wikilink': place.wikipedia})  # and the Wikipedia link.
    # Return the list of dictionaries.
    return places_dict_list


def create_feat_collection(places_dict_list):
    """Creates a Feature Collection for the GeoJSON from the list of place dictionaries."""
    # Empty list is created for storing the features
    features_list = []
    # For each place in the given list
    for place in places_dict_list:
        # Create a Feature using the information in the dictionary
        feature = Feature(geometry=(Point((place['lng'],
                                           place['lat']))),
                          properties={'name': place['name'],
                                      'name2': place['name2'],
                                      'wikilink': place['wikilink']})
        # Add the feature to the list of features
        features_list.append(feature)
    # Convert the list of features into a Feature Collection and return it
    return FeatureCollection(features_list)


def save_feat_collection_to_file(feat_collection, path):
    """Saves the given Feature Collection in a (Geo)JSON file at the given path."""
    with open(file=path, mode='w', encoding='utf-8', ) as file:
        dump(feat_collection, file, ensure_ascii=False)


# The main method is executed when the Python script is run.
# The functions are called in the necessary order to create the GeoJSON file used in the web application.
if __name__ == '__main__':
    get_all_fa_places('data/wikipedia_place_names_fa.csv')
    places_list = get_geo_places('data/place_names_en_fa.csv')
    print(f'\n{len(places_list)} places')
    feature_collection = create_feat_collection(places_list)
    save_feat_collection_to_file(feature_collection, 'data/new_places.json')
