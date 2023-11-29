# // ---------------------------------------------------------------------
# // ------- [EZSQL] Testing
# // ---------------------------------------------------------------------

# // ---- Imports
import EZSQL
import time

# // ---- Main
# // SQL Table Definitions
class food:
    id = EZSQL.column(
        type = EZSQL.dataTypes.integerType,
        default = 0,
        isPrimary = True
    )

    name = EZSQL.column(
        type = EZSQL.dataTypes.stringType,
        default = "",
        isPrimary = False
    )

    description = EZSQL.column(
        type = EZSQL.dataTypes.stringType,
        default = "",
        isPrimary = False
    )
    
    # so we can create a value at any time. id is optional because id is the primary key
    def __init__(self, id: int = None, name: str = None, description: str = None):
        if id:
            self.id = id
        
        self.name = name
        self.description = description
    
# // Create Database
# create db
database = EZSQL.database("test.db")

# create food table
foodTable = database.createTable("Food", food)

# // Modify Database
# insert food into food table
foodTable.insert(
    value = food( # since id is the primary key AND its an integer, we don't need to specify it because it will automatically increment
        name = "Chicken",
        description = "It's excellent"
    )
)

foodTable.insert(
    value = food(
        id = 2, # if a food of this id already exists in the db, then this will not be added
        name = "Rice",
        description = "h"
    )
)

# retrieve something from the db
foods: list[food] = foodTable.get(
    searchParameters = food(name = "Rice", description = "h"), # search for food with the name "Rice" and description "h"
    fetchHowMany = -1 # -1 = get all results, 1 = get a singular result (not in a list), 2+ = get x results (in a list)
)

# retrieve everything from the db
foods: list[food] = foodTable.getAll()

# foods[0]:
"""
food(
    id = 2,
    name = "Rice",
    description = "h"
)
"""

# remove every value with the name "Chicken" from the database
foodTable.remove(
    searchParameters = food(name = "Chicken")
)

# remove all values after 5 seconds
time.sleep(5)
foodTable.removeAll()

# remove table after another 5 seconds
time.sleep(5)
foodTable.removeTable()