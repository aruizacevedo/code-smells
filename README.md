# 7 Python code smells

This repository contains the code for the Python code smells video on the ArjanCodes channel (watch the video [here](https://youtu.be/LrtnLEkOwFE)).

The example is about employees at a company. In `before.py`, you find the original code (containing 7 code smells + a bonus smell). The `after.py` file contains the same code, but a lot less smelly.

## Code smells examples

### 1. Imprecise types: eg. Using strings instead of `Enum` for defined categories

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

### 2. Duplicate code

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

### 3. Not using available built-in functions

The following code can be refactored using list comprehensions

```
def find_employees(self, role: Role) -> List[Employee]:
    """Find all employees with a particular role."""
    employees = []
    for employee in self.employees:
        if employee.role == role:
            employees.append(employee)
    return employees
```

```
    def find_employees(self, role: Role) -> List[Employee]:
        """Find all employees with a particular role."""
        return [employee for employee in self.employees if employee.role is role]
```

### 4. Vague identifiers

```
@dataclass
class HourlyEmployee(Employee):
    """Employee that's paid based on number of worked hours."""

    hourly_rate: float = 50
    amount: int = 10         # <-- Not meaningful
```

```
@dataclass
class HourlyEmployee(Employee):
    """Employee that's paid based on number of worked hours."""

    hourly_rate_dollars: float = 50   # <-- Include units (dollars) 
    hours_worked: int = 10            # <-- Includes units (hours)
```


### 5. Using 'isinstance' to separate behavior

In the code below, 'isinstance()' introduces code dependency with the subclass of employee. 
If a new employee type is introduced, this method will have to be extended accordingly. 
There is a lot of *coupling*, which is a bad thing. 

```
# Within the scope of 'class Company()`

    def pay_employee(self, employee: Employee) -> None:
        """Pay an employee."""
        if isinstance(employee, SalariedEmployee):
            print(
                f"Paying employee {employee.name} a monthly salary of ${employee.monthly_salary}."
            )
        elif isinstance(employee, HourlyEmployee):
            print(
                f"Paying employee {employee.name} a hourly rate of \
                ${employee.hourly_rate_dollars} for {employee.hours_worked} hours."
            )
```

The solution is to include a 'pay()' method to each employee type:


```
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Employee(ABC):
    """Basic representation of an employee at the company."""

    @abstractmethod
    def pay(self) -> None:
        """Method to call when paying an employee."""
```
```
@dataclass
class HourlyEmployee(Employee):
    """Employee that's paid based on number of worked hours."""

    hourly_rate_dollars: float = 50
    hours_worked: int = 10

    def pay(self) -> None:
        print(
            f"Paying employee {self.name} a hourly rate of \
            ${self.hourly_rate_dollars} for {self.hours_worked} hours."
        )

@dataclass
class SalariedEmployee(Employee):
    """Employee that's paid based on a fixed monthly salary."""

    monthly_salary: float = 5000

    def pay(self) -> None:
        print(
            f"Paying employee {self.name} a monthly salary of ${self.monthly_salary}."
        )
```


### 6. Using boolean flags to make a method do 2 different things

A function which does two completely different things depending on the value of a boolean flag. This is bad, because
the whole idea of methods is they allow you to separate out responsibilities. It results in long functions with 
low cohesion, which is also harder to understand. 

```
FIXED_VACATION_DAYS_PAYOUT = 5  # The fixed nr of vacation days that can be paid out.

@dataclass
class Employee(ABC):
    """Basic representation of an employee at the company."""

    name: str
    role: Role
    vacation_days: int = 25

    def take_a_holiday(self, payout: bool) -> None:
        """Let the employee take a single holiday, or pay out 5 holidays."""
        if payout:
            # check that there are enough vacation days left for a payout
            if self.vacation_days < FIXED_VACATION_DAYS_PAYOUT:
                raise ValueError(
                    f"You don't have enough holidays left over for a payout.\
                        Remaining holidays: {self.vacation_days}."
                )
            try:
                self.vacation_days -= FIXED_VACATION_DAYS_PAYOUT
                print(f"Paying out a holiday. Holidays left: {self.vacation_days}")
            except Exception:
                # this should never happen
                pass
        else:
            if self.vacation_days < 1:
                raise ValueError(
                    "You don't have any holidays left. Now back to work, you!"
                )
            self.vacation_days -= 1
            print("Have fun on your holiday. Don't forget to check your emails!")

```

The fix is to split this method into two.

```
@dataclass
class Employee(ABC):
    """Basic representation of an employee at the company."""

    name: str
    role: Role
    vacation_days: int = 25

    def take_a_holiday(self) -> None:
        """Let the employee take a single holiday."""
        if self.vacation_days < 1:
            raise ValueError("You don't have any holidays left. Now back to work, you!")
        self.vacation_days -= 1
        print("Have fun on your holiday. Don't forget to check your emails!")

    def payout_a_holiday(self) -> None:
        """Let the employee get paid for unused holidays."""
        # check that there are enough vacation days left for a payout
        if self.vacation_days < FIXED_VACATION_DAYS_PAYOUT:
            raise ValueError(
                f"You don't have enough holidays left over for a payout.\
                    Remaining holidays: {self.vacation_days}."
            )
        try:
            self.vacation_days -= FIXED_VACATION_DAYS_PAYOUT
            print(f"Paying out a holiday. Holidays left: {self.vacation_days}")
        except Exception:
            # this should never happen
            pass
```


### 7. Catching and then ignoring exceptions

Don't catch an exception if you're not going to do anything with it. It may hide defects in your code
which may be even harder to spot. Fix by simply deleting the `try: ... except: ...` snippet.

From:

```
@dataclass
class Employee(ABC):
    """Basic representation of an employee at the company."""

    def payout_a_holiday(self) -> None:
        """Let the employee get paid for unused holidays."""
        # check that there are enough vacation days left for a payout
        if self.vacation_days < FIXED_VACATION_DAYS_PAYOUT:
            raise ValueError(
                f"You don't have enough holidays left over for a payout.\
                    Remaining holidays: {self.vacation_days}."
            )
        try:
            self.vacation_days -= FIXED_VACATION_DAYS_PAYOUT
            print(f"Paying out a holiday. Holidays left: {self.vacation_days}")
        except Exception:
            # this should never happen
            pass

```

To:

```
@dataclass
class Employee(ABC):
    """Basic representation of an employee at the company."""

    def payout_a_holiday(self) -> None:
        """Let the employee get paid for unused holidays."""
        # check that there are enough vacation days left for a payout
        if self.vacation_days < FIXED_VACATION_DAYS_PAYOUT:
            raise ValueError(
                f"You don't have enough holidays left over for a payout.\
                    Remaining holidays: {self.vacation_days}."
            )

        self.vacation_days -= FIXED_VACATION_DAYS_PAYOUT
        print(f"Paying out a holiday. Holidays left: {self.vacation_days}")
```

#### Bonus: Not using custom exceptions

In Python, `ValueError` is used when there is an issue with the provided value. If you need 
a custom exception, it is better to define it, so the user knows what is the problem in the code. 

```
class VacationDaysShortageError(ValueError):
    """Custom error that is raised when not enough vacation days are available."""
    def __init__(self, requested_days: int, remaining_days: int, message: str) -> None:
        self.requested_days = requested_days
        self.remaining_days = remaining_days
        self.message = message
        super().__init__(message)
```






