import numpy as np
from ease_lonlat import EASE2GRID

### EASE2 grid generator ###
def get_e2_grid(resolution_key):
    # Map both 'M36' and '36km' (or similar) to the corresponding grid parameters
    resolution_map = {
        'M01': '1km', '1km': '1km',
        'M03': '3km', '3km': '3km',
        'M03.125': '3.125km', '3.125km': '3.125km',
        'M06.25': '6.25km', '6.25km': '6.25km',
        'M09': '9km', '9km': '9km',
        'M12.5': '12.5km', '12.5km': '12.5km',
        'M25': '25km', '25km': '25km',
        'M36': '36km', '36km': '36km'
    }

    # Translate the resolution_key to the corresponding key in e2_grid_params
    grid_key = resolution_map.get(resolution_key)

    if not grid_key:
        raise ValueError(f"Unsupported resolution key: {resolution_key}")

    # Dictionary with grid parameters
    e2_grid_params = {
        '1km': {'epsg': 6933, 'x_min': -17367530.44, 'y_max': 7314540.83, 'res': 1000.9, 'n_cols': 34704, 'n_rows': 14616},
        '3km': {'epsg': 6933, 'x_min': -17367530.44, 'y_max': 7314540.83, 'res': 3002.69, 'n_cols': 11568, 'n_rows': 4872},
        '3.125km': {'epsg': 6933, 'x_min': -17367530.44, 'y_max': 7307375.92, 'res': 3128.16, 'n_cols': 11104, 'n_rows': 4672},
        '6.25km': {'epsg': 6933, 'x_min': -17367530.44, 'y_max': 7307375.92, 'res': 6256.32, 'n_cols': 5552, 'n_rows': 2336},
        '9km': {'epsg': 6933, 'x_min': -17367530.44, 'y_max': 7314540.83, 'res': 9008.05, 'n_cols': 3856, 'n_rows': 1624},
        '12.5km': {'epsg': 6933, 'x_min': -17367530.44, 'y_max': 7307375.92, 'res': 12512.63, 'n_cols': 2776, 'n_rows': 1168},
        '25km': {'epsg': 6933, 'x_min': -17367530.44, 'y_max': 7307375.92, 'res': 25025.26, 'n_cols': 1388, 'n_rows': 584},
        '36km': {'epsg': 6933, 'x_min': -17367530.44, 'y_max': 7314540.83, 'res': 36032.22, 'n_cols': 964, 'n_rows': 406}
    }

    # Retrieve the grid parameters based on the mapped key
    grid_params = e2_grid_params[grid_key]

    # Initialize the EASE2GRID with the specified parameters
    grid = EASE2GRID(
        name=f'EASE2_G{grid_key.replace("km", "")}',
        epsg=grid_params['epsg'],
        x_min=grid_params['x_min'],
        y_max=grid_params['y_max'],
        res=grid_params['res'],
        n_cols=grid_params['n_cols'],
        n_rows=grid_params['n_rows']
    )
    return grid

def generate_lon_lat_e2grid(resolution_key):
    # Initialize the grid using the previous function
    grid = get_e2_grid(resolution_key)

    # Determine the number of columns and rows from the grid
    n_cols = grid.n_cols
    n_rows = grid.n_rows

    # Create empty arrays to store latitude and longitude
    latitudes = np.zeros((n_rows, n_cols))
    longitudes = np.zeros((n_rows, n_cols))

    # Iterate over each cell in the grid
    for row in range(n_rows):
        for col in range(n_cols):
            lon, lat = grid.rc2lonlat(col, row)
            longitudes[row, col] = lon
            latitudes[row, col] = lat

        # Optionally print progress
        if row % 100 == 0:
            print(f"Processing row {row}/{n_rows}")

    return longitudes, latitudes

### ----------------------------------------------- ###
def generate_lon_lat_eqdgrid(*args, bounds=[]):
    """
    Generates 2D arrays of latitudes and longitudes. The function can either take a single argument specifying the 
    resolution in degrees or two arguments specifying the number of latitude and longitude points.

    Args:
    *args: Variable length argument list. Can be either a single float indicating resolution in degrees, or two
           integers indicating the number of latitude and longitude points (grid rows and columns).
    bounds: List of cropped bounds. (e.g., bounds = [125.7, 129.7, 33.9, 38.8] # entire Korea)
    
    Returns:
    tuple: Two 2D numpy arrays containing the latitude and longitude values respectively.
    """
    if len(args) == 1:
        # Assume single argument is the resolution in degrees
        resolution = args[0]
        y_dim = int(180 / resolution)
        x_dim = int(360 / resolution)
    elif len(args) == 2:
        # Two arguments specifying the grid dimensions
        y_dim, x_dim = args
    else:
        raise ValueError("Invalid number of arguments. Provide either resolution or dimensions.")

    # Calculate the size of each pixel
    lat_step = 180 / y_dim
    lon_step = 360 / x_dim

    # Calculate latitude and longitude values starting from the center of the first pixel
    latitudes = np.linspace(90 - lat_step / 2, -90 + lat_step / 2, y_dim)
    longitudes = np.linspace(-180 + lon_step / 2, 180 - lon_step / 2, x_dim)

    # Crop latitude and longitude for bound area
    if bounds != []:
        lon_crop = (longitudes > bounds[0]) & (longitudes < bounds[1])
        lat_crop = (latitudes > bounds[2]) & (latitudes < bounds[3])

        lon_indices = np.where(lon_crop)[0]
        lat_indices = np.where(lat_crop)[0]

        min_lon, max_lon = lon_indices.min(), lon_indices.max()
        min_lat, max_lat = lat_indices.min(), lat_indices.max()
        
        # Crop lat, lon, data
        longitudes = longitudes[min_lon:max_lon+1]
        latitudes = latitudes[min_lat:max_lat+1]
    
    # Mesh the latitude and longitude values to create 2D arrays
    lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)
    return lon_grid, lat_grid

# Example usage
#y_dim = 3600  # Number of latitude points
#x_dim = 7200  # Number of longitude points
#lat_grid, lon_grid = create_geo_grid(y_dim, x_dim)
#lat_grid, lon_grid = create_geo_grid('0.05')
#domain_lon, domain_lat = generate_lon_lat_eqdgrid(0.01, bounds=[125.7, 129.7, 33.9, 38.8]) # 1km resolution & entire Korea
