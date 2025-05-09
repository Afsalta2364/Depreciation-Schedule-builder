GAAP_USEFUL_LIVES = {
    "US GAAP": {
        "Building": 40,
        "Vehicle": 5,
        "Machinery": 10,
        "Furniture": 7
    },
    "IFRS": {
        "Building": 30,
        "Vehicle": 7,
        "Machinery": 8,
        "Furniture": 5
    }
}

def get_useful_life(gaap, asset_type):
    return GAAP_USEFUL_LIVES.get(gaap, {}).get(asset_type, None)
