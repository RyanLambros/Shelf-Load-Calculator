from bakery import assert_equal
from drafter import *
from dataclasses import dataclass


# DATA CLASSES

@dataclass
class BeamCalculation:
    """Stores the information and results for one beam calculation."""
    material: str
    length: float
    width: float
    thickness: float
    load: float
    load_type: str
    stress: float
    safety_factor: float
    safe: bool


@dataclass
class State:
    """Stores the current measurements and saved calculations."""
    material: str
    length: str
    width: str
    thickness: str
    load: str
    load_type: str
    calculations: list

 



# MATERIAL STRENGTH

def get_material_strength(material: str)-> int:
    """Returns the approximate strength value for a material."""
    if material == "Pine":
        return 6000
    elif material == "Oak":
        return 10000
    elif material == "Maple":
        return 12000
    elif material == "Steel":
        return 36000
    else:
        return 0


assert_equal(get_material_strength("Pine"), 6000)
assert_equal(get_material_strength("Oak"), 10000)
assert_equal(get_material_strength("Maple"), 12000)
assert_equal(get_material_strength("Steel"), 36000)
assert_equal(get_material_strength("Unknown"), 0)


# STRESS CALCULATION

def calculate_stress(load:float,length:float,width:float,thickness:float,load_type:str)->float:
    """Calculates simplified beam stress based on the load type."""
    if load_type == "Point":
        factor = 1.5
    else:
        factor = 0.75

    stress = (load * length * factor) / (width * thickness)
    return stress



# SAFETY FACTOR

def calculate_safety_factor(strength: float, stress: float) -> float:
    """Calculates the safety factor by dividing strength by stress."""
    if stress <= 0:
        return 0

    return strength / stress


assert_equal(calculate_safety_factor(6000, 90), 6000 / 90)
assert_equal(calculate_safety_factor(6000, 0), 0)


# SAFETY CHECK

def is_safe(safety_factor: float) -> bool:
    """Returns True when the safety factor is at least 2."""
    return safety_factor >= 2


assert_equal(is_safe(2), True)
assert_equal(is_safe(3), True)
assert_equal(is_safe(1.5), False)


# INPUT VALIDATION

def is_positive_number(value: str) ->bool:
    """Checks whether a string contains a positive number."""
    if value == "":
        return False

    decimal_count = 0
    digit_count = 0

    for character in value:
        if character == ".":
            decimal_count += 1
        elif character.isdigit():
            digit_count += 1
        else:
            return False

    if decimal_count > 1 or digit_count == 0:
        return False

    return float(value) > 0


assert_equal(is_positive_number("10"), True)
assert_equal(is_positive_number("10.5"), True)
assert_equal(is_positive_number("0"), False)
assert_equal(is_positive_number("-5"), False)
assert_equal(is_positive_number("abc"), False)
assert_equal(is_positive_number(""), False)


# HOME PAGE

@route
def index(state: State)-> Page:
    """Displays the main menu of the Shelf Load Calculator."""
    return Page(state, [
        Header("Shelf Load Calculator"),
        Text("Calculate whether a shelf can safely support a load."),
        Button("Start Calculation", "input_form"),
        Button("Saved Calculations", "saved_calculations"),
        Button("Materials", "materials"),
        Button("About", "about")
    ])


# MEASUREMENTS PAGE

@route
def input_form(state: State) -> Page:
    """Allows the user to enter shelf measurements."""
    return Page(state, [
        Header("Shelf Measurements"),
        Text("Enter the measurements of your shelf."),
        "Length:",
        TextBox("length", state.length),
        "Width:",
        TextBox("width", state.width),
        "Thickness:",
        TextBox("thickness", state.thickness),
        Button("Continue", "save_dimensions"),
        Button("Home", "index")
    ])


@route
def save_dimensions(state: State, length: str, width: str,
                    thickness: str) -> Page:
    """Validates and saves the shelf measurements."""
    if not is_positive_number(length):
        return Page(state, [
            Header("Invalid Length"),
            Text("Please enter a positive number."),
            Button("Go Back", "input_form")
        ])

    if not is_positive_number(width):
        return Page(state, [
            Header("Invalid Width"),
            Text("Please enter a positive number."),
            Button("Go Back", "input_form")
        ])

    if not is_positive_number(thickness):
        return Page(state, [
            Header("Invalid Thickness"),
            Text("Please enter a positive number."),
            Button("Go Back", "input_form")
        ])

    state.length = length
    state.width = width
    state.thickness = thickness

    return Page(state, [
        Header("Measurements Saved"),
        Text("Your shelf measurements have been saved."),
        Button("Continue", "load_form")
    ])


# LOAD PAGE

@route
def load_form(state: State) -> Page:
    """Allows the user to select a material and enter a load."""
    return Page(state, [
        Header("Load Information"),
        "Material:",
        SelectBox("material", [
            "Pine", "Oak", "Maple", "Steel"
        ]),
        "Load Type:",
        SelectBox("load_type", [
            "Point", "Distributed"
        ]),
        "Load in pounds:",
        TextBox("load", state.load),
        Button("Calculate", "calculate"),
        Button("Back", "input_form")
    ])


# CALCULATION PAGE

@route
def calculate(state: State, material: str,
              load_type: str, load: str) -> Page:
    """Calculates stress and safety factor for the shelf."""
    if not is_positive_number(load):
        return Page(state, [
            Header("Invalid Load"),
            Text("Please enter a positive load."),
            Button("Go Back", "load_form")
        ])

    strength = get_material_strength(material)

    stress = calculate_stress(
        float(load),
        float(state.length),
        float(state.width),
        float(state.thickness),
        load_type
    )

    safety_factor = calculate_safety_factor(strength, stress)
    safe = is_safe(safety_factor)

    calculation = BeamCalculation(
        material,
        float(state.length),
        float(state.width),
        float(state.thickness),
        float(load),
        load_type,
        stress,
        safety_factor,
        safe
    )

    state.calculations.append(calculation)

    return Page(state, [
        Header("Calculation Complete"),
        Text("Your shelf calculation is complete."),
        Button("View Results", "results"),
        Button("Home", "index")
    ])


# RESULTS PAGE

@route
def results(state: State) -> Page:
    """Displays the most recent shelf calculation."""
    if len(state.calculations) == 0:
        return Page(state, [
            Header("No Results"),
            Text("Complete a calculation first."),
            Button("Home", "index")
        ])

    calculation = state.calculations[-1]

    if calculation.safe:
        safety_message = "Your shelf passed the safety check."
    else:
        safety_message = "Your shelf did not pass the safety check."

    return Page(state, [
        Header("Calculation Results"),
        Text("Material: " + calculation.material),
        Text("Stress: " + str(calculation.stress)),
        Text("Safety Factor: " + str(calculation.safety_factor)),
        Text(safety_message),
        Button("View Details", "details"),
        Button("Calculate Again", "input_form"),
        Button("Home", "index")
    ])


# DETAILS PAGE

@route
def details(state: State) -> Page:
    """Displays all measurements and load details."""
    if len(state.calculations) == 0:
        return Page(state, [
            Header("No Details Available"),
            Button("Home", "index")
        ])

    calculation = state.calculations[-1]

    return Page(state, [
        Header("Calculation Details"),
        Text("Material: " + calculation.material),
        Text("Length: " + str(calculation.length)),
        Text("Width: " + str(calculation.width)),
        Text("Thickness: " + str(calculation.thickness)),
        Text("Load: " + str(calculation.load)),
        Text("Load Type: " + calculation.load_type),
        Text("Stress: " + str(calculation.stress)),
        Text("Safety Factor: " + str(calculation.safety_factor)),
        Button("Back to Results", "results"),
        Button("Home", "index")
    ])


# SAVED CALCULATIONS PAGE

@route
def saved_calculations(state: State) -> Page:
    """Displays the user's saved calculations."""
    page_content: list[PageContent] = [
        Header("Saved Calculations")
    ]

    if len(state.calculations) == 0:
        page_content.append(Text("No saved calculations."))
    else:
        for calculation in state.calculations:
            page_content.append(
                Text(
                    calculation.material
                    + " - Load: "
                    + str(calculation.load)
                    + " lbs - Safety Factor: "
                    + str(calculation.safety_factor)
                )
            )

    page_content.append(Button("Clear History", "clear_history"))
    page_content.append(Button("Home", "index"))

    return Page(state, page_content)


# CLEAR HISTORY PAGE

@route
def clear_history(state: State) -> Page:
    """Removes all saved calculations."""
    state.calculations = []

    return Page(state, [
        Header("History Cleared"),
        Text("All saved calculations have been removed."),
        Button("Home", "index")
    ])


# MATERIALS PAGE

@route
def materials(state: State) -> Page:
    """Explains the available shelf materials and their strengths."""
    return Page(state, [
        Header("Available Materials"),
        Text("Pine: 6000"),
        Text("Oak: 10000"),
        Text("Maple: 12000"),
        Text("Steel: 36000"),
        Button("Home", "index")
    ])


# ABOUT PAGE

@route
def about(state: State) -> Page:
    """Explains the purpose of the Shelf Load Calculator."""
    return Page(state, [
        Header("About"),
        Text(
            "The Shelf Load Calculator estimates shelf stress "
            "and checks whether the shelf meets a safety factor "
            "of at least 2."
        ),
        Button("Home", "index")
    ])


# START APPLICATION

start_server(State(
    material="Pine",
    length="",
    width="",
    thickness="",
    load="",
    load_type="Point",
    calculations=[]
))
