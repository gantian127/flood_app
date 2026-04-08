"""
Evaluation (Tian Gan, 2025 Sept)

Description:
This code is for the participatory modeling project.
It includes the ModelEvaluation class to evaluate the model performance
with the model results

"""

import os
import rasterio
from .utils import calculate_npv

# folder = (
#   "/Users/tiga7385/Desktop/flood_app/user_upload/9f144dc1-25a6-484f-91d0-42ddb0ef75b9"
# )
# land_type_path = os.path.join(folder, "land_type.txt")
# max_water_depth_path = os.path.join(folder, "output", "max_water_depth.asc")
# cum_result_path = os.path.join(folder, "output", "cum_result_test.txt")
# infil_result_path = os.path.join(folder, "output", "infil_result.txt")
# output_folder = os.path.join(folder, "output")


class ModelEvaluation:
    LAND_TYPE = {
        "streets": 30,
        "houses": 31,
        "agricultural": 20,
        "berm_low": 50,
        "berm_high": 51,
        "mulch": 60,
    }

    def __init__(
        self,
        land_type_path,
        max_water_depth_path,
        cum_result_path,
        infil_result_path,
        output_folder,
        cell_size=50,
        no_data=-9999,
    ):
        with rasterio.open(land_type_path) as src:
            self.land_type = src.read(1)
        with rasterio.open(max_water_depth_path) as src:
            self.max_water_depth = src.read(1)
        with open(cum_result_path, "r") as f:
            first_line = f.readline().strip()
            self.cum_result = float(first_line.split(" ")[0])
        with open(infil_result_path, "r") as f:
            first_line = f.readline().strip()
            self.infil_result = float(first_line.split(" ")[0])
        self.output_dir = output_folder
        self.cell_area = cell_size**2
        self.cell_size = cell_size
        self.no_data = no_data

    def evaluate(self):
        # get evaluation results
        (
            max_flooded_area_percentage,
            flooded_streets_percentage,
            damage_cost_infrastructure,
            damage_cost_agricultural,
        ) = self.calc_flood_area_and_cost()

        (
            investment,
            mulching_investment,
            berm1_investment,
            berm2_investment,
        ) = self.calc_investment()  # TODO: only keep investment in the future

        # write results as a text file
        eval_result_path = os.path.join(self.output_dir, "evaluation_results.txt")
        with open(eval_result_path, "w") as f:
            # f.write(f"{self.land_type}.\n")
            # f.write(f"{self.max_water_depth}\n")
            # f.write(f"{self.cum_result}\n")
            # f.write(f"{self.output_dir}\n")
            f.write(
                f"damage cost infrastructure (dollars): {damage_cost_infrastructure}\n"
            )
            f.write(f"damage cost agricultural (dollars): {damage_cost_agricultural}\n")
            f.write(f"flooded streets (%): {round(flooded_streets_percentage, 3)}\n")
            f.write(
                f"maximum flooded area (%): {round(max_flooded_area_percentage, 3)}\n"
            )
            f.write(f"investment (dollars): {investment}\n")
            f.write(f"impact downstream (%): {round(self.cum_result, 3)}\n")
            f.write(f"groundwater infiltration (%): {round(self.infil_result, 3)}\n")
            f.write(f"cost of mulching (dollars):{mulching_investment}\n")
            f.write(f"cost of 1m berm (dollars): {berm1_investment}\n")
            f.write(f"cost of 2m berm (dollars): {berm2_investment}\n")

        return eval_result_path

    def calc_flood_area_and_cost(self):
        """
        function to estimate maximum flooded area, flooded streets, and damage cost
        """
        # TODO may need to define land type dict for flooding threshold,
        #  right now all values are hardcoded

        # pre-defined criteria
        street_cost = 100  # dollar/ m2
        house_cost = 200  # dollar/ m2
        agricultural_cost = 0.3  # dollar/ m2
        street_percentage = 7 / self.cell_size
        thresholds = {
            "streets": 0.15,
            "houses": 0.2,
            "agricultural": 0.15,
            "other": 0.3,
        }

        # identify flooded cells
        flooded_streets_cells = len(
            self.max_water_depth[
                (self.land_type == self.LAND_TYPE["streets"])
                & (self.max_water_depth >= thresholds["streets"])
            ]
        )
        flooded_houses_cells = len(
            self.max_water_depth[
                (self.land_type == self.LAND_TYPE["houses"])
                & (self.max_water_depth >= thresholds["houses"])
            ]
        )
        flooded_agricultural_cells = len(
            self.max_water_depth[
                (self.land_type == self.LAND_TYPE["agricultural"])
                & (self.max_water_depth >= thresholds["agricultural"])
            ]
        )

        flooded_other_cells = len(
            self.max_water_depth[
                (self.land_type != self.LAND_TYPE["streets"])
                & (self.land_type != self.LAND_TYPE["houses"])
                & (self.land_type != self.LAND_TYPE["agricultural"])
                & (self.max_water_depth >= thresholds["other"])
            ]
        )

        # identify flooded area and percentage
        flooded_streets_area = (
            flooded_streets_cells * self.cell_area * street_percentage
        )
        max_flooded_area = (
            flooded_agricultural_cells + flooded_houses_cells + flooded_other_cells
        ) * self.cell_area + flooded_streets_area

        total_streets_cells = len(
            self.land_type[self.land_type == self.LAND_TYPE["streets"]]
        )
        total_watershed_cells = len(self.land_type[self.land_type != self.no_data])
        flooded_streets_percentage = (
            100 * flooded_streets_cells / total_streets_cells
            if total_streets_cells > 0
            else 0
        )
        max_flooded_area_percentage = (
            100 * max_flooded_area / (total_watershed_cells * self.cell_area)
            if total_watershed_cells > 0
            else 0
        )

        # Testing!
        # print("total_streets_cells", total_streets_cells)
        # print("flooded_streets_cells", flooded_streets_cells)
        # print("flooded_streets_percentage", flooded_streets_percentage)
        # print("total_watershed_cells", total_watershed_cells)
        # print("max_flooded_area", max_flooded_area)
        # print("max_flooded_area_percentage", max_flooded_area_percentage)
        # print("flooded_cells", flooded_streets_cells, flooded_houses_cells,
        # flooded_agricultural_cells, flooded_other_cells)

        # calculate damage cost of street and house
        damage_cost_streets = flooded_streets_area * street_cost
        damage_cost_houses = flooded_houses_cells * self.cell_area * house_cost
        damage_cost_infrastructure = damage_cost_houses + damage_cost_streets
        damage_cost_agricultural = (
            flooded_agricultural_cells * self.cell_area * agricultural_cost
        )

        # !! Testing
        # print(flooded_streets_cells,flooded_houses_cells, flooded_other_cells)

        return (
            max_flooded_area_percentage,
            flooded_streets_percentage,
            damage_cost_infrastructure,
            damage_cost_agricultural,
        )

    def calc_investment(self):
        """Estimate the cost of interventions: mulching, berm"""

        # pre-defined criteria for berm
        berm_width = 2  # meter
        berm_height_1 = 1  # meter
        berm_height_2 = 2  # meter
        berm_install_cost = 30  # dollar/m3
        berm_maintain_cost = 3  # dollar/m3/year

        # pre-defined criteria for mulching
        mulching_install_cost = 0.5  # dollar/m2
        mulching_maintain_cost = mulching_install_cost * 0.05 # dollar/m2/year

        # pre-define inflation rate for 20 years
        inflation_rates = [0.033, 0.025, 0.021] +  [0.02] * 16

        # pre-defined discount rate
        discount_rate = 0.07

        # cost of berm1
        berm1_cells = len(
            self.max_water_depth[self.land_type == self.LAND_TYPE["berm_low"]]
        )
        berm1_volume = berm_width * berm_height_1 * self.cell_size * berm1_cells
        berm1_npv = calculate_npv(
            berm_install_cost, berm_maintain_cost, inflation_rates, discount_rate)
        berm1_investment = berm1_volume * berm1_npv["total_cost"]

        # cost of berm2
        berm2_cells = len(
            self.max_water_depth[self.land_type == self.LAND_TYPE["berm_high"]]
        )
        berm2_volume = berm_width * berm_height_2 * self.cell_size * berm2_cells
        berm2_npv = calculate_npv(
            berm_install_cost, berm_maintain_cost, inflation_rates, discount_rate)
        berm2_investment = berm2_volume * berm2_npv["total_cost"]

        # cost of mulching
        mulching_cells = len(
            self.max_water_depth[self.land_type == self.LAND_TYPE["mulch"]]
        )
        mulching_npv = calculate_npv(
            mulching_install_cost,
            mulching_maintain_cost,
            inflation_rates,
            discount_rate
        )
        mulching_investment = (
            mulching_cells
            * self.cell_area
            * mulching_npv["total_cost"]
        )

        investment = berm1_investment + berm2_investment + mulching_investment

        # !! Testing
        # print(berm_cells, mulching_cells)
        # print(berm_investment, mulching_investment)

        # TODO, only keep investment when efficiency function is implemented
        return investment, mulching_investment, berm1_investment, berm2_investment


# test = ModelEvaluation(
#     land_type_path,
#     max_water_depth_path,
#     cum_result_path,
#     infil_result_path,
#     output_folder,
# )
# test.evaluate()
