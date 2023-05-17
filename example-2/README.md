# More code smells

This repository contains the code for the More code smells video on the ArjanCodes channel. Watch the video [here](https://youtu.be/zmWf_cHyo8s).

## Code smells examples

### 1. Too many parameters

In this example, the method *.add_vehicle_model_info()* from `VehicleRegistry` requires too many parameters. In fact, 
the same parameters as those from `VehicleModelInfo`. This is related to **Feature envy**, ie. when a method requires 
the implementation details of another object. This suggests that they should be merged, or implemented differently.

Also, note that `VehicleModelInfo` does not have default values. Having default values helps reduce the number of 
arguments needed to instantiate the class.


```
@dataclass
class VehicleModelInfo:
    """Class that contains basic information about a vehicle model."""

    brand: str
    model: str
    catalogue_price: int
    fuel_type: FuelType
    production_year: int


class VehicleRegistry:
    """Class representing a basic vehicle registration system."""

    def __init__(self) -> None:
        self.vehicle_models: list[VehicleModelInfo] = []
        self.online = True

    def add_vehicle_model_info(
        self,
        brand: str,
        model: str,
        catalogue_price: int,
        fuel_type: FuelType,
        year: int,
    ) -> None:
        """Helper method for adding a VehicleModelInfo object to a list."""
        self.vehicle_models.append(
            VehicleModelInfo(brand, model, catalogue_price, fuel_type, year)
        )

```

Therefore, we can do two things:

1. Pass default values to `VehicleModelInfo`.
2. Change *.add_vehicle_model_info()* to accept an instance of `VehicleModelInfo`


```
from datetime import datetime

@dataclass
class VehicleModelInfo:
    """Class that contains basic information about a vehicle model."""

    brand: str
    model: str
    catalogue_price: int
    fuel_type: FuelType = FuelType.ELECTRIC
    production_year: int = datetime.now().year


class VehicleRegistry:
    """Class representing a basic vehicle registration system."""

    def __init__(self) -> None:
        self.vehicle_models: list[VehicleModelInfo] = []
        self.online = True

    def add_vehicle_model_info(self, model_info: VehicleModelInfo) -> None:
        """Helper method for adding a VehicleModelInfo object to a list."""
        self.vehicle_models.append(model_info)

```

### 2. Too deep nesting

Here. *.register_vehicle()* is doing too many things. It is responsible for :

- checking vehicle info
- generating id values
- returning the vehicle

The code implementation is not clean because of the use of nested if-statements inside 
of a for-loop. This makes the code hard to read.

```
class VehicleRegistry:
    """Class representing a basic vehicle registration system."""

    def __init__(self) -> None:
        self.vehicle_models: list[VehicleModelInfo] = []
        self.online = True

    def register_vehicle(self, brand: str, model: str) -> Vehicle:
        """Create a new vehicle and generate an id and a license plate."""
        for vehicle_info in self.vehicle_models:
            if vehicle_info.brand == brand:
                if vehicle_info.model == model:
                    vehicle_id = self.generate_vehicle_id(12)
                    license_plate = self.generate_vehicle_license(vehicle_id)
                    return Vehicle(vehicle_id, license_plate, vehicle_info)
        raise VehicleInfoMissingError(brand, model)
```

Here, we can fix the code by separating the responsibilities of (1) finding vehicle info, 
and (2) creating the vehicle. 

```
from typing import Optional

    def find_model_info(self, brand: str, model: str) -> Optional[VehicleModelInfo]:
        """Create a new vehicle and generate an id and a license plate."""
        for vehicle_info in self.vehicle_models:
            if vehicle_info.brand == brand:
                if vehicle_info.model == model:
                    return vehicle_info
        return None

    def register_vehicle(self, brand: str, model: str) -> Vehicle:
        """Create a new vehicle and generate an id and a license plate."""
        vehicle_model = self.find_model_info(brand, model)
        if vehicle_model:
            vehicle_id = self.generate_vehicle_id(12)
            license_plate = self.generate_vehicle_license(vehicle_id)
            return Vehicle(vehicle_id, license_plate, vehicle_model)
        raise VehicleInfoMissingError(brand, model)
```

Note that the nested code in *.find_model_info()* that can be improved by 
using a logical operation. 

```
    def find_model_info(self, brand: str, model: str) -> Optional[VehicleModelInfo]:
        """Create a new vehicle and generate an id and a license plate."""
        for vehicle_info in self.vehicle_models:
            if vehicle_info.brand == brand and vehicle_info.model == model:
                return vehicle_info
        return None
```

#### Special cases can be handled at the beginning of a method. 

If you look at the code of *.register_vehicle()*, you notice that the method is mainly supposed to provide 
a 'vehicle_id', a 'license_plate', and return a 'Vehicle' instance. But there is a lot
of code surrounding the main part. As a good practice, the main code should not be nested
at all. The way to fix this here is by turning around the **if** condition. Instead of checking 
whether a vehicle model is valid, check whether the vehicle info is not valid.

```
    def register_vehicle(self, brand: str, model: str) -> Vehicle:
        """Create a new vehicle and generate an id and a license plate."""
        vehicle_model = self.find_model_info(brand, model)
        if not vehicle_model:
            raise VehicleInfoMissingError(brand, model)

        vehicle_id = self.generate_vehicle_id(12)
        license_plate = self.generate_vehicle_license(vehicle_id)
        return Vehicle(vehicle_id, license_plate, vehicle_model)
```

Similarly, the main code of *.find_model_info()* can be brought one level down by switching the 
logical operation to its inverse:

```
    def find_model_info(self, brand: str, model: str) -> Optional[VehicleModelInfo]:
        """Create a new vehicle and generate an id and a license plate."""
        for vehicle_info in self.vehicle_models:
            if vehicle_info.brand != brand or vehicle_info.model != model:
                continue
            return vehicle_info
        return None
```

Finally, you can use the walrus operator in *.register_vehicle()*. The walrus operator asigns a value and 
returns the result of the assignment. So you can combine assignment and checking in a single statement. 

```
    def register_vehicle(self, brand: str, model: str) -> Vehicle:
        """Create a new vehicle and generate an id and a license plate."""
        if not (vehicle_model := self.find_model_info(brand, model)):
            raise VehicleInfoMissingError(brand, model)

        vehicle_id = self.generate_vehicle_id(12)
        license_plate = self.generate_vehicle_license(vehicle_id)
        return Vehicle(vehicle_id, license_plate, vehicle_model)
```

### 3. Not using the right data structure

Here, storing 'vehicle_info' as a list involves that each check has to be done over the whole list.
Using a dictionary would be more suitable, as we can use the 'brand' and 'model' as keys.

From:

```
class VehicleRegistry:
    """Class representing a basic vehicle registration system."""

    def __init__(self) -> None:
        self.vehicle_models: list[VehicleModelInfo] = []
        self.online = True

    def add_vehicle_model_info(self, model_info: VehicleModelInfo) -> None:
        """Helper method for adding a VehicleModelInfo object to a list."""
        self.vehicle_models.append(model_info)

    def find_model_info(self, brand: str, model: str) -> Optional[VehicleModelInfo]:
        """Finds vehicle model info for a brand and model. If no info can be found, None is returned."""
        for vehicle_info in self.vehicle_models:
            if vehicle_info.brand != brand or vehicle_info.model != model:
                continue
            return vehicle_info
        return None
```

To:

```
from typing import Tuple

class VehicleRegistry:
    """Class representing a basic vehicle registration system."""

    def __init__(self) -> None:
        self.vehicle_models: dict[Tuple(str, str), VehicleModelInfo] = {}
        self.online = True

    def add_vehicle_model_info(self, model_info: VehicleModelInfo) -> None:
        """Helper method for adding a VehicleModelInfo object to a dict."""
        self.vehicle_models[(model_info.brand, model_info.model)] = model_info

    def find_model_info(self, brand: str, model: str) -> Optional[VehicleModelInfo]:
        """Finds vehicle model info for a brand and model. If no info can be found, None is returned."""
        return self.vehicle_models.get((brand, model))
```

### 4. Nested conditional expressions

Nested conditional expressions are hard to read. It is not clear under which conditions what should happen. 
It is better to split them. 

From:

```
# In 'VehicleRegistry':

    def online_status(self) -> RegistryStatus:
        """Report whether the registry system is online."""
        return (
            RegistryStatus.OFFLINE
            if not self.online
            else RegistryStatus.CONNECTION_ERROR
            if len(self.vehicle_models) == 0
            else RegistryStatus.ONLINE
        )
```

To:

```
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
```

### 5. Using wildcard imports

Using wildcard import is a bad idea, as it polutes your namespace in the module, which may 
become confusing very quickly. 

```
from random import *
from string import *
```

Instead, import the libraries, and call the appropriate methods where appropriate

```
import random
import string

random.choices()
string.digits
string.ascii_uppercase
```

### 6. Asymmetrical code

The following classes have a method to print as a string. Note however that the names of these methods 
are not consistent: *.get_info_str()* and *.to_string()*. In this case, it is better to use the 
built-in method of `__str__()`

From:

```
@dataclass
class VehicleModelInfo:
    """Class that contains basic information about a vehicle model."""

    brand: str
    model: str
    catalogue_price: int
    fuel_type: FuelType = FuelType.ELECTRIC
    production_year: int = datetime.now().year

    def get_info_str(self) -> str:
        """String representation of this instance."""
        return f"brand: {self.brand} - type: {self.model} - tax: {self.tax}"
```
```
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
```

To: 

```
@dataclass
class VehicleModelInfo:
    """Class that contains basic information about a vehicle model."""

    brand: str
    model: str
    catalogue_price: int
    fuel_type: FuelType = FuelType.ELECTRIC
    production_year: int = datetime.now().year

    def __str__(self) -> str:
        return f"brand: {self.brand} - type: {self.model} - tax: {self.tax}"
```
```
@dataclass
class Vehicle:
    """Class representing a vehicle (electric or fossil fuel)."""

    vehicle_id: str
    license_plate: str
    info: VehicleModelInfo

    def __str__(self) -> str:
        return f"Id: {self.vehicle_id}. License plate: {self.license_plate}. Info: {self.info}."
```

#### Using `__str__` or `__repr__`?

Use `__str__` to produce a human readable string, and `__repr__` to produce a string that represents
the object. In other words, *str* is intended for the users, and *repr* for the developers.


### 7. Using `self` when it's not needed

If you have a method that does not change an instance value, it's better to use `@staticmethod` and 
remove *self* from the method. For example:

From:

```
class VehicleRegistry:
    """Class representing a basic vehicle registration system."""

    def generate_vehicle_id(self, length: int) -> str:
        """Helper method for generating a random vehicle id."""
        return "".join(random.choices(string.ascii_uppercase, k=length))

    def generate_vehicle_license(self, _id: str) -> str:
        """Helper method for generating a vehicle license number."""
        return f"{_id[:2]}-{''.join(random.choices(string.digits, k=2))}-{''.join(random.choices(string.ascii_uppercase, k=2))}"
```

To:

```
class VehicleRegistry:
    """Class representing a basic vehicle registration system."""

    @staticmethod
    def generate_vehicle_id(length: int) -> str:
        """Helper method for generating a random vehicle id."""
        return "".join(random.choices(string.ascii_uppercase, k=length))

    @staticmethod
    def generate_vehicle_license(_id: str) -> str:
        """Helper method for generating a vehicle license number."""
        return f"{_id[:2]}-{''.join(random.choices(string.digits, k=2))}-{''.join(random.choices(string.ascii_uppercase, k=2))}"
```

Note that the method *.generate_vehicle_license()* can be refactored as so, to increase readability:

```
    @staticmethod
    def generate_vehicle_license(_id: str) -> str:
        """Helper method for generating a vehicle license number."""
        digit_part = "".join(random.choices(string.digits, k=2))
        letter_part = "".join(random.choices(string.ascii_uppercase, k=2))
        return f"{_id[:2]}-{digit_part}-{letter_part}"
```

#### *Static* methods vs *Class* methods

**Class methods** are methods that have access to the class instance, so it can change class variables, attributes.
**Static methods** can't do that. They simply belong to a class.

In this example, you could argue that generating vehicle plates and ids shouldn't even be part of the Registry, 
but they should belong to a separate module that provides helper functions. 


### 8. Not using a *main()* function

If you don't create a *main()* function, and instead place your running code under an if-statement, then
every variable that you create is going to be available at the module level, and that might lead to 
all kind of name clashes, etc. The solution is to always use a separate *main()* function.

From:

```
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
    print(vehicle)
```

To:

```
def main():

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
    print(vehicle)


if __name__ == "__main__":
    main()
```



