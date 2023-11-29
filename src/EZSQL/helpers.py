# // ---------------------------------------------------------------------
# // ------- [EZSQL] EZSQL Helpers
# // ---------------------------------------------------------------------

# // ---- Functions
def listClassAttributes(target: object) -> dict[str, any]:
    # define exceptions
    exceptions = ["__module__", "__dict__", "__weakref__", "__doc__"]
    typeExceptions = ["function"]
    
    # set vars for later
    attributes = {}
    
    # get all class attributes
    for varName, var in vars(target).items():
        # exceptions check
        if varName in exceptions or type(var).__name__ in typeExceptions:
            continue
        
        # save attribute
        attributes[varName] = var
            
    # return
    return attributes