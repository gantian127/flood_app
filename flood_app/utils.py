"""
This is the utility file that includes functions used by the flood app

Source of mapping table values
mannings'n:
- USGS https://pubs.usgs.gov/wsp/2339/report.pdf

hydraulic conductivity:
- GREEN-AMPT INFILTRATION PARAMETERS. FROM SOILS DATA. By Walter J. Rawls et al. 1982
"""

import os
import json

import numpy as np
from landlab import RasterModelGrid
from landlab.components import FlowAccumulator, ChannelProfiler
from landlab.utils import get_watershed_mask

MANNING_MAPPING = {
    "unclassified": 0.03,
    "barrenland": 0.025,
    "openwater": 0.02,
    "vegetatedland": 0.05,
    "agricultural": 0.04,
    "road": 0.0175,  # from L-Grid model
    "building": 0.08,
    "berm_low": 0.03,
    "berm_high": 0.03,
    "mulch": 0.06,

}

CONDUCTIVITY_MAPPING = {
    "unclassified": 1e-7,  # default
    "barrenland": 2e-7,  # 5e-6？
    "openwater": 1e-10,  # low
    "vegetatedland": 1e-6,  # high  1e-5？
    "agricultural": 5e-7,  # 5e-6？
    "road": 1e-10,  # ignore
    "building": 1e-10,  # ignore
    "berm_low": 1e-7,
    "berm_high": 1e-7,
    "mulch": 1e-4,
}

LANDTYPE_MAPPING = {
    "unclassified": 1,
    "barrenland": 10,
    "openwater": 11,
    "vegetatedland": 12,
    "agricultural": 20,
    "road": 30,
    "building": 31,
    "berm_low": 50,
    "berm_high": 51,
    "mulch":60,
}


def create_ascii_files_from_geojson(
    dem_info,
    output_folder,
    geojson_str=False,
    delineation=False,
    intervention=False,
    no_data=-9999.0
):
    """
    create ASCII files for elevation with a given dem geojson

    :param dem_info: dem in UTM projection geojson file or json string
    :param output_folder: where to store the output file
    :param geojson_str: indicate whether the dem_info is as json str or a json file.
           If false, open the file and load the file content.
    :param delineation: indicate whether the input DEM needs watershed delineation.
           If ture, input DEM will be processed for watershed delineation
    :param intervention: indicate whether the input DEM needs watershed intervention
    :param no_data: indicate the cell that is outside the watershed.
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
    land_type = np.full([nrows, ncols], LANDTYPE_MAPPING["unclassified"])
    mannings_n = np.full([nrows, ncols], MANNING_MAPPING["unclassified"])
    conductivity = np.full([nrows, ncols], CONDUCTIVITY_MAPPING["unclassified"])

    # get data from geojson string
    for i in np.arange(0, node_numbers):
        y = features[i]["properties"]["x"]  # in json x represents col ind
        x = features[i]["properties"]["y"]  # in json y represents row ind

        # add elevation data
        elevation[x][y] = features[i]["properties"]["elevation"]

        # add land type data
        land_type_name = features[i]["properties"]["selectedLandType"]["name"]
        land_type[x][y] = LANDTYPE_MAPPING.get(
            land_type_name, LANDTYPE_MAPPING["unclassified"]
        )

        # add manning's n data
        mannings_n[x][y] = MANNING_MAPPING.get(
            land_type_name, MANNING_MAPPING["unclassified"]
        )

        # add hydraulic conductivity data
        conductivity[x][y] = CONDUCTIVITY_MAPPING.get(
            land_type_name, CONDUCTIVITY_MAPPING["unclassified"]
        )

        if intervention and len(features[i]["properties"]["tokens"])>0:
            intervention_type = features[i]["properties"]["tokens"][0].get("type", "")
            if intervention_type == "berm_low":
                land_type[x][y] = LANDTYPE_MAPPING["berm_low"]
                mannings_n[x][y] = MANNING_MAPPING["berm_low"]
                conductivity[x][y] = CONDUCTIVITY_MAPPING["berm_low"]
                elevation[x][y] = elevation[x][y] + 1  # add 1 meter elevation for berm
            elif intervention_type == "berm_high":
                land_type[x][y] = LANDTYPE_MAPPING["berm_high"]
                mannings_n[x][y] = MANNING_MAPPING["berm_high"]
                conductivity[x][y] = CONDUCTIVITY_MAPPING["berm_high"]
                elevation[x][y] = elevation[x][y] + 2  # add 2 meter elevation for berm
            elif intervention_type == "mulch":
                land_type[x][y] = LANDTYPE_MAPPING["mulch"]
                mannings_n[x][y] = MANNING_MAPPING["mulch"]
                conductivity[x][y] = CONDUCTIVITY_MAPPING["mulch"]

    # watershed delineation
    outlet_id = -1
    if delineation:
        elevation, outlet_id = watershed_delineation(
            elevation, cellsize, no_data=no_data
        )
    # mask nodata for land type, manning's n and conductivity data
    land_type[elevation == no_data] = no_data
    # mannings_n[elevation == no_data] = no_data
    # conductivity[elevation == no_data] = no_data  # need to be positive values as input file

    # define header info
    header = {
        "ncols": ncols,
        "nrows": nrows,
        "xllcorner": 0,
        "yllcorner": 0,
        "cellsize": cellsize,
        "nodata_value": no_data,
    }

    header_lines = [f"{key} {str(val)}" for key, val in list(header.items())]

    # save elevation data
    elev_path = os.path.join(output_folder, "elevation.txt")
    np.savetxt(
        elev_path,
        np.flipud(elevation),
        header=os.linesep.join(header_lines),
        comments="",
    )

    # save land type data
    land_type_path = os.path.join(output_folder, "land_type.txt")
    np.savetxt(
        land_type_path,
        np.flipud(land_type),
        header=os.linesep.join(header_lines),
        comments="",
        fmt="%d",
    )

    # save manning's n data
    mannings_n_path = os.path.join(output_folder, "mannings_n.txt")
    np.savetxt(
        mannings_n_path,
        np.flipud(mannings_n),
        header=os.linesep.join(header_lines),
        comments="",
        fmt="%.4f",
    )

    # save hydraulic conductivity data
    conductivity_path = os.path.join(output_folder, "conductivity.txt")
    np.savetxt(
        conductivity_path,
        np.flipud(conductivity),
        header=os.linesep.join(header_lines),
        comments="",
        fmt="%.4e",
    )

    return {
        "outlet_id": outlet_id,
        "elevation": elev_path,
        "land_type": land_type_path,
        "mannings_n": mannings_n_path,
        "conductivity": conductivity_path,
    }


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


def watershed_delineation(elevation, cell_size, no_data=-9999.0):
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

    return dem_field.reshape(grid_shape), outlet
