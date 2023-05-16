# 7 Python code smells

This repository contains the code for the Python code smells video on the ArjanCodes channel (watch the video [here](https://youtu.be/LrtnLEkOwFE)).

The example is about employees at a company. In `before.py`, you find the original code (containing 7 code smells + a bonus smell). The `after.py` file contains the same code, but a lot less smelly.

## Using strings instead of `Enum` for defined categories

```
from enum import Enum, auto   # <-- Import these

class Role(Enum):             # <-- Define a class with the allowed values
    """Employee roles."""

    PRESIDENT = auto()
    VICEPRESIDENT = auto()
    MANAGER = auto()
    LEAD = auto()
    WORKER = auto()
    INTERN = auto()

@dataclass
class Employee:
    """Basic representation of an employee at the company."""

    name: str
    role: Role               # <-- Replace 'str' with Enum class


class Company:
    """Represents a company with employees."""

    def __init__(self) -> None:
        self.employees: List[Employee] = []

    def add_employee(self, employee: Employee) -> None:
        """Add an employee to the list of employees."""
        self.employees.append(employee)

```

```
def main() -> None:
    """Main function."""

    company = Company()
    company.add_employee(
        SalariedEmployee(
            name="Louis", 
            role=Role.MANAGER   # <-- Use instead of 'str'
        )
    )
```

### Code duplication

```
# Within the scope of 'class Company()`

    def find_managers(self) -> List[Employee]:
        """Find all manager employees."""
        managers = []
        for employee in self.employees:
            if employee.role == Role.MANAGER:
                managers.append(employee)
        return managers

    def find_vice_presidents(self) -> List[Employee]:
        """Find all vice-president employees."""
        vice_presidents = []
        for employee in self.employees:
            if employee.role == Role.VICEPRESIDENT:
                vice_presidents.append(employee)
        return vice_presidents

    def find_interns(self) -> List[Employee]:
        """Find all interns."""
        interns = []
        for employee in self.employees:
            if employee.role == Role.INTERN:
                interns.append(employee)
        return interns
```

Do this instead:
```
    def find_employees(self, role: Role) -> List[Employee]:
        """Find all employees with a particular role."""
        employees = []
        for employee in self.employees:
            if employee.role == role:
                employees.append(employee)
        return employees

```

