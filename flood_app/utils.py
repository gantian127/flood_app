"""
This is the utility file that includes functions used by the flood app
"""

import os
import json

import numpy as np
from landlab import RasterModelGrid
from landlab.components import FlowAccumulator, ChannelProfiler
from landlab.utils import get_watershed_mask


MANNING_MAPPING = {
    "building": 0.1,
    "imperviouscover": 0.2,
    "otherwater": 0.3,
    "permeable": 0.4,
    "road": 0.5,
    "unclassified": 0.6,
}


def create_ascii_files_from_geojson(
    dem_info, output_folder, geojson_str=False, delineation=False
):
    """
    create ASCII files for elevation with a given dem geojson

    :param dem_info: dem in UTM projection geojson file or json string
    :param output_folder: where to store the output file
    :param geojson_str: indicate whether the dem_info is as json str or a json file.
           If false, open the file and load the file content.
    :param delineation: indicate whether the input DEM needs watershed delineation.
           If ture, input DEM will be processed for watershed delineation
    :return: elevation.txt
    """
    if geojson_str:
        data = dem_info
    else:
        with open(dem_info, "r") as file:
            data = json.load(file)

    # get row, col and cell size info
    nrows = data["properties"]["verticalSquares"]  # vertical represents row numbers
    ncols = data["properties"]["horizontalSquares"]  # horizontal represents col numbers
    cellsize = data["properties"]["squareSize"]
    node_numbers = ncols * nrows

    # define empty arrays
    features = data["features"]
    elevation = np.empty([nrows, ncols])

    # get data from geojson string
    for i in np.arange(0, node_numbers):
        y = features[i]["properties"]["x"]  # in json x represents col ind
        x = features[i]["properties"]["y"]  # in json y represents row ind
        elevation[x][y] = features[i]["properties"]["elevation"]

    # define header info
    header = {
        "ncols": ncols,
        "nrows": nrows,
        "xllcorner": 0,
        "yllcorner": 0,
        "cellsize": cellsize,
        "nodata_value": -9999,
    }

    header_lines = [f"{key} {str(val)}" for key, val in list(header.items())]

    if delineation:
        elevation = watershed_delineation(elevation, cellsize)

    # save elevation data
    elev_path = os.path.join(output_folder, "elevation.txt")
    np.savetxt(
        elev_path,
        np.flipud(elevation),
        header=os.linesep.join(header_lines),
        comments="",
    )

    return elev_path


def create_ascii_files(dem_info, output_folder, json_str=False, delineation=False):
    """
    create ASCII files for elevation and manning's n with a given dem json file

    :param dem_info: dem json file or json string create by fora.ai platform
    :param output_folder: where to store the output file
    :param json_str: indicate whether the dem_info is as json str or a json file
    :param delineation: indicate whether the input DEM needs watershed delineation.
           If ture, input DEM will be processed for watershed delineation
    :return: the file path for elevation and manning's n file with file
             name as elevation.txt and mannings_n.txt
    """
    if json_str:
        data = dem_info
    else:
        with open(dem_info, "r") as file:
            data = json.load(file)[0]

    # get row, col and cell size info
    nrows = data["verticalSquares"]  # vertical represents row numbers
    ncols = data["horizontalSquares"]  # horizontal represents col numbers
    cellsize = round(111320 * data["squareSize"], 1)
    node_numbers = ncols * nrows

    # define empty arrays
    entity = data["entities"]
    elevation = np.empty([nrows, ncols])
    land_type = np.empty([nrows, ncols], dtype="<U15")

    # get data from json string
    for i in np.arange(0, node_numbers):
        y = entity[i]["metadata"]["colorResult"]["x"]  # in json x represents col ind
        x = entity[i]["metadata"]["colorResult"]["y"]  # in json y represents row ind
        elevation[x][y] = entity[i]["elevation"]
        land_type[x][y] = entity[i]["metadata"]["colorResult"]["colorData"][0]["name"]

    # define header info
    header = {
        "ncols": ncols,
        "nrows": nrows,
        "xllcorner": 0,
        "yllcorner": 0,
        "cellsize": cellsize,
        "nodata_value": -9999,
    }

    header_lines = [f"{key} {str(val)}" for key, val in list(header.items())]

    # refine elevation data
    elevation = np.where(land_type == "water", -9999, elevation)  # replace water area

    if delineation:
        elevation = watershed_delineation(elevation, cellsize)

    # save elevation data
    elev_path = os.path.join(output_folder, "elevation.txt")
    np.savetxt(
        elev_path,
        np.flipud(elevation),
        header=os.linesep.join(header_lines),
        comments="",
    )

    # create and save manning's n data
    replace_values = np.vectorize(MANNING_MAPPING.get)
    mannings_n = replace_values(land_type)

    mannings_n_path = os.path.join(output_folder, "mannings_n.txt")
    np.savetxt(
        mannings_n_path,
        np.flipud(mannings_n),
        header=os.linesep.join(header_lines),
        comments="",
    )

    return elev_path, mannings_n_path


def watershed_delineation(elevation, cell_size, no_data=-9999):
    """
    Conduct watershed delineation with the given elevation data.

    :param elevation: 2D array of DEM data.
    :param cell_size: the grid resolution of the 2D DEM data.
    :param no_data: nodata value for grid cells. The grid cells which are without the
           watershed will also be assigned as this value.
    :return: 2D array of DEM data which includes a delineated watershed
    """

    # define model grid and data field
    grid_shape = elevation.shape
    model_grid = RasterModelGrid(grid_shape, xy_spacing=cell_size)
    dem_field = model_grid.add_field(
        "topographic__elevation", elevation.astype("float")
    )
    model_grid.status_at_node[dem_field < 0] = (
        model_grid.BC_NODE_IS_CLOSED
    )  # water area

    # flow accumulation
    fa = FlowAccumulator(
        model_grid,
        method="Steepest",
        flow_director="FlowDirectorSteepest",
        depression_finder="LakeMapperBarnes",
        redirect_flow_steepest_descent=True,
        reaccumulate_flow=True,
    )
    fa.run_one_step()

    # set up channel profiler
    profiler = ChannelProfiler(model_grid, number_of_watersheds=1)
    profiler.run_one_step()

    # get watershed mask
    outlet = profiler.nodes[0][0]
    watershed_mask = get_watershed_mask(model_grid, outlet)

    # assign nodata to cells outside the watershed
    model_grid.at_node["topographic__elevation"][~watershed_mask] = no_data

    return dem_field.reshape(grid_shape)
