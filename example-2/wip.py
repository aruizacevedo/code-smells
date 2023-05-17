"""
Basic example of a Vehicle registration system.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from random import *
from string import *
from typing import Optional, Tuple


class FuelType(Enum):
    """Types of fuel used in a vehicle."""

    ELECTRIC = auto()
    PETROL = auto()


class RegistryStatus(Enum):
    """Possible statuses for the vehicle registry system."""

    ONLINE = auto()
    CONNECTION_ERROR = auto()
    OFFLINE = auto()


taxes = {FuelType.ELECTRIC: 0.02, FuelType.PETROL: 0.05}


@dataclass
class VehicleInfoMissingError(Exception):
    """Custom error that is raised when vehicle information is missing for a particular brand."""

    brand: str
    model: str
    message: str = "Vehicle information is missing."


@dataclass
class VehicleModelInfo:
    """Class that contains basic information about a vehicle model."""

    brand: str
    model: str
    catalogue_price: int
    fuel_type: FuelType = FuelType.ELECTRIC
    production_year: int = datetime.now().year

    @property
    def tax(self) -> float:
        """Tax to be paid when registering a vehicle of this type."""
        tax_percentage = taxes[self.fuel_type]
        return tax_percentage * self.catalogue_price

    def get_info_str(self) -> str:
        """String representation of this instance."""
        return f"brand: {self.brand} - type: {self.model} - tax: {self.tax}"


@dataclass
class Vehicle:
    """Class representing a vehicle (electric or fossil fuel)."""

    vehicle_id: str
    license_plate: str
    info: VehicleModelInfo

    def to_string(self) -> str:
        """String representation of this instance."""
        info_str = self.info.get_info_str()
        return f"Id: {self.vehicle_id}. License plate: {self.license_plate}. Info: {info_str}."


class VehicleRegistry:
    """Class representing a basic vehicle registration system."""

    def __init__(self) -> None:
        self.vehicle_models: dict[Tuple[str, str], VehicleModelInfo] = {}
        self.online = True

    def add_vehicle_model_info(self, model_info: VehicleModelInfo) -> None:
        """Helper method for adding a VehicleModelInfo object to a dict."""
        self.vehicle_models[(model_info.brand, model_info.model)] = model_info

    def generate_vehicle_id(self, length: int) -> str:
        """Helper method for generating a random vehicle id."""
        return "".join(choices(ascii_uppercase, k=length))

    def generate_vehicle_license(self, _id: str) -> str:
        """Helper method for generating a vehicle license number."""
        return f"{_id[:2]}-{''.join(choices(digits, k=2))}-{''.join(choices(ascii_uppercase, k=2))}"

    def find_model_info(self, brand: str, model: str) -> Optional[VehicleModelInfo]:
        """Finds vehicle model info for a brand and model. If no info can be found, None is returned."""
        return self.vehicle_models.get((brand, model))

    def register_vehicle(self, brand: str, model: str) -> Vehicle:
        """Create a new vehicle and generate an id and a license plate."""
        if not (vehicle_model := self.find_model_info(brand, model)):
            raise VehicleInfoMissingError(brand, model)

        vehicle_id = self.generate_vehicle_id(12)
        license_plate = self.generate_vehicle_license(vehicle_id)
        return Vehicle(vehicle_id, license_plate, vehicle_model)

    def online_status(self) -> RegistryStatus:
        """Report whether the registry system is online."""
        if not self.online:
            return RegistryStatus.OFFLINE
        else:
            return (
                RegistryStatus.CONNECTION_ERROR
                if len(self.vehicle_models) == 0
                else RegistryStatus.ONLINE
            )


if __name__ == "__main__":
    # create a registry instance
    registry = VehicleRegistry()

    # add a couple of different vehicle models
    registry.add_vehicle_model_info(VehicleModelInfo("Tesla", "Model 3", 50000))
    registry.add_vehicle_model_info(VehicleModelInfo("Volkswagen", "ID3", 35000))
    registry.add_vehicle_model_info(
        VehicleModelInfo("BMW", "520e", 60000, FuelType.PETROL)
    )
    registry.add_vehicle_model_info(VehicleModelInfo("Tesla", "Model Y", 55000))

    # verify that the registry is online
    print(f"Registry status: {registry.online_status()}")

    # register a new vehicle
    vehicle = registry.register_vehicle("Volkswagen", "ID3")

    # print out the vehicle information
    print(vehicle.to_string())
